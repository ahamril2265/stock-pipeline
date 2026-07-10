import streamlit as st
import pandas as pd

from airflow_metrics import (
    airflow_alive,
    health,
    dags,
    dag_runs,
    summary
)

from components.cards import metric_card


def render():

    st.title("🌬 Airflow Monitor")

    st.caption(
        "Real-time monitoring of Apache Airflow"
    )

    # =====================================================
    # Connection
    # =====================================================

    if not airflow_alive():

        st.error(
            "❌ Unable to connect to Airflow."
        )

        st.info(
            "Verify that the Airflow Webserver is running."
        )

        return

    airflow_health = health()

    airflow_summary = summary()

    dag_df = pd.DataFrame(dags())

    # =====================================================
    # Overall Status
    # =====================================================

    st.success(
        "🟢 Airflow Connected"
    )

    st.divider()

    # =====================================================
    # KPI Cards
    # =====================================================

    st.subheader("📊 Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        metric_card(

            "Total DAGs",

            airflow_summary["total"],

            "📦"

        )

    with c2:

        metric_card(

            "Active DAGs",

            airflow_summary["active"],

            "▶"

        )

    with c3:

        metric_card(

            "Paused DAGs",

            airflow_summary["paused"],

            "⏸"

        )

    with c4:

        metric_card(

            "Scheduler",

            airflow_health["scheduler"].upper(),

            "⚙"

        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # Health
    # =====================================================

    st.subheader("❤️ Airflow Components")

    left, right = st.columns(2)

    with left:

        if airflow_health["scheduler"] == "healthy":

            st.success(
                "🟢 Scheduler Healthy"
            )

        else:

            st.error(
                "🔴 Scheduler Offline"
            )

    with right:

        if airflow_health["metadatabase"] == "healthy":

            st.success(
                "🟢 Metadata Database Healthy"
            )

        else:

            st.error(
                "🔴 Metadata Database Offline"
            )

    st.divider()

    # =====================================================
    # DAG List
    # =====================================================

    st.subheader("📋 DAGs")

    if dag_df.empty:

        st.info(
            "No DAGs found."
        )

    else:

        st.dataframe(

            dag_df,

            hide_index=True,

            use_container_width=True

        )

    st.divider()

    # =====================================================
    # DAG Runs
    # =====================================================

    if not dag_df.empty:

        st.subheader("▶ DAG Runs")

        dag = st.selectbox(

            "Select DAG",

            dag_df["DAG ID"]

        )

        runs = pd.DataFrame(

            dag_runs(dag)

        )

        if runs.empty:

            st.info(
                "No runs available."
            )

        else:

            st.dataframe(

                runs,

                hide_index=True,

                use_container_width=True

            )

    st.divider()

    # =====================================================
    # Scheduler Status
    # =====================================================

    st.subheader("🚦 Scheduler Status")

    if airflow_health["scheduler"] == "healthy":

        st.success(
            "Scheduler is operating normally."
        )

    else:

        st.error(
            "Scheduler is not healthy."
        )

    if airflow_health["metadatabase"] == "healthy":

        st.success(
            "Metadata Database connected."
        )

    else:

        st.error(
            "Metadata Database unavailable."
        )