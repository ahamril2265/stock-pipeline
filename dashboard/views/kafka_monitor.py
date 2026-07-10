import streamlit as st
import pandas as pd

from kafka_metrics import (
    broker_alive,
    cluster_summary,
    topics,
    topic_statistics,
    cluster_health
)

from components.cards import metric_card


def render():

    st.title("📨 Kafka Cluster")

    st.caption(
        "Real-time monitoring of Apache Kafka"
    )

    # =====================================================
    # Connection
    # =====================================================

    if not broker_alive():

        st.error(
            "❌ Kafka Broker is unreachable."
        )

        st.info(
            "Verify that the Kafka container is running."
        )

        return

    summary = cluster_summary()

    health = cluster_health()

    topic_df = pd.DataFrame(
        topic_statistics()
    )

    # =====================================================
    # Status
    # =====================================================

    st.success(
        "🟢 Kafka Broker Connected"
    )

    st.divider()

    # =====================================================
    # KPI Cards
    # =====================================================

    st.subheader("📊 Cluster Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        metric_card(
            "Broker",
            summary["broker"],
            "🖥"
        )

    with c2:

        metric_card(
            "Topics",
            summary["topics"],
            "📦"
        )

    with c3:

        metric_card(
            "Partitions",
            summary["partitions"],
            "🧩"
        )

    with c4:

        metric_card(
            "User Topics",
            summary["user_topics"],
            "📁"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # Additional Metrics
    # =====================================================

    st.subheader("📈 Topic Statistics")

    left, right = st.columns(2)

    with left:

        st.metric(
            "Internal Topics",
            summary["internal_topics"]
        )

    with right:

        st.metric(
            "Healthy Broker",
            "YES" if health["healthy"] else "NO"
        )

    st.divider()

    # =====================================================
    # Topics
    # =====================================================

    st.subheader("📋 Topic Details")

    if topic_df.empty:

        st.warning(
            "No topics available."
        )

    else:

        st.dataframe(
            topic_df,
            hide_index=True,
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # Cluster Summary
    # =====================================================

    st.subheader("📊 Cluster Summary")

    summary_df = pd.DataFrame({

        "Metric": [

            "Broker Status",

            "Topics",

            "User Topics",

            "Internal Topics",

            "Partitions"

        ],

        "Value": [

            summary["broker"],

            summary["topics"],

            summary["user_topics"],

            summary["internal_topics"],

            summary["partitions"]

        ]

    })

    st.dataframe(
        summary_df,
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # Health
    # =====================================================

    st.subheader("❤️ Cluster Health")

    if health["healthy"]:

        st.success("🟢 Kafka Cluster Healthy")

    else:

        st.error("🔴 Kafka Cluster Offline")

    st.info(
        f"""
Broker Status: **{summary['broker']}**

Topics: **{summary['topics']}**

Partitions: **{summary['partitions']}**
"""
    )