import streamlit as st

from db import (
    get_market_kpis,
    get_top_symbols
)

from components.cards import metric_card
from components.charts import (
    top_symbols_chart,
    buy_sell_chart
)

from formatter import (
    number,
    price,
    latency
)
from notifications import render_notifications

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": [
        "lasso2d",
        "select2d"
    ]
}


def render():

    

    st.title("📈 Market Overview")
    st.caption("Real-Time Market Summary")

    # ==========================================
    # Load Data
    # ==========================================

    market_df = get_market_kpis()

    if market_df.empty:
        st.warning("No Market KPI data available.")
        return

    top_symbols = get_top_symbols()

    if top_symbols.empty:
        st.warning("No Top Symbols data available.")
        return

    row = market_df.iloc[0]

    # ==========================================
    # Market KPIs
    # ==========================================

    st.subheader("📊 Market KPIs")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Market Volume",
            number(row['total_market_volume']),
            "📊"
        )

    with c2:
        metric_card(
            "Active Symbols",
            number(row["active_symbols"]),
            "📈"
        )

    with c3:
        metric_card(
            "Market VWAP",
            price(row['market_vwap']),
            "💰"
        )

    with c4:
        metric_card(
            "Average Latency",
            latency(row['avg_market_latency']),
            "⚡"
        )

    st.write("")

    c5, c6, c7 = st.columns(3)

    with c5:
        metric_card(
            "Buy Volume",
            number(row['total_buy_volume']),
            "🟢"
        )

    with c6:
        metric_card(
            "Sell Volume",
            number(row['total_sell_volume']),
            "🔴"
        )

    with c7:
        metric_card(
            "Average Price",
            price(row['avg_market_price']),
            "💵"
        )

    st.info(f"🕒 Last Updated: {row['updated_at']}")

    st.divider()

    # ==========================================
    # Charts
    # ==========================================

    st.subheader("📊 Market Analytics")

    left, right = st.columns(2)

    with left:

        st.plotly_chart(
            top_symbols_chart(top_symbols),
            use_container_width=True,
            config=PLOTLY_CONFIG
        )

    with right:

        st.plotly_chart(
            buy_sell_chart(market_df),
            use_container_width=True,
            config=PLOTLY_CONFIG
        )

    st.divider()

    # ==========================================
    # Leaderboard
    # ==========================================

    st.subheader("🏆 Market Leaderboard")

    leaderboard = top_symbols[
        [
            "volume_rank",
            "stock_symbol",
            "latest_price",
            "total_volume",
            "buy_volume",
            "sell_volume",
            "vwap"
        ]
    ].rename(
        columns={
            "volume_rank": "Rank",
            "stock_symbol": "Symbol",
            "latest_price": "Price",
            "total_volume": "Volume",
            "buy_volume": "Buy Volume",
            "sell_volume": "Sell Volume",
            "vwap": "VWAP"
        }
    )

    st.dataframe(
        leaderboard,
        hide_index=True,
        use_container_width=True
    )

    # ==========================================
    # Raw Data
    # ==========================================

    with st.expander("🔍 View Raw Data"):

        st.dataframe(
            market_df,
            hide_index=True,
            use_container_width=True
        )
    
    render_notifications()