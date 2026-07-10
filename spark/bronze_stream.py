from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType

# Schema
schema = StructType() \
    .add("event_id", StringType()) \
    .add("event_type", StringType()) \
    .add("event_time", StringType()) \
    .add("stock_symbol", StringType()) \
    .add("price", DoubleType()) \
    .add("volume", IntegerType())

# Spark session
spark = SparkSession.builder \
    .appName("KafkaToBronze") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "admin123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Read Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "price_ticks") \
    .option("startingOffsets", "latest") \
    .option("maxOffsetsPerTrigger", 10000) \
    .load()

# Parse JSON
parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Write to S3 (MinIO)
query = parsed_df.writeStream \
    .format("parquet") \
    .option("path", "s3a://stock-data/bronze/price_ticks") \
    .option("checkpointLocation", "s3a://stock-data/checkpoints/price_ticks") \
    .option("maxRecordsPerFile", 50000) \
    .partitionBy("stock_symbol") \
    .outputMode("append") \
    .trigger(processingTime="5 seconds") \
    .start()

query.awaitTermination()