import streamlit as st
import pandas as pd
from airflow_metrics import health, dags, dag_runs, summary, airflow_alive
from components.cards import metric_card, section_header, page_title
from config import PLOTLY_CONFIG

def render():
    page_title("🌬 Airflow Monitor", "Apache Airflow Workflow Orchestration")

    if not airflow_alive():
        st.error("❌ Airflow webserver unreachable. Is the stack running?")
        return

    h = health()
    st.divider()

    # ── Health Cards ─────────────────────────────────────
    section_header("❤ Airflow Health")
    if h:
        c1, c2 = st.columns(2)
        with c1:
            ok = h.get("scheduler") == "healthy"
            metric_card("Scheduler", h.get("scheduler","unknown").title(), "⚙",
                        color="success" if ok else "error")
        with c2:
            ok2 = h.get("metadatabase") == "healthy"
            metric_card("Metadatabase", h.get("metadatabase","unknown").title(), "🗄",
                        color="success" if ok2 else "error")
    else:
        st.warning("Health details unavailable.")

    st.divider()

    # ── DAG Summary ──────────────────────────────────────
    dag_summary = summary()
    section_header("📋 DAG Overview")
    d1, d2, d3 = st.columns(3)
    with d1:
        metric_card("Total DAGs",   str(dag_summary["total"]),  "📂")
    with d2:
        metric_card("Active DAGs",  str(dag_summary["active"]), "✅", color="success")
    with d3:
        metric_card("Paused DAGs",  str(dag_summary["paused"]), "⏸", color="warning")

    st.divider()

    # ── DAG List ──────────────────────────────────────────
    section_header("📋 DAG List")
    dag_list = dags()
    if dag_list:
        df = pd.DataFrame(dag_list)
        st.dataframe(df, hide_index=True, use_container_width=True)

        # ── DAG Runs ──────────────────────────────────────
        st.divider()
        section_header("🏃 DAG Runs")
        dag_ids = [d["DAG ID"] for d in dag_list]
        selected_dag = st.selectbox("Select DAG to view runs", dag_ids)
        if selected_dag:
            runs = dag_runs(selected_dag)
            if runs:
                df_runs = pd.DataFrame(runs)
                st.dataframe(df_runs, hide_index=True, use_container_width=True)
            else:
                st.info("No runs found for this DAG.")
    else:
        st.info("No DAGs found.")