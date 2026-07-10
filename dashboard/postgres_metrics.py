import psycopg2


# ==========================================================
# Configuration
# ==========================================================

HOST = "postgres"
PORT = 5432

DATABASE = "airflow"

USER = "airflow"
PASSWORD = "airflow"


# ==========================================================
# Connection
# ==========================================================

def connection():

    return psycopg2.connect(

        host=HOST,

        port=PORT,

        dbname=DATABASE,

        user=USER,

        password=PASSWORD

    )


# ==========================================================
# Health
# ==========================================================

def postgres_alive():

    try:

        conn = connection()

        conn.close()

        return True

    except Exception:

        return False


# ==========================================================
# Metrics
# ==========================================================

def postgres_summary():

    try:

        conn = connection()

        cur = conn.cursor()

        # ------------------------------------
        # Database Size
        # ------------------------------------

        cur.execute("""

            SELECT pg_database_size(current_database())

        """)

        db_size = cur.fetchone()[0]

        # ------------------------------------
        # Active Connections
        # ------------------------------------

        cur.execute("""

            SELECT count(*)

            FROM pg_stat_activity

        """)

        connections = cur.fetchone()[0]

        # ------------------------------------
        # Tables
        # ------------------------------------

        cur.execute("""

            SELECT count(*)

            FROM information_schema.tables

            WHERE table_schema='public'

        """)

        tables = cur.fetchone()[0]

        # ------------------------------------
        # Indexes
        # ------------------------------------

        cur.execute("""

            SELECT count(*)

            FROM pg_indexes

            WHERE schemaname='public'

        """)

        indexes = cur.fetchone()[0]

        # ------------------------------------
        # Version
        # ------------------------------------

        cur.execute("""

            SELECT version()

        """)

        version = cur.fetchone()[0]

        cur.close()

        conn.close()

        return {

            "healthy": True,

            "database_size": db_size,

            "connections": connections,

            "tables": tables,

            "indexes": indexes,

            "version": version

        }

    except Exception:

        return {

            "healthy": False,

            "database_size": 0,

            "connections": 0,

            "tables": 0,

            "indexes": 0,

            "version": "Unknown"

        }


# ==========================================================
# Formatter
# ==========================================================

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