from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime
import clickhouse_connect

# ==========================================
# Spark
# ==========================================

spark = SparkSession.builder \
    .appName("GoldTopSymbolsBuilder") \
    .config(
        "spark.sql.extensions",
        "io.delta.sql.DeltaSparkSessionExtension"
    ) \
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    ) \
    .getOrCreate()

# ==========================================
# MinIO
# ==========================================

hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()

hadoop_conf.set("fs.s3a.endpoint", "http://minio:9000")
hadoop_conf.set("fs.s3a.access.key", "admin")
hadoop_conf.set("fs.s3a.secret.key", "admin123")
hadoop_conf.set("fs.s3a.path.style.access", "true")
hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")

# ==========================================
# Read Silver
# ==========================================

price_df = spark.read.format("delta").load(
    "s3a://stock-data/silver/price_events"
)

vwap_df = spark.read.format("delta").load(
    "s3a://stock-data/silver/trade_vwap_metrics"
)

vol_df = spark.read.format("delta").load(
    "s3a://stock-data/silver/trade_volume_metrics"
)

# ==========================================
# Latest Price
# ==========================================

latest_price = price_df.groupBy("stock_symbol").agg(
    max(
        struct(
            col("event_timestamp"),
            col("price")
        )
    ).alias("latest")
).select(
    "stock_symbol",
    col("latest.price").alias("latest_price")
)

# ==========================================
# Latest VWAP
# ==========================================

latest_vwap = vwap_df.groupBy("stock_symbol").agg(
    max(
        struct(
            col("window.end"),
            col("vwap"),
            col("total_volume")
        )
    ).alias("latest")
).select(
    "stock_symbol",
    col("latest.vwap").alias("vwap"),
    col("latest.total_volume").alias("total_volume")
)

# ==========================================
# Latest Buy/Sell Volume
# ==========================================

latest_volume = vol_df.groupBy("stock_symbol").agg(
    max(
        struct(
            col("window.end"),
            col("buy_volume"),
            col("sell_volume")
        )
    ).alias("latest")
).select(
    "stock_symbol",
    col("latest.buy_volume").alias("buy_volume"),
    col("latest.sell_volume").alias("sell_volume")
)

# ==========================================
# Join
# ==========================================

gold_df = latest_price \
    .join(latest_vwap, "stock_symbol") \
    .join(latest_volume, "stock_symbol")

# Rank by volume

gold_df = gold_df.orderBy(
    desc("total_volume")
)

rows = gold_df.collect()

# ==========================================
# ClickHouse
# ==========================================

client = clickhouse_connect.get_client(
    host="clickhouse",
    port=8123,
    username="admin",
    password="admin123",
    database="stock_analytics"
)

client.command(
    "TRUNCATE TABLE gold_top_symbols"
)

data = []

for rank, row in enumerate(rows, start=1):

    data.append([
        row["stock_symbol"],
        float(row["latest_price"]),
        int(row["total_volume"]),
        int(row["buy_volume"]),
        int(row["sell_volume"]),
        float(row["vwap"]),
        rank,
        datetime.now()
    ])

client.insert(
    "gold_top_symbols",
    data,
    column_names=[
        "stock_symbol",
        "latest_price",
        "total_volume",
        "buy_volume",
        "sell_volume",
        "vwap",
        "volume_rank",
        "updated_at"
    ]
)

print("✅ Gold Top Symbols Loaded")