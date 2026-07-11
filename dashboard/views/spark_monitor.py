import streamlit as st
import pandas as pd
from spark_metrics import cluster_metrics, workers, applications
from components.cards import metric_card, section_header, page_title
from components.charts import cluster_bar, gauge_chart
from config import PLOTLY_CONFIG

def render():
    page_title("⚡ Spark Cluster", "Apache Spark Structured Streaming Monitor")

    metrics = cluster_metrics()

    if metrics is None:
        st.error("❌ Spark Master unreachable. Is the stack running?")
        st.info("Expected at: http://spark-master:8080")
        return

    st.divider()

    # ── Summary Cards ─────────────────────────────────────
    section_header("🏭 Cluster Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Workers",        f'{metrics["alive_workers"]}/{metrics["workers"]}', "🖥",
                    color="success" if metrics["alive_workers"] == metrics["workers"] else "error")
    with c2:
        metric_card("Cores Used",     f'{metrics["cores_used"]}/{metrics["cores_total"]}', "⚙", color="primary")
    with c3:
        metric_card("Memory Used",    f'{metrics["memory_used"]} / {metrics["memory_total"]} MB', "🧠", color="primary")
    with c4:
        metric_card("Active Apps",    str(metrics["applications"]), "🚀",
                    color="success" if metrics["applications"] > 0 else "warning")

    st.write("")
    c5, c6, c7 = st.columns(3)
    with c5:
        metric_card("Dead Workers",    str(metrics["dead_workers"]),     "💀", color="error" if metrics["dead_workers"] > 0 else "success")
    with c6:
        metric_card("Completed Apps",  str(metrics["completed_apps"]),   "✅", color="success")
    with c7:
        metric_card("Cluster Util %",  f'{metrics["cluster_utilization"]}%', "📊",
                    color="warning" if metrics["cluster_utilization"] > 80 else "primary")

    st.divider()

    # ── Gauge Charts ─────────────────────────────────────
    section_header("📊 Cluster Utilization")
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(gauge_chart(metrics["cpu_usage"],    100, "Core Utilization %"), use_container_width=True)
    with g2:
        st.plotly_chart(gauge_chart(metrics["memory_usage"], 100, "Memory Utilization %"), use_container_width=True)

    st.divider()

    # ── Worker Table ─────────────────────────────────────
    section_header("🖥 Worker Details")
    worker_list = workers()
    if worker_list:
        df = pd.DataFrame(worker_list)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("No workers registered.")

    # ── Applications Table ────────────────────────────────
    app_list = applications()
    if app_list:
        st.divider()
        section_header("🚀 Active Applications")
        df_apps = pd.DataFrame(app_list)
        st.dataframe(df_apps, hide_index=True, use_container_width=True)