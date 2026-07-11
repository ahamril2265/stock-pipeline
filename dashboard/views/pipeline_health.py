import streamlit as st
from db import get_market_kpis, get_symbol_summary, get_top_symbols, get_ohlc, get_gold_freshness
from components.cards import metric_card, status_badge, section_header, page_title
from components.charts import gauge_chart
from notifications import get_notifications
from health import pipeline_summary, system_resources
from config import PLOTLY_CONFIG

def render():
    page_title("⚙ Pipeline Health", "Real-time Infrastructure & Data Layer Monitoring")

    # ── Data ──────────────────────────────────────────────
    pipeline  = pipeline_summary()
    services  = pipeline["services"]
    resources = pipeline["resources"]
    healthy   = pipeline["healthy"]
    total     = pipeline["total"]
    pct       = pipeline["health_percentage"]

    # ── Overall Banner ─────────────────────────────────────
    if pct == 100:
        banner_cls = "health-banner-ok"
        banner_txt = f"✅ Pipeline Fully Healthy — {healthy}/{total} services online"
    elif pct >= 70:
        banner_cls = "health-banner-warn"
        banner_txt = f"⚠ Pipeline Degraded — {healthy}/{total} services online"
    else:
        banner_cls = "health-banner-err"
        banner_txt = f"❌ Pipeline Critical — only {healthy}/{total} services online"

    st.markdown(f'<div class="{banner_cls}">{banner_txt}</div>', unsafe_allow_html=True)
    st.write("")

    # ── Gauge Charts (resources) ───────────────────────────
    section_header("💻 Host Resource Utilization")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.plotly_chart(gauge_chart(resources["cpu"],    100, "CPU Usage %"),    use_container_width=True)
    with g2:
        st.plotly_chart(gauge_chart(resources["memory"], 100, "Memory Usage %"), use_container_width=True)
    with g3:
        st.plotly_chart(gauge_chart(resources["disk"],   100, "Disk Usage %"),   use_container_width=True)

    st.divider()

    # ── Service Status Grid ────────────────────────────────
    section_header("🚀 Infrastructure Services")
    descriptions = {
        "Kafka":           "Streaming Platform (port 29092)",
        "Spark":           "Processing Engine (port 8080)",
        "Schema Registry": "Avro Schema Service (port 8081)",
        "ClickHouse":      "Analytics Database (port 8123)",
        "PostgreSQL":      "Metadata Store (port 5432)",
        "MinIO":           "Object Storage (port 9000)",
        "Airflow":         "Workflow Scheduler (port 8088)",
    }
    left, right = st.columns(2)
    service_items = list(services.items())
    mid = len(service_items) // 2 + len(service_items) % 2
    with left:
        for svc, ok in service_items[:mid]:
            status_badge(svc, ok, descriptions.get(svc, ""))
    with right:
        for svc, ok in service_items[mid:]:
            status_badge(svc, ok, descriptions.get(svc, ""))

    st.divider()

    # ── Gold Layer Status ──────────────────────────────────
    section_header("🗄 Gold Layer Data Freshness")
    freshness = get_gold_freshness()
    gl1, gl2 = st.columns(2)
    gold_items = list(freshness.items())
    for i, (label, info) in enumerate(gold_items):
        col = gl1 if i % 2 == 0 else gl2
        with col:
            has_data = info["rows"] > 0
            status_badge(
                label,
                has_data,
                f"{info['rows']:,} rows • Updated: {info['ts'] or 'n/a'}",
            )

    st.divider()

    # ── Alerts ────────────────────────────────────────────
    section_header("🚨 Active Alerts")
    alerts = get_notifications()
    if not alerts:
        st.success("✅ No active alerts.")
    else:
        for alert in alerts:
            if alert["level"] == "error":
                st.error(f"🚨 **{alert['title']}** — {alert['message']}")
            elif alert["level"] == "warning":
                st.warning(f"⚠ **{alert['title']}** — {alert['message']}")
            else:
                st.info(f"ℹ **{alert['title']}** — {alert['message']}")