import streamlit as st
from db import get_symbol_summary, get_ohlc_for_symbol, get_ohlc
from components.cards import metric_card, section_header, page_title
from components.charts import candlestick_chart
from formatter import price, number
from config import PLOTLY_CONFIG

def render():
    page_title("🔍 Symbol Analysis", "Per-Symbol Deep Dive")

    summary_df = get_symbol_summary()
    if summary_df.empty:
        st.warning("⏳ No symbol data yet.")
        return

    symbols = sorted(summary_df["stock_symbol"].tolist())
    selected = st.selectbox("🔍 Select Symbol", symbols)

    detail_df = summary_df[summary_df["stock_symbol"] == selected]
    ohlc_df   = get_ohlc_for_symbol(selected)

    if detail_df.empty:
        st.warning(f"No data for {selected}.")
        return

    row = detail_df.iloc[0]
    st.divider()

    # ── KPI Cards ─────────────────────────────────────────
    section_header(f"📊 {selected} — Market Stats")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("Latest Price",  price(row["latest_price"]),  "💰", color="primary")
    with k2:
        metric_card("Daily Volume",  number(row["daily_volume"]), "📊", color="success")
    with k3:
        metric_card("VWAP",          price(row["vwap"]),          "💹", color="primary")
    with k4:
        metric_card("Avg Spread",    f'{row["avg_spread"]:.4f}',  "↔", color="warning")

    st.write("")
    k5, k6, k7 = st.columns(3)
    with k5:
        metric_card("Buy Volume",  number(row["buy_volume"]),  "🟢", color="success")
    with k6:
        metric_card("Sell Volume", number(row["sell_volume"]), "🔴", color="error")
    with k7:
        buy_pct = row["buy_volume"] / (row["buy_volume"] + row["sell_volume"]) * 100 if (row["buy_volume"] + row["sell_volume"]) > 0 else 0
        metric_card("Buy Ratio", f"{buy_pct:.1f}%", "⚖", color="success" if buy_pct > 50 else "error")

    st.divider()

    # ── OHLC Chart ────────────────────────────────────────
    section_header(f"🕯 OHLC Candlestick — {selected}")
    if not ohlc_df.empty:
        st.plotly_chart(
            candlestick_chart(ohlc_df, symbol=selected),
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )
    else:
        st.info("No OHLC data available for this symbol yet.")

    st.divider()

    # ── OHLC Summary Table ────────────────────────────────
    if not ohlc_df.empty:
        section_header("📋 OHLC Window Details")
        display = ohlc_df[[
            "window_start","window_end","open_price","high_price",
            "low_price","close_price","total_volume"
        ]].sort_values("window_start", ascending=False).head(20)
        display.columns = ["Start","End","Open","High","Low","Close","Volume"]
        st.dataframe(display, hide_index=True, use_container_width=True)

    # ── Raw Symbol Summary ─────────────────────────────────
    with st.expander("🔍 Raw Symbol Summary"):
        st.dataframe(detail_df, hide_index=True, use_container_width=True)