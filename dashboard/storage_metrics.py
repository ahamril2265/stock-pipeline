import socket

import clickhouse_connect
from minio import Minio
import psycopg2


# ==========================================================
# Configuration
# ==========================================================

CLICKHOUSE_HOST = "clickhouse"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "admin"
CLICKHOUSE_PASSWORD = "admin123"
CLICKHOUSE_DATABASE = "stock_analytics"

MINIO_HOST = "minio:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "admin123"

POSTGRES_HOST = "postgres"
POSTGRES_PORT = 5432
POSTGRES_DB = "airflow"
POSTGRES_USER = "airflow"
POSTGRES_PASSWORD = "airflow"


# ==========================================================
# Port Check
# ==========================================================

def port_open(host, port):

    try:

        sock = socket.create_connection(

            (host, port),

            timeout=2

        )

        sock.close()

        return True

    except Exception:

        return False

# ==========================================================
# ClickHouse Scalar Helper
# ==========================================================

def ch_scalar(client, query, parameters=None):

    result = client.query(
        query,
        parameters=parameters
    )

    if not result.result_rows:
        return 0

    value = result.result_rows[0][0]

    if value is None:
        return 0

    return value

# ==========================================================
# ClickHouse
# ==========================================================

def clickhouse_metrics():

    try:

        client = clickhouse_connect.get_client(

            host=CLICKHOUSE_HOST,

            port=CLICKHOUSE_PORT,

            username=CLICKHOUSE_USER,

            password=CLICKHOUSE_PASSWORD,

            database=CLICKHOUSE_DATABASE

        )

        tables = ch_scalar(

            client,

            """
            SELECT count()

            FROM system.tables

            WHERE database=%(db)s
            """,

            {"db": CLICKHOUSE_DATABASE}

        )

        rows = ch_scalar(

            client,

            """
            SELECT sum(rows)

            FROM system.parts

            WHERE active

            AND database=%(db)s
            """,

            {"db": CLICKHOUSE_DATABASE}

        )

        database_size = ch_scalar(

            client,

            """
            SELECT sum(bytes_on_disk)

            FROM system.parts

            WHERE active

            AND database=%(db)s
            """,

            {"db": CLICKHOUSE_DATABASE}

        )

        active_queries = ch_scalar(

            client,

            """
            SELECT count()

            FROM system.processes
            """

        )

        parts = ch_scalar(

            client,

            """
            SELECT count()

            FROM system.parts

            WHERE active

            AND database=%(db)s
            """,

            {"db": CLICKHOUSE_DATABASE}

        )

        return {

            "healthy": True,

            "tables": int(tables),

            "rows": int(rows),

            "database_size": int(database_size),

            "active_queries": int(active_queries),

            "parts": int(parts)

        }

    except Exception as e:

        print("ClickHouse Error:", e)

        return {

            "healthy": False,

            "tables": 0,

            "rows": 0,

            "database_size": 0,

            "active_queries": 0,

            "parts": 0

        }
    
# ==========================================================
# MinIO
# ==========================================================


def minio_metrics():

    try:

        client = Minio(

            MINIO_HOST,

            access_key=MINIO_ACCESS_KEY,

            secret_key=MINIO_SECRET_KEY,

            secure=False

        )

        buckets = client.list_buckets()

        total_objects = 0

        total_storage = 0

        largest_bucket = "-"

        largest_bucket_size = 0

        usage = {}

        for bucket in buckets:

            bucket_objects = 0

            bucket_size = 0

            for obj in client.list_objects(

                bucket.name,

                recursive=True

            ):

                bucket_objects += 1

                bucket_size += obj.size

            usage[bucket.name] = {

                "objects": bucket_objects,

                "size": bucket_size

            }

            total_objects += bucket_objects

            total_storage += bucket_size

            if bucket_size > largest_bucket_size:

                largest_bucket_size = bucket_size

                largest_bucket = bucket.name

        return {

            "healthy": True,

            "buckets": len(buckets),

            "objects": total_objects,

            "storage_used": total_storage,

            "largest_bucket": largest_bucket,

            "usage": usage

        }

    except Exception:

        return {

            "healthy": False,

            "buckets": 0,

            "objects": 0,

            "storage_used": 0,

            "largest_bucket": "-",

            "usage": {}

        }
# ==========================================================
# PostgreSQL
# ==========================================================

def postgres_metrics():

    try:

        conn = psycopg2.connect(

            host=POSTGRES_HOST,

            port=POSTGRES_PORT,

            dbname=POSTGRES_DB,

            user=POSTGRES_USER,

            password=POSTGRES_PASSWORD

        )

        cursor = conn.cursor()

        # ------------------------------------------
        # Tables
        # ------------------------------------------

        cursor.execute(
            """
            SELECT count(*)
            FROM information_schema.tables
            WHERE table_schema='public'
            """
        )

        tables = cursor.fetchone()[0]

        # ------------------------------------------
        # Active Connections
        # ------------------------------------------

        cursor.execute(
            """
            SELECT count(*)
            FROM pg_stat_activity
            """
        )

        connections = cursor.fetchone()[0]

        # ------------------------------------------
        # Database Size
        # ------------------------------------------

        cursor.execute(
            """
            SELECT pg_database_size(current_database())
            """
        )

        database_size = cursor.fetchone()[0]

        # ------------------------------------------
        # Indexes
        # ------------------------------------------

        cursor.execute(
            """
            SELECT count(*)
            FROM pg_indexes
            WHERE schemaname='public'
            """
        )

        indexes = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {

            "healthy": True,

            "tables": tables,

            "connections": connections,

            "database_size": database_size,

            "indexes": indexes

        }

    except Exception:

        return {

            "healthy": False,

            "tables": 0,

            "connections": 0,

            "database_size": 0,

            "indexes": 0

        }

# ==========================================================
# Storage Summary
# ==========================================================

def storage_summary():

    clickhouse = clickhouse_metrics()

    minio = minio_metrics()

    #postgres = postgres_metrics()

    healthy = sum([

        clickhouse["healthy"],

        minio["healthy"],

        #postgres["healthy"]

    ])

    return {

        "services": 2,

        "healthy": healthy,

        "clickhouse": clickhouse,

        "minio": minio,

        #"postgres": postgres

    }

def bytes_to_human(size):

    units = [

        "B",

        "KB",

        "MB",

        "GB",

        "TB"

    ]

    i = 0

    while size >= 1024 and i < len(units) - 1:

        size /= 1024

        i += 1

    return f"{size:.2f} {units[i]}"