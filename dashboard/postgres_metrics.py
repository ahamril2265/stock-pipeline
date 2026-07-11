import os
import psycopg2


# ==========================================================
# Configuration  (from env vars, matching docker-compose)
# ==========================================================

HOST     = os.getenv("POSTGRES_HOST",     "postgres")
PORT     = int(os.getenv("POSTGRES_PORT", 5432))
DATABASE = os.getenv("POSTGRES_DB",       "stockdb")
USER     = os.getenv("POSTGRES_USER",     "admin")
PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")


# ==========================================================
# Connection
# ==========================================================

def connection():
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
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
        cur  = conn.cursor()

        cur.execute("SELECT pg_database_size(current_database())")
        db_size = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM pg_stat_activity")
        connections = cur.fetchone()[0]

        cur.execute("""
            SELECT count(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchone()[0]

        cur.execute("""
            SELECT count(*)
            FROM pg_indexes
            WHERE schemaname = 'public'
        """)
        indexes = cur.fetchone()[0]

        cur.execute("SELECT version()")
        version = cur.fetchone()[0]

        cur.close()
        conn.close()

        return {
            "healthy":       True,
            "database_size": db_size,
            "connections":   connections,
            "tables":        tables,
            "indexes":       indexes,
            "version":       version,
        }

    except Exception:
        return {
            "healthy":       False,
            "database_size": 0,
            "connections":   0,
            "tables":        0,
            "indexes":       0,
            "version":       "Unavailable",
        }


# ==========================================================
# Formatter
# ==========================================================

def bytes_to_human(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {units[i]}"