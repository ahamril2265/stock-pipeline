from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

from pyspark.sql.avro.functions import from_avro

# -----------------------------------
# Spark Session
# -----------------------------------

spark = SparkSession.builder \
    .appName("TradeBronzeStream") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# -----------------------------------
# Kafka Stream
# -----------------------------------

kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "trade_events") \
    .option("startingOffsets", "latest") \
    .option("maxOffsetsPerTrigger", 5000) \
    .load()

# -----------------------------------
# Avro Schema
# -----------------------------------

avro_schema = open("/opt/spark/work-dir/schemas/trade_event.avsc").read()

# -----------------------------------
# Deserialize Avro
# -----------------------------------

clean_df = kafka_df.selectExpr(
    "substring(value, 6) as avro_value"
)

# Deserialize pure Avro payload

parsed_df = clean_df.select(
    from_avro(
        col("avro_value"),
        avro_schema,
        {"mode": "PERMISSIVE"}
    ).alias("data")
).select("data.*")

# -----------------------------------
# Add Partition Columns
# -----------------------------------

final_df = parsed_df \
    .withColumn(
        "event_date",
        to_date(col("event_time"))
    )

# -----------------------------------
# Bronze Write
# -----------------------------------

query = final_df.writeStream \
    .format("parquet") \
    .option(
        "path",
        "s3a://stock-data/bronze/event_type=trade_events"
    ) \
    .option(
        "checkpointLocation",
        "s3a://stock-data/checkpoints/trade_events"
    ) \
    .partitionBy(
        "event_date",
        "stock_symbol"
    ) \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()