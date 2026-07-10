import streamlit as st
import plotly.express as px

from db import get_top_symbols
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

    st.title("🏆 Top Symbols")
    st.caption("Market leaders ranked by trading volume")

    # ==================================================
    # Load Data
    # ==================================================

    df = get_top_symbols()

    if df.empty:
        st.warning("No Top Symbols data available.")
        return

    df = df.sort_values("volume_rank")

    # ==================================================
    # KPI Cards
    # ==================================================

    st.subheader("📊 Market Leaders")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Tracked Symbols",
            len(df),
            "📈"
        )

    with c2:
        metric_card(
            "Highest Volume",
            f"{int(df['total_volume'].max()):,}",
            "📊"
        )

    with c3:
        metric_card(
            "Highest VWAP",
            f"${df['vwap'].max():.2f}",
            "💰"
        )

    st.divider()

    # ==================================================
    # Filters
    # ==================================================

    st.subheader("🔍 Filters")

    f1, f2, f3 = st.columns(3)

    with f1:

        search = st.text_input(
            "Search Symbol"
        )

    with f2:

        sort_by = st.selectbox(
            "Sort By",
            [
                "Volume",
                "VWAP",
                "Price"
            ]
        )

    with f3:

        min_volume = st.slider(
            "Minimum Volume",
            0,
            int(df["total_volume"].max()),
            0
        )

    # ==================================================
    # Apply Filters
    # ==================================================

    filtered = df.copy()

    if search:

        filtered = filtered[
            filtered["stock_symbol"]
            .str.contains(
                search.upper(),
                case=False,
                na=False
            )
        ]

    filtered = filtered[
        filtered["total_volume"] >= min_volume
    ]

    mapping = {
        "Volume": "total_volume",
        "VWAP": "vwap",
        "Price": "latest_price"
    }

    filtered = filtered.sort_values(
        mapping[sort_by],
        ascending=False
    )

    if filtered.empty:
        st.warning("No symbols match the selected filters.")
        return

    st.info(f"Displaying {len(filtered)} symbol(s)")

    st.divider()

    # ==================================================
    # Charts
    # ==================================================

    left, right = st.columns(2)

    with left:

        bar = px.bar(

            filtered,

            x="total_volume",

            y="stock_symbol",

            orientation="h",

            color="total_volume",

            color_continuous_scale="Viridis",

            text="total_volume",

            template="plotly_dark"

        )

        bar.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )

        bar.update_layout(

            title="Trading Volume",

            xaxis_title="Volume",

            yaxis_title="",

            height=500

        )

        st.plotly_chart(
            bar,
            use_container_width=True,
            config=PLOTLY_CONFIG
        )

    with right:

        pie = px.pie(

            filtered,

            names="stock_symbol",

            values="total_volume",

            hole=0.55,

            template="plotly_dark"

        )

        pie.update_layout(
            title="Market Share",
            height=500
        )

        st.plotly_chart(
            pie,
            use_container_width=True,
            config=PLOTLY_CONFIG
        )

    st.divider()

    # ==================================================
    # VWAP Comparison
    # ==================================================

    st.subheader("💰 VWAP Comparison")

    vwap = px.bar(

        filtered,

        x="stock_symbol",

        y="vwap",

        color="vwap",

        color_continuous_scale="Blues",

        text="vwap",

        template="plotly_dark"

    )

    vwap.update_traces(
        texttemplate="$%{text:.2f}",
        textposition="outside"
    )

    vwap.update_layout(

        height=420,

        xaxis_title="",

        yaxis_title="VWAP ($)"

    )

    st.plotly_chart(
        vwap,
        use_container_width=True,
        config=PLOTLY_CONFIG
    )

    st.divider()

    # ==================================================
    # Summary Statistics
    # ==================================================

    st.subheader("📊 Summary")

    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric(
            "Average Price",
            f"${filtered['latest_price'].mean():.2f}"
        )

    with s2:
        st.metric(
            "Average VWAP",
            f"${filtered['vwap'].mean():.2f}"
        )

    with s3:
        st.metric(
            "Total Volume",
            f"{int(filtered['total_volume'].sum()):,}"
        )

    st.divider()

    # ==================================================
    # Leaderboard
    # ==================================================

    st.subheader("🏅 Leaderboard")

    leaderboard = filtered[
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
            "latest_price": "Latest Price",
            "total_volume": "Total Volume",
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

    # ==================================================
    # Raw Data
    # ==================================================

    with st.expander("📄 View Raw Dataset"):

        st.dataframe(
            filtered,
            hide_index=True,
            use_container_width=True
        )
    
    render_notifications()