from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable

# =========================================================
# Spark Session
# =========================================================

spark = SparkSession.builder \
    .appName("SilverPriceProcessor") \
    .config(
        "spark.sql.extensions",
        "io.delta.sql.DeltaSparkSessionExtension"
    ) \
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    ) \
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

# =========================================================
# Paths
# =========================================================

BRONZE_PATH = (
    "s3a://stock-data/bronze/"
    "namespace=com.stock.price_ticks.v1"
)

SILVER_EVENTS_PATH = (
    "s3a://stock-data/silver/price_events"
)

SILVER_OHLC_1M_PATH = (
    "s3a://stock-data/silver/price_ohlc_1m"
)

SILVER_SPREAD_PATH = (
    "s3a://stock-data/silver/price_spread_metrics"
)

QUARANTINE_PATH = (
    "s3a://stock-data/silver_quarantine/invalid_prices"
)

CHECKPOINT_PATH = (
    "s3a://stock-data/checkpoints/"
    "silver_price_processor"
)

# =========================================================
# Read Bronze Delta
# =========================================================

bronze_df = spark.read.format("delta").load(BRONZE_PATH)

# =========================================================
# Validation
# =========================================================

valid_df = bronze_df.filter(
    (col("price") > 0) &
    (col("volume") > 0) &
    (col("bid_price") > 0) &
    (col("ask_price") > 0) &
    (col("spread") >= 0)
)

invalid_df = bronze_df.subtract(valid_df)

# =========================================================
# Quarantine Invalid Records
# =========================================================

if invalid_df.count() > 0:

    invalid_df.write \
        .format("delta") \
        .mode("append") \
        .save(QUARANTINE_PATH)

    print(
        f"⚠️ Quarantined "
        f"{invalid_df.count()} invalid records"
    )

# =========================================================
# Deduplication
# =========================================================

dedup_df = valid_df.dropDuplicates([
    "event_id",
    "event_time",
    "stock_symbol"
])

# =========================================================
# Event Time
# =========================================================

dedup_df = dedup_df.withColumn(
    "event_timestamp",
    to_timestamp(col("event_time"))
)

dedup_df = dedup_df.withColumn(
    "event_date",
    to_date(col("event_timestamp"))
)

# =========================================================
# 1-Minute Sliding OHLC
# =========================================================

ohlc_df = dedup_df \
    .withWatermark("event_timestamp", "1 minute") \
    .groupBy(
        window(
            col("event_timestamp"),
            "1 minute",
            "10 seconds"
        ),
        col("stock_symbol")
    ) \
    .agg(
        first("price").alias("open"),
        max("price").alias("high"),
        min("price").alias("low"),
        last("price").alias("close"),
        sum("volume").alias("total_volume")
    )

# =========================================================
# Spread Metrics
# =========================================================

spread_df = dedup_df \
    .withWatermark("event_timestamp", "1 minute") \
    .groupBy(
        window(
            col("event_timestamp"),
            "1 minute",
            "10 seconds"
        ),
        col("stock_symbol")
    ) \
    .agg(
        avg("spread").alias("avg_spread"),
        max("spread").alias("max_spread"),
        min("spread").alias("min_spread")
    )

# =========================================================
# Write Silver Event Table
# =========================================================

dedup_df.write \
    .format("delta") \
    .mode("append") \
    .partitionBy(
        "event_date",
        "stock_symbol"
    ) \
    .save(SILVER_EVENTS_PATH)

# =========================================================
# Write OHLC Aggregates
# =========================================================

ohlc_df.write \
    .format("delta") \
    .mode("append") \
    .save(SILVER_OHLC_1M_PATH)

# =========================================================
# Write Spread Metrics
# =========================================================

spread_df.write \
    .format("delta") \
    .mode("append") \
    .save(SILVER_SPREAD_PATH)

print("✅ Silver price processing complete")