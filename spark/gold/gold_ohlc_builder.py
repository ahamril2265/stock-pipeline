from pyspark.sql import SparkSession
import clickhouse_connect
from datetime import datetime

# ==========================================
# Spark
# ==========================================

spark = SparkSession.builder \
    .appName("GoldOHLCBuilder") \
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
# Read Silver OHLC
# ==========================================

ohlc_df = spark.read.format("delta").load(
    "s3a://stock-data/silver/price_ohlc_1m"
)

rows = ohlc_df.collect()

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
    "TRUNCATE TABLE gold_ohlc"
)

data = []

for row in rows:

    data.append([
        row["window"]["start"],
        row["window"]["end"],

        row["stock_symbol"],

        float(row["open"]),
        float(row["high"]),
        float(row["low"]),
        float(row["close"]),

        int(row["total_volume"]),

        datetime.now()
    ])

client.insert(
    "gold_ohlc",
    data,
    column_names=[
        "window_start",
        "window_end",

        "stock_symbol",

        "open_price",
        "high_price",
        "low_price",
        "close_price",

        "total_volume",

        "updated_at"
    ]
)

print("✅ Gold OHLC Loaded")