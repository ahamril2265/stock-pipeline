import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# =========================================================
# Arguments
# =========================================================

parser = argparse.ArgumentParser()

parser.add_argument(
    "--date",
    required=True,
    help="Replay date YYYY-MM-DD"
)

parser.add_argument(
    "--symbol",
    required=False,
    help="Optional stock symbol"
)

args = parser.parse_args()

REPLAY_DATE = args.date
REPLAY_SYMBOL = args.symbol

# =========================================================
# Spark Session
# =========================================================

spark = SparkSession.builder \
    .appName("SilverReplayEngine") \
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

BRONZE_PRICE_PATH = (
    "s3a://stock-data/bronze/"
    "namespace=com.stock.price_ticks.v1"
)

BRONZE_TRADE_PATH = (
    "s3a://stock-data/bronze/"
    "namespace=com.stock.trade_events.v1"
)

# =========================================================
# Read Bronze
# =========================================================

price_df = spark.read.format("delta").load(
    BRONZE_PRICE_PATH
)

trade_df = spark.read.format("delta").load(
    BRONZE_TRADE_PATH
)

# =========================================================
# Filter Replay Date
# =========================================================

price_df = price_df.filter(
    to_date(col("event_time")) == REPLAY_DATE
)

trade_df = trade_df.filter(
    to_date(col("event_time")) == REPLAY_DATE
)

# =========================================================
# Optional Symbol Filter
# =========================================================

if REPLAY_SYMBOL:

    price_df = price_df.filter(
        col("stock_symbol") == REPLAY_SYMBOL
    )

    trade_df = trade_df.filter(
        col("stock_symbol") == REPLAY_SYMBOL
    )

# =========================================================
# Replay Stats
# =========================================================

price_count = price_df.count()

trade_count = trade_df.count()

print(
    f"🚀 Replaying "
    f"{price_count} price events"
)

print(
    f"🚀 Replaying "
    f"{trade_count} trade events"
)

# =========================================================
# Rebuild Silver Inputs
# =========================================================

price_replay_path = (
    "s3a://stock-data/replay/price_events"
)

trade_replay_path = (
    "s3a://stock-data/replay/trade_events"
)

price_df.write \
    .format("delta") \
    .mode("overwrite") \
    .save(price_replay_path)

trade_df.write \
    .format("delta") \
    .mode("overwrite") \
    .save(trade_replay_path)

# =========================================================
# Completion
# =========================================================

print("✅ Replay dataset prepared")