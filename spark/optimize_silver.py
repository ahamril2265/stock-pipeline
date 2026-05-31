from pyspark.sql import SparkSession
from delta.tables import DeltaTable

# =========================================================
# Spark Session
# =========================================================

spark = SparkSession.builder \
    .appName("OptimizeSilverTables") \
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
# Silver Tables
# =========================================================

TABLES = [

    {
        "name": "price_events",
        "path": "s3a://stock-data/silver/price_events",
        "zorder": "stock_symbol"
    },

    {
        "name": "price_ohlc_1m",
        "path": "s3a://stock-data/silver/price_ohlc_1m",
        "zorder": "stock_symbol"
    },

    {
        "name": "price_spread_metrics",
        "path": "s3a://stock-data/silver/price_spread_metrics",
        "zorder": "stock_symbol"
    },

    {
        "name": "trade_events",
        "path": "s3a://stock-data/silver/trade_events",
        "zorder": "stock_symbol"
    },

    {
        "name": "trade_vwap_metrics",
        "path": "s3a://stock-data/silver/trade_vwap_metrics",
        "zorder": "stock_symbol"
    },

    {
        "name": "trade_latency_metrics",
        "path": "s3a://stock-data/silver/trade_latency_metrics",
        "zorder": "stock_symbol"
    },

    {
        "name": "trade_volume_metrics",
        "path": "s3a://stock-data/silver/trade_volume_metrics",
        "zorder": "stock_symbol"
    }

]

# =========================================================
# Optimization Threshold
# =========================================================

MIN_FILES_THRESHOLD = 5

# =========================================================
# Optimize Function
# =========================================================

def optimize_table(table):

    path = table["path"]

    name = table["name"]

    zorder_col = table["zorder"]

    print(f"🚀 Optimizing table: {name}")

    try:

        # ---------------------------------------------
        # Read Delta Table
        # ---------------------------------------------

        df = spark.read.format("delta").load(path)

        file_count = len(df.inputFiles())

        print(f"📦 File count: {file_count}")

        # ---------------------------------------------
        # Adaptive Threshold Check
        # ---------------------------------------------

        if file_count < MIN_FILES_THRESHOLD:

            print(
                f"⏭️ Skipping optimization "
                f"for {name}"
            )

            return

        # ---------------------------------------------
        # Compact Files
        # ---------------------------------------------

        compacted = df.coalesce(1)

        compacted.write \
            .format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .save(path)

        print(
            f"✅ Compaction complete "
            f"for {name}"
        )

        # ---------------------------------------------
        # ZORDER Optimization
        # ---------------------------------------------

        spark.sql(f"""
            OPTIMIZE delta.`{path}`
            ZORDER BY ({zorder_col})
        """)

        print(
            f"✅ ZORDER complete "
            f"for {name}"
        )

    except Exception as e:

        print(
            f"❌ Optimization failed "
            f"for {name}: {e}"
        )

# =========================================================
# Run Optimization
# =========================================================

for table in TABLES:

    optimize_table(table)

print("✅ Silver optimization complete")