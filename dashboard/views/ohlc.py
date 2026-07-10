import streamlit as st
import plotly.graph_objects as go

from db import get_ohlc
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

    

    st.title("🕯 OHLC Analysis")
    st.caption("Interactive candlestick visualization")

    # ==========================================
    # Load Data
    # ==========================================

    df = get_ohlc()

    if df.empty:
        st.warning("No OHLC data available.")
        return

    # ==========================================
    # Filters
    # ==========================================

    left, right = st.columns([3, 1])

    with left:

        symbol = st.selectbox(
            "Stock Symbol",
            sorted(df["stock_symbol"].unique())
        )

    with right:

        periods = {
            "10": 10,
            "25": 25,
            "50": 50,
            "All": None
        }

        selected = st.selectbox(
            "Candles",
            list(periods.keys()),
            index=2
        )

    # ==========================================
    # Filter Dataset
    # ==========================================

    filtered = df[
        df["stock_symbol"] == symbol
    ].sort_values("window_start")

    if periods[selected] is not None:
        filtered = filtered.tail(periods[selected])

    if filtered.empty:
        st.warning("No candles available.")
        return

    latest = filtered.iloc[-1]

    # ==========================================
    # KPI Cards
    # ==========================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Open",
            f"${latest['open_price']:.2f}",
            "🟢"
        )

    with c2:
        metric_card(
            "High",
            f"${latest['high_price']:.2f}",
            "📈"
        )

    with c3:
        metric_card(
            "Low",
            f"${latest['low_price']:.2f}",
            "📉"
        )

    with c4:
        metric_card(
            "Close",
            f"${latest['close_price']:.2f}",
            "💰"
        )

    st.info(
        f"Latest Candle: {latest['window_start']}"
    )

    st.divider()

    # ==========================================
    # Candlestick Chart
    # ==========================================

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

        title=f"{symbol} OHLC",

        template="plotly_dark",

        height=650,

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

    # ==========================================
    # Volume Chart
    # ==========================================

    st.subheader("📦 Trading Volume")

    volume_fig = go.Figure()

    volume_fig.add_trace(

        go.Bar(

            x=filtered["window_start"],

            y=filtered["total_volume"],

            marker_color="#58A6FF",

            name="Volume"

        )

    )

    volume_fig.update_layout(

        template="plotly_dark",

        height=300,

        xaxis_title="Time",

        yaxis_title="Volume",

        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        )

    )

    st.plotly_chart(
        volume_fig,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

    st.divider()

    # ==========================================
    # Statistics
    # ==========================================

    st.subheader("📊 Statistics")

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "Highest High",
            f"${filtered['high_price'].max():.2f}"
        )

    with s2:
        st.metric(
            "Lowest Low",
            f"${filtered['low_price'].min():.2f}"
        )

    with s3:
        st.metric(
            "Average Volume",
            f"{int(filtered['total_volume'].mean()):,}"
        )

    st.divider()

    # ==========================================
    # Raw Data
    # ==========================================

    with st.expander("📋 View OHLC Data"):

        display = filtered.rename(
            columns={
                "window_start": "Start",
                "window_end": "End",
                "stock_symbol": "Symbol",
                "open_price": "Open",
                "high_price": "High",
                "low_price": "Low",
                "close_price": "Close",
                "total_volume": "Volume"
            }
        )

        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True
        )
    
    render_notifications()