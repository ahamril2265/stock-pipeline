import streamlit as st

from db import (
    get_market_kpis,
    get_symbol_summary,
    get_top_symbols,
    get_ohlc
)
from notifications import render_notifications

from components.cards import metric_card
from health import pipeline_summary


def service_status(name, healthy, description=""):

    with st.container(border=True):

        left, right = st.columns([5, 1])

        with left:

            st.markdown(f"#### {name}")

            if description:
                st.caption(description)

        with right:

            if healthy:
                st.success("🟢")
            else:
                st.error("🔴")

        if healthy:
            st.success("ONLINE")
        else:
            st.error("OFFLINE")


def render():

    

    st.title("⚙ Pipeline Health")

    st.caption(
        "Real-time monitoring of the analytics platform"
    )

    # =====================================================
    # Load Gold Layer
    # =====================================================

    market = get_market_kpis()
    summary = get_symbol_summary()
    top = get_top_symbols()
    ohlc = get_ohlc()

    # =====================================================
    # Infrastructure Health
    # =====================================================

    pipeline = pipeline_summary()

    services = pipeline["services"]

    resources = pipeline["resources"]

    healthy_services = pipeline["healthy"]

    total_services = pipeline["total"]

    # =====================================================
    # Overall Status
    # =====================================================

    if healthy_services == total_services:

        st.success(
            f"✅ Pipeline Healthy ({healthy_services}/{total_services} services online)"
        )

    else:

        st.error(
            f"❌ Pipeline Degraded ({healthy_services}/{total_services} services online)"
        )

    st.divider()

    # =====================================================
    # Dataset KPIs
    # =====================================================

    st.subheader("📊 Gold Layer Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Market KPIs",
            len(market),
            "📊"
        )

    with c2:
        metric_card(
            "Symbol Summary",
            len(summary),
            "📈"
        )

    with c3:
        metric_card(
            "Top Symbols",
            len(top),
            "🏆"
        )

    with c4:
        metric_card(
            "OHLC",
            len(ohlc),
            "🕯"
        )

    st.divider()

    # =====================================================
    # Resource Usage
    # =====================================================

    st.subheader("💻 Resource Utilization")

    r1, r2, r3 = st.columns(3)

    with r1:

        st.metric(
            "CPU",
            f"{resources['cpu']}%"
        )

        st.progress(resources["cpu"] / 100)

    with r2:

        st.metric(
            "Memory",
            f"{resources['memory']}%"
        )

        st.progress(resources["memory"] / 100)

    with r3:

        st.metric(
            "Disk",
            f"{resources['disk']}%"
        )

        st.progress(resources["disk"] / 100)

    st.divider()

    # =====================================================
    # Gold Layer Status
    # =====================================================

    left, right = st.columns(2)

    with left:

        st.subheader("🗄 Gold Layer")

        service_status(
            "Market KPIs",
            not market.empty,
            "Aggregated market statistics"
        )

        service_status(
            "Symbol Summary",
            not summary.empty,
            "Per-symbol analytics"
        )

        service_status(
            "Top Symbols",
            not top.empty,
            "Top volume rankings"
        )

        service_status(
            "OHLC",
            not ohlc.empty,
            "Candlestick aggregation"
        )

    with right:

        st.subheader("🚀 Infrastructure")

        descriptions = {

            "Kafka": "Streaming Platform",

            "Spark": "Processing Engine",

            "Schema Registry": "Avro Schema Service",

            "ClickHouse": "Analytics Database",

            "PostgreSQL": "Metadata Store",

            "MinIO": "Object Storage",

            "Airflow": "Workflow Scheduler"

        }

        for service, status in services.items():

            service_status(

                service,

                status,

                descriptions.get(service, "")

            )

    st.divider()

    # =====================================================
    # Dataset Summary
    # =====================================================

    st.subheader("📋 Dataset Summary")

    stats = {

        "Dataset": [

            "Market KPIs",

            "Symbol Summary",

            "Top Symbols",

            "OHLC"

        ],

        "Rows": [

            len(market),

            len(summary),

            len(top),

            len(ohlc)

        ],

        "Status": [

            "🟢 Healthy" if not market.empty else "🔴 Empty",

            "🟢 Healthy" if not summary.empty else "🔴 Empty",

            "🟢 Healthy" if not top.empty else "🔴 Empty",

            "🟢 Healthy" if not ohlc.empty else "🔴 Empty"

        ]

    }

    st.dataframe(

        stats,

        hide_index=True,

        use_container_width=True

    )

    st.divider()

    # =====================================================
    # Gold Preview
    # =====================================================

    with st.expander("📈 Symbol Summary Preview"):

        st.dataframe(

            summary,

            hide_index=True,

            use_container_width=True

        )

    # =====================================================
    # Notifications
    # =====================================================

    st.divider()

    st.subheader("🚨 Notifications")

    alerts = []

    if resources["cpu"] > 85:
        alerts.append("🔥 High CPU utilization detected.")

    if resources["memory"] > 85:
        alerts.append("🧠 High memory utilization detected.")

    if resources["disk"] > 90:
        alerts.append("💾 Disk usage is critically high.")

    for service, status in services.items():

        if not status:
            alerts.append(f"❌ {service} is offline.")

    if alerts:

        for alert in alerts:

            st.error(alert)

    else:

        st.success("✅ No active alerts.")
    
    render_notifications()