import streamlit as st
import pandas as pd

from components.architecture_flow import render as architecture_flow

from db import (
    get_market_kpis,
    get_symbol_summary,
    get_top_symbols,
    get_ohlc
)

from health import pipeline_summary
from components.cards import metric_card


def render():

    st.title("🏗 Pipeline Architecture")

    st.caption(
        "End-to-End Real-Time Stock Market Data Pipeline"
    )

    # =====================================================
    # Load Data
    # =====================================================

    market = get_market_kpis()
    summary = get_symbol_summary()
    top = get_top_symbols()
    ohlc = get_ohlc()

    pipeline = pipeline_summary()

    services = pipeline["services"]

    resources = pipeline["resources"]

    # =====================================================
    # Live KPIs
    # =====================================================

    st.subheader("🚀 Live Pipeline Overview")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        metric_card(
            "Trades",
            len(ohlc),
            "📈"
        )

    with c2:

        metric_card(
            "Symbols",
            len(summary),
            "📊"
        )

    with c3:

        metric_card(
            "Gold Tables",
            len(market),
            "🥇"
        )

    with c4:

        metric_card(
            "Top Symbols",
            len(top),
            "🏆"
        )

    with c5:

        healthy = sum(services.values())

        metric_card(
            "Services",
            f"{healthy}/{len(services)}",
            "🟢"
        )

    st.divider()

    # =====================================================
    # Pipeline Diagram
    # =====================================================

    architecture_flow()

    st.divider()

    # =====================================================
    # Infrastructure Resources
    # =====================================================

    st.subheader("💻 Infrastructure Resources")

    r1, r2, r3 = st.columns(3)

    with r1:

        st.metric(
            "CPU Usage",
            f"{resources['cpu']}%"
        )

        st.progress(resources["cpu"] / 100)

    with r2:

        st.metric(
            "Memory Usage",
            f"{resources['memory']}%"
        )

        st.progress(resources["memory"] / 100)

    with r3:

        st.metric(
            "Disk Usage",
            f"{resources['disk']}%"
        )

        st.progress(resources["disk"] / 100)

    st.divider()

    # =====================================================
    # Technology Stack
    # =====================================================

    st.subheader("🛠 Technology Stack")

    stack = pd.DataFrame({

        "Component": [

            "Producer",
            "Kafka",
            "Spark",
            "Bronze",
            "Silver",
            "Gold",
            "ClickHouse",
            "Airflow",
            "MinIO",
            "Dashboard"

        ],

        "Technology": [

            "Python",
            "Apache Kafka",
            "Apache Spark",
            "Delta Lake",
            "Spark SQL",
            "ClickHouse",
            "ClickHouse SQL",
            "Apache Airflow",
            "MinIO",
            "Streamlit"

        ],

        "Status": [

            "🟢",
            "🟢",
            "🟢",
            "🟢",
            "🟢",
            "🟢",
            "🟢",
            "🟢",
            "🟢",
            "🟢"

        ]

    })

    st.dataframe(

        stack,

        hide_index=True,

        use_container_width=True

    )

    st.divider()

    # =====================================================
    # Component Status
    # =====================================================

    st.subheader("⚙ Component Status")

    cols = st.columns(len(services))

    for col, (name, healthy) in zip(cols, services.items()):

        with col:

            if healthy:

                st.success(name)

            else:

                st.error(name)

    st.divider()

    # =====================================================
    # Pipeline Summary
    # =====================================================

    st.subheader("📋 Pipeline Summary")

    summary_df = pd.DataFrame({

        "Stage": [

            "Producer",
            "Kafka",
            "Bronze",
            "Spark",
            "Silver",
            "Gold",
            "Dashboard"

        ],

        "Description": [

            "Generates market trades",

            "Streams events",

            "Stores raw Delta data",

            "Processes streaming jobs",

            "Validates & cleans data",

            "Aggregates analytics",

            "Visualizes results"

        ],

        "Status": [

            "🟢",

            "🟢",

            "🟢",

            "🟢",

            "🟢",

            "🟢",

            "🟢"

        ]

    })

    st.dataframe(

        summary_df,

        hide_index=True,

        use_container_width=True

    )

    st.divider()

    # =====================================================
    # Overall Health
    # =====================================================

    if pipeline["overall"]:

        st.success(
            "✅ Entire Pipeline is Healthy"
        )

    else:

        st.error(
            "❌ One or more services are offline."
        )