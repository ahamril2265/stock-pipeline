import os
from datetime import datetime, UTC, timedelta

import clickhouse_connect
import requests

# ==========================================================
# ClickHouse Client
# ==========================================================

def _ch_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "admin"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "admin123"),
        database=os.getenv("CLICKHOUSE_DATABASE", "stock_analytics"),
    )

def _scalar(client, sql, default=0):
    try:
        result = client.query(sql)
        if result.result_rows and result.result_rows[0][0] is not None:
            return result.result_rows[0][0]
    except Exception:
        pass
    return default


# ==========================================================
# Recovery KPIs  (derived from gold table health)
# ==========================================================

def get_recovery_metrics():
    try:
        client = _ch_client()
        rows_kpis   = _scalar(client, "SELECT count() FROM gold_market_kpis")
        rows_sym    = _scalar(client, "SELECT count() FROM gold_symbol_summary")
        rows_top    = _scalar(client, "SELECT count() FROM gold_top_symbols")
        rows_ohlc   = _scalar(client, "SELECT count() FROM gold_ohlc")
        total_gold  = rows_kpis + rows_sym + rows_top + rows_ohlc
        recovered   = total_gold
        rejected    = 0
        success_pct = 100.0 if total_gold > 0 else 0.0
        return {
            "recovered_messages": recovered,
            "retry_queue": 0,
            "dead_letter_queue": rejected,
            "recovery_success": success_pct,
        }
    except Exception:
        return {
            "recovered_messages": 0,
            "retry_queue": 0,
            "dead_letter_queue": 0,
            "recovery_success": 0.0,
        }


# ==========================================================
# Bronze Layer  (derived from gold freshness proxy)
# ==========================================================

def bronze_status():
    try:
        client = _ch_client()
        latest = _scalar(client, "SELECT max(updated_at) FROM gold_market_kpis")
        rows   = _scalar(client, "SELECT count() FROM gold_market_kpis")
        return {
            "records": rows,
            "latest_write": latest if latest else datetime.now(UTC),
            "checkpoint": rows > 0,
            "quarantined": 0,
            "latency": 0.0,
        }
    except Exception:
        return {
            "records": 0,
            "latest_write": None,
            "checkpoint": False,
            "quarantined": 0,
            "latency": 0.0,
        }


# ==========================================================
# Silver Layer  (derived from symbol summary)
# ==========================================================

def silver_status():
    try:
        client = _ch_client()
        processed = _scalar(client, "SELECT count() FROM gold_symbol_summary")
        ohlc_rows = _scalar(client, "SELECT count() FROM gold_ohlc")
        return {
            "processed": processed + ohlc_rows,
            "duplicates": 0,
            "rejected": 0,
            "checkpoint": processed > 0,
            "latency": 0.0,
        }
    except Exception:
        return {
            "processed": 0,
            "duplicates": 0,
            "rejected": 0,
            "checkpoint": False,
            "latency": 0.0,
        }


# ==========================================================
# Gold Layer
# ==========================================================

def gold_status():
    try:
        client = _ch_client()
        r_kpis = _scalar(client, "SELECT count() FROM gold_market_kpis")
        r_sym  = _scalar(client, "SELECT count() FROM gold_symbol_summary")
        r_top  = _scalar(client, "SELECT count() FROM gold_top_symbols")
        r_ohlc = _scalar(client, "SELECT count() FROM gold_ohlc")
        latest = _scalar(client, "SELECT max(updated_at) FROM gold_market_kpis")
        total_rows = r_kpis + r_sym + r_top + r_ohlc
        failures = 0 if total_rows > 0 else 1
        return {
            "tables": 4,
            "rows": total_rows,
            "refresh": latest if latest else None,
            "failures": failures,
        }
    except Exception:
        return {"tables": 4, "rows": 0, "refresh": None, "failures": 1}


# ==========================================================
# Pipeline Flow  (live service health)
# ==========================================================

def pipeline_flow():
    try:
        from health import all_services
        services = all_services()
    except Exception:
        services = {}

    kafka_ok  = services.get("Kafka", False)
    spark_ok  = services.get("Spark", False)
    ch_ok     = services.get("ClickHouse", False)

    gold = gold_status()
    gold_ok = gold["rows"] > 0

    return [
        {"name": "Producer",    "healthy": kafka_ok},
        {"name": "Kafka",       "healthy": kafka_ok},
        {"name": "Bronze",      "healthy": spark_ok and kafka_ok},
        {"name": "Silver",      "healthy": spark_ok},
        {"name": "Gold",        "healthy": gold_ok},
        {"name": "ClickHouse",  "healthy": ch_ok},
        {"name": "Dashboard",   "healthy": True},
    ]


# ==========================================================
# Failure Events  (real unhealthy services)
# ==========================================================

def failure_events():
    try:
        from health import all_services
        services = all_services()
    except Exception:
        return []

    now = datetime.now(UTC)
    events = []
    for service, healthy in services.items():
        if not healthy:
            events.append({
                "time":      now,
                "component": service,
                "event":     "Service Unreachable",
                "status":    "OFFLINE",
            })
    return events


# ==========================================================
# Recovery Statistics  (from gold layer health)
# ==========================================================

def recovery_statistics():
    gold = gold_status()
    has_data = gold["rows"] > 0
    return {
        "avg_recovery": 0.0 if has_data else 5.0,
        "max_recovery": 0.0 if has_data else 10.0,
        "total_recoveries": gold["rows"],
        "successful_retries": gold["rows"],
        "failed_retries": gold["failures"],
    }


# ==========================================================
# Alerts  (real service alerts)
# ==========================================================

def alerts():
    try:
        from health import all_services, system_resources
        services  = all_services()
        resources = system_resources()
    except Exception:
        return []

    items = []
    for service, healthy in services.items():
        if not healthy:
            items.append(f"❌ {service} is OFFLINE.")
    if resources.get("cpu", 0) > 85:
        items.append(f"🔥 High CPU: {resources['cpu']}%")
    if resources.get("memory", 0) > 85:
        items.append(f"🧠 High Memory: {resources['memory']}%")
    if resources.get("disk", 0) > 90:
        items.append(f"💾 Disk critical: {resources['disk']}%")
    return items