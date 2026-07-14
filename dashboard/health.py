import socket
import psutil
import requests
import clickhouse_connect

# ==========================================================
# Configuration
# ==========================================================

KAFKA_HOST = "kafka"
KAFKA_PORT = 29092

SPARK_MASTER_UI = "http://spark-master:8080"

AIRFLOW_URL = "http://airflow-webserver:8080"

MINIO_URL = "http://minio:9000"

SCHEMA_REGISTRY = "http://schema-registry:8081"

CLICKHOUSE_HOST = "clickhouse"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "admin"
CLICKHOUSE_PASSWORD = "admin123"
CLICKHOUSE_DATABASE = "stock_analytics"

POSTGRES_HOST = "postgres"
POSTGRES_PORT = 5432


# ==========================================================
# Generic Port Check
# ==========================================================

def check_port(host, port, timeout=1):

    try:

        sock = socket.create_connection(
            (host, port),
            timeout=timeout
        )

        sock.close()

        return True

    except Exception:

        return False


# ==========================================================
# Kafka
# ==========================================================

def kafka_health():

    return check_port(
        KAFKA_HOST,
        KAFKA_PORT
    )


# ==========================================================
# Spark Master
# ==========================================================

def spark_health():

    try:

        response = requests.get(
            SPARK_MASTER_UI,
            timeout=1
        )

        return response.status_code == 200

    except Exception:

        return False


# ==========================================================
# Airflow
# ==========================================================

def airflow_health():

    endpoints = [

        "/health",

        "/api/v1/health"

    ]

    for endpoint in endpoints:

        try:

            response = requests.get(
                AIRFLOW_URL + endpoint,
                timeout=1
            )

            if response.status_code == 200:

                return True

        except Exception:

            pass

    return False


# ==========================================================
# MinIO
# ==========================================================

def minio_health():

    try:

        response = requests.get(
            MINIO_URL + "/minio/health/live",
            timeout=1
        )

        return response.status_code == 200

    except Exception:

        return False


# ==========================================================
# Schema Registry
# ==========================================================

def schema_registry_health():

    try:

        response = requests.get(
            SCHEMA_REGISTRY + "/subjects",
            timeout=1
        )

        return response.status_code == 200

    except Exception:

        return False


# ==========================================================
# ClickHouse
# ==========================================================

def clickhouse_health():

    try:

        client = clickhouse_connect.get_client(

            host=CLICKHOUSE_HOST,

            port=CLICKHOUSE_PORT,

            username=CLICKHOUSE_USER,

            password=CLICKHOUSE_PASSWORD,

            database=CLICKHOUSE_DATABASE

        )

        client.command("SELECT 1")

        return True

    except Exception:

        return False


# ==========================================================
# PostgreSQL
# ==========================================================

def postgres_health():

    return check_port(

        POSTGRES_HOST,

        POSTGRES_PORT

    )


# ==========================================================
# Resource Monitoring
# ==========================================================

def system_resources():

    return {

        "cpu": round(

            psutil.cpu_percent(interval=0.5),

            1

        ),

        "memory": round(

            psutil.virtual_memory().percent,

            1

        ),

        "disk": round(

            psutil.disk_usage("/").percent,

            1

        )

    }


# ==========================================================
# Overall Service Status
# ==========================================================

def all_services():

    return {

        "Kafka": kafka_health(),

        "Spark": spark_health(),

        "Schema Registry": schema_registry_health(),

        "ClickHouse": clickhouse_health(),

        "PostgreSQL": postgres_health(),

        "MinIO": minio_health(),

        "Airflow": airflow_health()

    }


# ==========================================================
# Dashboard Summary
# ==========================================================

def pipeline_summary():

    services = all_services()

    healthy = sum(services.values())

    total = len(services)

    overall = healthy == total

    return {

        "overall": overall,

        "services": services,

        "healthy": healthy,

        "total": total,

        "resources": system_resources(),

        "health_percentage": round(
            healthy / total * 100,
            1
        )

    }