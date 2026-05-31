from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable

# =========================================================
# Spark Session
# =========================================================

spark = SparkSession.builder \
    .appName("SilverTradeProcessor") \
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
    "namespace=com.stock.trade_events.v1"
)

SILVER_EVENTS_PATH = (
    "s3a://stock-data/silver/trade_events"
)

VWAP_PATH = (
    "s3a://stock-data/silver/trade_vwap_metrics"
)

LATENCY_PATH = (
    "s3a://stock-data/silver/trade_latency_metrics"
)

VOLUME_PATH = (
    "s3a://stock-data/silver/trade_volume_metrics"
)

QUARANTINE_PATH = (
    "s3a://stock-data/silver_quarantine/invalid_trades"
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
    (col("execution_latency_ms") >= 0)
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
        f"{invalid_df.count()} invalid trades"
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
# VWAP Metrics
# =========================================================

vwap_df = dedup_df \
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
        (
            sum(col("price") * col("volume")) /
            sum(col("volume"))
        ).alias("vwap"),

        sum("volume").alias("total_volume")
    )

# =========================================================
# Buy/Sell Imbalance
# =========================================================

volume_df = dedup_df \
    .withColumn(
        "buy_volume",
        when(
            col("trade_type") == "BUY",
            col("volume")
        ).otherwise(0)
    ) \
    .withColumn(
        "sell_volume",
        when(
            col("trade_type") == "SELL",
            col("volume")
        ).otherwise(0)
    ) \
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
        sum("buy_volume").alias("buy_volume"),
        sum("sell_volume").alias("sell_volume")
    )

# =========================================================
# Latency Metrics
# =========================================================

latency_df = dedup_df \
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
        avg("execution_latency_ms")
            .alias("avg_latency_ms"),

        max("execution_latency_ms")
            .alias("max_latency_ms"),

        expr(
            "percentile_approx("
            "execution_latency_ms, 0.95)"
        ).alias("p95_latency_ms")
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
# Write VWAP Metrics
# =========================================================

vwap_df.write \
    .format("delta") \
    .mode("append") \
    .save(VWAP_PATH)

# =========================================================
# Write Volume Metrics
# =========================================================

volume_df.write \
    .format("delta") \
    .mode("append") \
    .save(VOLUME_PATH)

# =========================================================
# Write Latency Metrics
# =========================================================

latency_df.write \
    .format("delta") \
    .mode("append") \
    .save(LATENCY_PATH)

print("✅ Silver trade processing complete")