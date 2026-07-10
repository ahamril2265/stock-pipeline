import streamlit as st
import pandas as pd

from spark_metrics import (
    spark_alive,
    cluster_summary,
    cluster_metrics,
    workers,
    applications,
    resource_usage
)

from components.cards import metric_card


def render():

    st.title("⚡ Spark Cluster")

    st.caption(
        "Real-time monitoring of the Apache Spark cluster"
    )

    # =====================================================
    # Connection
    # =====================================================

    if not spark_alive():

        st.error(
            "❌ Unable to connect to Spark Master."
        )

        st.info(
            "Verify that the Spark Master is running."
        )

        return

    summary = cluster_summary()

    metrics = cluster_metrics()

    usage = resource_usage()

    worker_df = pd.DataFrame(workers())

    app_df = pd.DataFrame(applications())

    # =====================================================
    # Status
    # =====================================================

    st.success(
        f"🟢 Spark Cluster Online • {summary['alive_workers']} Worker(s) Alive"
    )

    st.divider()

    # =====================================================
    # Cluster Overview
    # =====================================================

    st.subheader("📊 Cluster Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        metric_card(
            "Workers",
            summary["workers"],
            "👷"
        )

    with c2:

        metric_card(
            "Applications",
            summary["applications"],
            "🚀"
        )

    with c3:

        metric_card(
            "Drivers",
            summary["drivers"],
            "🖥"
        )

    with c4:

        metric_card(
            "Completed Apps",
            summary["completed_apps"],
            "✅"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # Resource Utilization
    # =====================================================

    st.subheader("💻 Cluster Resources")

    left, right = st.columns(2)

    with left:

        st.metric(
            "CPU Usage",
            f"{metrics['cpu_usage']}%"
        )

        st.progress(
            metrics["cpu_usage"] / 100
        )

        st.caption(
            f"{summary['cores_used']} / {summary['cores_total']} Cores"
        )

    with right:

        st.metric(
            "Memory Usage",
            f"{metrics['memory_usage']}%"
        )

        st.progress(
            metrics["memory_usage"] / 100
        )

        st.caption(
            f"{summary['memory_used']:,} MB / {summary['memory_total']:,} MB"
        )

    st.divider()

    # =====================================================
    # Cluster Statistics
    # =====================================================

    st.subheader("📈 Cluster Statistics")

    s1, s2, s3, s4 = st.columns(4)

    with s1:

        metric_card(
            "Alive Workers",
            summary["alive_workers"],
            "🟢"
        )

    with s2:

        metric_card(
            "Dead Workers",
            summary["dead_workers"],
            "🔴"
        )

    with s3:

        metric_card(
            "Free Cores",
            summary["cores_free"],
            "⚙"
        )

    with s4:

        metric_card(
            "Cluster Utilization",
            f"{metrics['cluster_utilization']}%",
            "📊"
        )

    st.divider()

    # =====================================================
    # Workers
    # =====================================================

    st.subheader("👷 Worker Details")

    if worker_df.empty:

        st.info("No Spark workers registered.")

    else:

        st.dataframe(
            worker_df,
            hide_index=True,
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # Applications
    # =====================================================

    st.subheader("🚀 Active Applications")

    if app_df.empty:

        st.info(
            "No active Spark applications."
        )

    else:

        st.dataframe(
            app_df,
            hide_index=True,
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # Cluster Summary
    # =====================================================

    st.subheader("📋 Cluster Summary")

    summary_df = pd.DataFrame({

        "Metric": [

            "Workers",

            "Alive Workers",

            "Dead Workers",

            "Applications",

            "Completed Applications",

            "Drivers",

            "CPU Usage",

            "Memory Usage",

            "Cluster Utilization"

        ],

        "Value": [

            summary["workers"],

            summary["alive_workers"],

            summary["dead_workers"],

            summary["applications"],

            summary["completed_apps"],

            summary["drivers"],

            f"{metrics['cpu_usage']}%",

            f"{metrics['memory_usage']}%",

            f"{metrics['cluster_utilization']}%"

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

    if summary["dead_workers"] == 0:

        st.success("🟢 All Spark workers are online.")

    else:

        st.error(
            f"🔴 {summary['dead_workers']} worker(s) are offline."
        )

    if summary["applications"] > 0:

        st.success(
            f"🟢 {summary['applications']} active application(s)."
        )

    else:

        st.warning(
            "🟡 No active Spark applications."
        )

    if metrics["cpu_usage"] > 90:

        st.warning(
            "⚠ CPU utilization is above 90%."
        )

    if metrics["memory_usage"] > 90:

        st.warning(
            "⚠ Memory utilization is above 90%."
        )

    if metrics["cluster_utilization"] > 85:

        st.warning(
            "⚠ Cluster utilization is high."
        )