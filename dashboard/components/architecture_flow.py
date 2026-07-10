import streamlit as st

from health import pipeline_summary
from db import (
    get_market_kpis,
    get_symbol_summary,
    get_top_symbols,
    get_ohlc
)


# ==========================================================
# Pipeline Node
# ==========================================================

def node(title, icon, healthy, metric_name, metric_value):

    with st.container(border=True):

        st.markdown(
            f"""
            <div style="text-align:center;font-size:40px;">
            {icon}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"<h4 style='text-align:center'>{title}</h4>",
            unsafe_allow_html=True
        )

        if healthy:
            st.success("🟢 ONLINE")
        else:
            st.error("🔴 OFFLINE")

        st.metric(
            metric_name,
            metric_value
        )


# ==========================================================
# Arrow
# ==========================================================

def arrow():

    st.markdown(
        """
        <h2 style="text-align:center;padding-top:80px;">
        ➜
        </h2>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# Pipeline Diagram
# ==========================================================

def render():

    pipeline = pipeline_summary()

    services = pipeline["services"]

    market = get_market_kpis()

    summary = get_symbol_summary()

    top = get_top_symbols()

    ohlc = get_ohlc()

    cols = st.columns(13)

    with cols[0]:

        node(
            "Producer",
            "📤",
            True,
            "Trades",
            len(ohlc)
        )

    with cols[1]:
        arrow()

    with cols[2]:

        node(
            "Kafka",
            "📨",
            services["Kafka"],
            "Topics",
            "1"
        )

    with cols[3]:
        arrow()

    with cols[4]:

        node(
            "Bronze",
            "🥉",
            True,
            "Raw Trades",
            len(ohlc)
        )

    with cols[5]:
        arrow()

    with cols[6]:

        node(
            "Spark",
            "⚡",
            services["Spark"],
            "Jobs",
            "Streaming"
        )

    with cols[7]:
        arrow()

    with cols[8]:

        node(
            "Silver",
            "🥈",
            True,
            "Validated",
            len(summary)
        )

    with cols[9]:
        arrow()

    with cols[10]:

        node(
            "Gold",
            "🥇",
            services["ClickHouse"],
            "Analytics",
            len(market)
        )

    with cols[11]:
        arrow()

    with cols[12]:

        node(
            "Dashboard",
            "📊",
            True,
            "Views",
            "Live"
        )