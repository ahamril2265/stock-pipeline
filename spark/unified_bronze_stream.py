import requests
import time
import json
import struct as pystruct
import io
from fastavro import schemaless_reader
from pyspark.sql.types import *
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# -----------------------------------
# Spark Session
# -----------------------------------

spark = SparkSession.builder \
    .appName("UnifiedBronzeEngine") \
    .config(
        "spark.hadoop.fs.s3a.endpoint",
        "http://minio:9000"
    ) \
    .config(
        "spark.hadoop.fs.s3a.access.key",
        "admin"
    ) \
    .config(
        "spark.hadoop.fs.s3a.secret.key",
        "admin123"
    ) \
    .config(
        "spark.hadoop.fs.s3a.path.style.access",
        "true"
    ) \
    .config(
        "spark.hadoop.fs.s3a.connection.ssl.enabled",
        "false"
    ) \
    .config(
        "spark.hadoop.fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
    ) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# -----------------------------------
# Schema Registry
# -----------------------------------

SCHEMA_REGISTRY_URL = "http://schema-registry:8081"

# -----------------------------------
# Schema Cache
# -----------------------------------

schema_cache = {}

CACHE_TTL_SECONDS = 300

# -----------------------------------
# Schema Resolver
# -----------------------------------

def fetch_schema(schema_id):

    current_time = time.time()

    # Cache hit
    if schema_id in schema_cache:

        cached = schema_cache[schema_id]

        if current_time - cached["last_refresh"] < CACHE_TTL_SECONDS:

            return cached

    # Retry with exponential backoff
    retries = 5

    backoff = 1

    for attempt in range(retries):

        try:

            response = requests.get(
                f"{SCHEMA_REGISTRY_URL}/schemas/ids/{schema_id}"
            )

            response.raise_for_status()

            schema_json = response.json()

            schema_str = schema_json["schema"]

            parsed = json.loads(schema_str)

            namespace = parsed["namespace"]

            schema_cache[schema_id] = {
                "schema": parsed,
                "namespace": namespace,
                "last_refresh": current_time
            }

            return schema_cache[schema_id]

        except Exception as e:

            print(
                f"⚠️ Schema fetch failed "
                f"schema_id={schema_id} "
                f"attempt={attempt}"
            )

            time.sleep(backoff)

            backoff *= 2

    return None

# -----------------------------------
# Extract Schema ID
# -----------------------------------

def extract_schema_id(binary_data):

    # Confluent wire format:
    # byte 0 = magic byte
    # bytes 1-4 = schema ID

    return pystruct.unpack(">I", binary_data[1:5])[0]

# -----------------------------------
# Process Microbatch
# -----------------------------------

def process_batch(batch_df, batch_id):

    rows = batch_df.collect()

    print(f"🚀 Processing batch {batch_id}")

    schema_groups = {}

    # -----------------------------------
    # Group by Schema ID
    # -----------------------------------

    for row in rows:

        try:

            binary_value = row["value"]

            schema_id = extract_schema_id(binary_value)

            if schema_id not in schema_groups:

                schema_groups[schema_id] = []

            schema_groups[schema_id].append(row)

        except Exception as e:

            print(f"❌ Schema extraction failed: {e}")

    # -----------------------------------
    # Process Groups
    # -----------------------------------

    for schema_id, grouped_rows in schema_groups.items():

        schema_info = fetch_schema(schema_id)

        if schema_info is None:

            print(
                f"❌ Failed schema lookup "
                f"schema_id={schema_id}"
            )

            continue

        schema = schema_info["schema"]

        namespace = schema_info["namespace"]

        decoded_records = []

        quarantine_records = []

        # -----------------------------------
        # Decode Records
        # -----------------------------------

        for row in grouped_rows:

            decoded = decode_avro(
                row["value"],
                schema
            )

            if decoded is None:

                quarantine_records.append({
                    "schema_id": schema_id,
                    "raw_record": str(row["value"])
                })

            else:

                decoded_records.append(decoded)

        # -----------------------------------
        # Write Bronze Delta
        # -----------------------------------

        if decoded_records:

            bronze_df = spark.createDataFrame(decoded_records)

            bronze_df = bronze_df.withColumn(
                "event_date",
                to_date(col("event_time"))
            )

            bronze_path = (
                f"s3a://stock-data/bronze/"
                f"namespace={namespace}"
            )

            bronze_df.write \
                .format("delta") \
                .mode("append") \
                .partitionBy("event_date") \
                .save(bronze_path)

            print(
                f"✅ Bronze write success "
                f"namespace={namespace} "
                f"records={len(decoded_records)}"
            )

        # -----------------------------------
        # Write Quarantine
        # -----------------------------------

        if quarantine_records:

            quarantine_df = spark.createDataFrame(
                quarantine_records
            )

            quarantine_path = (
                f"s3a://stock-data/quarantine/"
                f"{namespace}"
            )

            quarantine_df.write \
                .format("delta") \
                .mode("append") \
                .save(quarantine_path)

            print(
                f"⚠️ Quarantined "
                f"{len(quarantine_records)} records"
            )

# -----------------------------------
# Decode Avro Payload
# -----------------------------------

def decode_avro(binary_data, schema):

    try:

        # Remove Confluent wire-format header
        payload = binary_data[5:]

        bytes_reader = io.BytesIO(payload)

        decoded = schemaless_reader(
            bytes_reader,
            schema
        )

        return decoded

    except Exception as e:

        print(f"❌ Avro decode failed: {e}")

        return None
    
# -----------------------------------
# Kafka Stream
# -----------------------------------

stream_df = spark.readStream \
    .format("kafka") \
    .option(
        "kafka.bootstrap.servers",
        "kafka:29092"
    ) \
    .option(
        "subscribePattern",
        ".*events|.*ticks"
    ) \
    .option(
        "startingOffsets",
        "latest"
    ) \
    .load()

# -----------------------------------
# Start Stream
# -----------------------------------

query = stream_df.writeStream \
    .foreachBatch(process_batch) \
    .outputMode("append") \
    .start()

query.awaitTermination()