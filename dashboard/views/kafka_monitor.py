import streamlit as st
import pandas as pd
import requests
from kafka_metrics import cluster_summary, topic_statistics, broker_alive
from components.cards import metric_card, section_header, page_title
from config import PLOTLY_CONFIG

SCHEMA_REGISTRY = "http://schema-registry:8081"

def render():
    page_title("📨 Kafka Cluster", "Apache Kafka & Schema Registry Monitor")

    alive   = broker_alive()
    summary = cluster_summary()

    if not alive or summary is None:
        st.error("❌ Kafka broker unreachable.")
        return

    st.divider()

    # ── Summary Cards ─────────────────────────────────────
    section_header("📊 Cluster Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Broker",        summary.get("broker", "ONLINE"),   "🟢", color="success")
    with c2:
        metric_card("Total Topics",  str(summary.get("topics", 0)),     "📂", color="primary")
    with c3:
        metric_card("Partitions",    str(summary.get("partitions", 0)), "📊", color="primary")
    with c4:
        metric_card("User Topics",   str(summary.get("user_topics", 0)),"📋", color="success")

    st.divider()

    # ── Topic Statistics ──────────────────────────────────
    section_header("📋 Topic Details")
    topics = topic_statistics()
    if topics:
        df = pd.DataFrame(topics)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("No topic data available.")

    st.divider()

    # ── Schema Registry ────────────────────────────────────
    section_header("📜 Schema Registry Subjects")
    try:
        resp = requests.get(f"{SCHEMA_REGISTRY}/subjects", timeout=4)
        if resp.status_code == 200:
            subjects = resp.json()
            metric_card("Registered Schemas", str(len(subjects)), "📝", color="success")
            st.write("")
            for subj in subjects:
                st.markdown(f'<code style="background:#1C2128;padding:3px 8px;border-radius:5px;font-size:0.82rem;">{subj}</code>', unsafe_allow_html=True)
        else:
            st.warning("Schema Registry responded with non-200 status.")
    except Exception:
        st.warning("⚠ Schema Registry unreachable.")