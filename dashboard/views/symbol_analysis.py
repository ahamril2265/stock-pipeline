import streamlit as st
import plotly.graph_objects as go

from db import (
    get_symbol_summary,
    get_ohlc
)

from components.cards import metric_card

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

    st.title("🔍 Symbol Analysis")
    st.caption("Detailed analytics for an individual stock")

    # ==================================================
    # Load Data
    # ==================================================

    summary_df = get_symbol_summary()

    if summary_df.empty:
        st.warning("No symbol summary available.")
        return

    ohlc_df = get_ohlc()

    # ==================================================
    # Symbol Selection
    # ==================================================

    symbol = st.selectbox(
        "Select Stock Symbol",
        sorted(summary_df["stock_symbol"].unique())
    )

    row = summary_df[
        summary_df["stock_symbol"] == symbol
    ].iloc[0]

    # ==================================================
    # Market KPIs
    # ==================================================

    st.subheader("📊 Market Metrics")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Latest Price",
            f"${row['latest_price']:.2f}",
            "💲"
        )

    with c2:
        metric_card(
            "VWAP",
            f"${row['vwap']:.2f}",
            "📈"
        )

    with c3:
        metric_card(
            "Average Spread",
            f"{row['avg_spread']:.4f}",
            "↔️"
        )

    with c4:
        metric_card(
            "Latency",
            f"{row['avg_latency']:.2f} ms",
            "⚡"
        )

    st.write("")

    c5, c6 = st.columns(2)

    with c5:
        metric_card(
            "Buy Volume",
            f"{int(row['buy_volume']):,}",
            "🟢"
        )

    with c6:
        metric_card(
            "Sell Volume",
            f"{int(row['sell_volume']):,}",
            "🔴"
        )

    st.info(f"Selected Symbol: **{symbol}**")

    st.divider()

    # ==================================================
    # OHLC Chart
    # ==================================================

    filtered = ohlc_df[
        ohlc_df["stock_symbol"] == symbol
    ].sort_values("window_start")

    if not filtered.empty:

        st.subheader("🕯 Price Action")

        fig = go.Figure()

        fig.add_trace(

            go.Candlestick(

                x=filtered["window_start"],

                open=filtered["open_price"],

                high=filtered["high_price"],

                low=filtered["low_price"],

                close=filtered["close_price"],

                increasing_line_color="#00E676",

                decreasing_line_color="#FF5252",

                name=symbol

            )

        )

        fig.update_layout(

            template="plotly_dark",

            height=600,

            title=f"{symbol} OHLC",

            xaxis_title="Time",

            yaxis_title="Price ($)",

            xaxis_rangeslider_visible=False,

            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )

        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=PLOTLY_CONFIG
        )

    st.divider()

    # ==================================================
    # Additional Statistics
    # ==================================================

    if not filtered.empty:

        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric(
                "Highest Price",
                f"${filtered['high_price'].max():.2f}"
            )

        with s2:
            st.metric(
                "Lowest Price",
                f"${filtered['low_price'].min():.2f}"
            )

        with s3:
            st.metric(
                "Average Volume",
                f"{int(filtered['total_volume'].mean()):,}"
            )

    st.divider()

    # ==================================================
    # Symbol Statistics
    # ==================================================

    st.subheader("📋 Symbol Statistics")

    stats = {
        "Metric": [
            "Latest Price",
            "VWAP",
            "Average Spread",
            "Average Latency",
            "Buy Volume",
            "Sell Volume"
        ],
        "Value": [
            f"${row['latest_price']:.2f}",
            f"${row['vwap']:.2f}",
            f"{row['avg_spread']:.4f}",
            f"{row['avg_latency']:.2f} ms",
            f"{int(row['buy_volume']):,}",
            f"{int(row['sell_volume']):,}"
        ]
    }

    st.dataframe(
        stats,
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    # ==================================================
    # Recent OHLC Data
    # ==================================================

    with st.expander("📄 View Recent OHLC Records"):

        st.dataframe(
            filtered.sort_values(
                "window_start",
                ascending=False
            ),
            hide_index=True,
            use_container_width=True
        )
    
    render_notifications()