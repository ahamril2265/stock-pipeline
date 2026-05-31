from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import clickhouse_connect
from datetime import datetime

# =====================================================
# Spark
# =====================================================

spark = SparkSession.builder \
    .appName("GoldMarketKPIsBuilder") \
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
# KPIs
# =====================================================

avg_market_price = price_df.select(
    avg("price")
).first()[0]

market_vwap = vwap_df.select(
    avg("vwap")
).first()[0]

avg_market_latency = lat_df.select(
    avg("avg_latency_ms")
).first()[0]

total_market_volume = vwap_df.select(
    sum("total_volume")
).first()[0]

buy_sell = vol_df.select(
    sum("buy_volume").alias("buy"),
    sum("sell_volume").alias("sell")
).first()

active_symbols = price_df.select(
    countDistinct("stock_symbol")
).first()[0]

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
    "TRUNCATE TABLE gold_market_kpis"
)

client.insert(
    "gold_market_kpis",
    [[
        int(total_market_volume),
        int(buy_sell["buy"]),
        int(buy_sell["sell"]),
        float(avg_market_price),
        float(market_vwap),
        float(avg_market_latency),
        int(active_symbols),
        datetime.now()
    ]],
    column_names=[
        "total_market_volume",
        "total_buy_volume",
        "total_sell_volume",
        "avg_market_price",
        "market_vwap",
        "avg_market_latency",
        "active_symbols",
        "updated_at"
    ]
)

print("✅ Gold Market KPIs Loaded")