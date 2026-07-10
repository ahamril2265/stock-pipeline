import streamlit as st


def render():

    # ==================================================
    # Branding
    # ==================================================

    st.sidebar.title("📈 Stock Analytics")

    st.sidebar.caption(
        "Real-Time Market Intelligence Platform"
    )

    st.sidebar.divider()

    # ==================================================
    # Navigation
    # ==================================================

    page = st.sidebar.radio(

        "Navigation",

        [

            "📈 Market Overview",

            "🏆 Top Symbols",

            "🔍 Symbol Analysis",

            "🕯 OHLC",

            "⚙ Pipeline Health",

            "🛡 Failure Recovery",

            "⚡ Spark Cluster",

            "🌬 Airflow Monitor",

            "📨 Kafka Cluster",

            "💾 Storage Monitor",

            "📜 Live Logs",

            "🏗 Architecture",

            "📊 Performance Benchmark",

        ]

    )

    st.sidebar.divider()

    # ==================================================
    # Pipeline Status
    # ==================================================

    st.sidebar.subheader("🚀 Pipeline")

    services = [

        ("Kafka", "🟢"),

        ("Spark", "🟢"),

        ("ClickHouse", "🟢"),

        ("Airflow", "🟢"),

        ("MinIO", "🟢")

    ]

    for service, status in services:

        left, right = st.sidebar.columns([5, 1])

        with left:
            st.write(service)

        with right:
            st.write(status)

    st.sidebar.divider()

    # ==================================================
    # Project Information
    # ==================================================

    st.sidebar.subheader("📦 Project")

    st.sidebar.markdown(
        """
        **Architecture**

        - Kafka
        - Spark
        - Delta Lake
        - ClickHouse
        - Airflow
        - MinIO
        """
    )

    st.sidebar.info("🔄 Auto Refresh: 5 Seconds")

    st.sidebar.success("Version 1.0.0")

    st.sidebar.divider()

    # ==================================================
    # Developer
    # ==================================================

    st.sidebar.caption("Developed by")

    st.sidebar.markdown("**Ahamed Rilwan**")

    return page