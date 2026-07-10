from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import clickhouse_connect
from datetime import datetime

# =====================================================
# Spark
# =====================================================

spark = SparkSession.builder \
    .appName("GoldSymbolSummaryBuilder") \
    .config(
        "spark.sql.extensions",
        "io.delta.sql.DeltaSparkSessionExtension"
    ) \
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    ) \
    .getOrCreate()

# =====================================================
# MinIO Config
# =====================================================

hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()

hadoop_conf.set("fs.s3a.endpoint", "http://minio:9000")
hadoop_conf.set("fs.s3a.access.key", "admin")
hadoop_conf.set("fs.s3a.secret.key", "admin123")
hadoop_conf.set("fs.s3a.path.style.access", "true")
hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")

# =====================================================
# Read Silver
# =====================================================

price_df = spark.read.format("delta").load(
    "s3a://stock-data/silver/price_events"
)

vwap_df = spark.read.format("delta").load(
    "s3a://stock-data/silver/trade_vwap_metrics"
)

lat_df = spark.read.format("delta").load(
    "s3a://stock-data/silver/trade_latency_metrics"
)

vol_df = spark.read.format("delta").load(
    "s3a://stock-data/silver/trade_volume_metrics"
)

# =====================================================
# Latest Price
# =====================================================

latest_price = price_df.groupBy("stock_symbol").agg(
    max(struct(
        col("event_timestamp"),
        col("price")
    )).alias("latest")
).select(
    "stock_symbol",
    col("latest.price").alias("latest_price")
)

# =====================================================
# Avg Spread
# =====================================================

avg_spread = price_df.groupBy(
    "stock_symbol"
).agg(
    avg("spread").alias("avg_spread")
)

# =====================================================
# Latest VWAP
# =====================================================

latest_vwap = vwap_df.groupBy(
    "stock_symbol"
).agg(
    max(struct(
        col("window.end"),
        col("vwap"),
        col("total_volume")
    )).alias("latest")
).select(
    "stock_symbol",
    col("latest.vwap").alias("vwap"),
    col("latest.total_volume").alias("daily_volume")
)

# =====================================================
# Latest Latency
# =====================================================

latest_latency = lat_df.groupBy(
    "stock_symbol"
).agg(
    max(struct(
        col("window.end"),
        col("avg_latency_ms")
    )).alias("latest")
).select(
    "stock_symbol",
    col("latest.avg_latency_ms").alias(
        "avg_latency"
    )
)

# =====================================================
# Latest Volume Metrics
# =====================================================

latest_volume = vol_df.groupBy(
    "stock_symbol"
).agg(
    max(struct(
        col("window.end"),
        col("buy_volume"),
        col("sell_volume")
    )).alias("latest")
).select(
    "stock_symbol",
    col("latest.buy_volume").alias(
        "buy_volume"
    ),
    col("latest.sell_volume").alias(
        "sell_volume"
    )
)

# =====================================================
# Build Gold Dataset
# =====================================================

gold_df = latest_price \
    .join(avg_spread, "stock_symbol") \
    .join(latest_vwap, "stock_symbol") \
    .join(latest_latency, "stock_symbol") \
    .join(latest_volume, "stock_symbol")

rows = gold_df.collect()

# =====================================================
# ClickHouse
# =====================================================

client = clickhouse_connect.get_client(
    host="clickhouse",
    port=8123,
    username="admin",
    password="admin123",
    database="stock_analytics"
)

client.command(
    "TRUNCATE TABLE gold_symbol_summary"
)

data = []

for row in rows:

    data.append([
        row["stock_symbol"],
        float(row["latest_price"]),
        int(row["daily_volume"]),
        float(row["vwap"]),
        float(row["avg_spread"]),
        float(row["avg_latency"]),
        int(row["buy_volume"]),
        int(row["sell_volume"]),
        datetime.now()
    ])

client.insert(
    "gold_symbol_summary",
    data,
    column_names=[
        "stock_symbol",
        "latest_price",
        "daily_volume",
        "vwap",
        "avg_spread",
        "avg_latency",
        "buy_volume",
        "sell_volume",
        "last_updated"
    ]
)

print("✅ Gold Symbol Summary Loaded")