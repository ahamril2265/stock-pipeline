import streamlit as st
from db import get_ohlc, get_symbol_summary
from components.cards import metric_card, section_header, page_title
from components.charts import candlestick_chart
from formatter import price, number
from config import PLOTLY_CONFIG

def render():
    page_title("🕯 OHLC View", "Candlestick Charts — All Symbols")

    ohlc_df = get_ohlc()
    if ohlc_df.empty:
        st.warning("⏳ No OHLC data yet.")
        return

    symbols = sorted(ohlc_df["stock_symbol"].unique().tolist())

    # ── Filters ───────────────────────────────────────────
    col1, col2 = st.columns([3, 2])
    with col1:
        selected_symbols = st.multiselect("Filter Symbols", symbols, default=symbols[:min(4, len(symbols))])
    with col2:
        col_count = st.radio("Grid Columns", [1, 2], index=1, horizontal=True)

    if not selected_symbols:
        selected_symbols = symbols

    st.divider()

    # ── OHLC Summary Table ─────────────────────────────────
    section_header("📋 OHLC Summary — All Symbols")
    summary = ohlc_df.groupby("stock_symbol", as_index=False).agg(
        Open  = ("open_price",  "first"),
        High  = ("high_price",  "max"),
        Low   = ("low_price",   "min"),
        Close = ("close_price", "last"),
        Volume= ("total_volume","sum"),
    )
    summary["Change %"] = ((summary["Close"] - summary["Open"]) / summary["Open"] * 100).round(2).astype(str) + "%"
    st.dataframe(summary, hide_index=True, use_container_width=True)

    st.divider()

    # ── Candlestick Grid ──────────────────────────────────
    section_header("🕯 Individual Candlestick Charts")

    if col_count == 2:
        pairs = [(selected_symbols[i], selected_symbols[i+1] if i+1 < len(selected_symbols) else None)
                 for i in range(0, len(selected_symbols), 2)]
        for sym_a, sym_b in pairs:
            l, r = st.columns(2)
            with l:
                df_a = ohlc_df[ohlc_df["stock_symbol"] == sym_a].sort_values("window_start")
                if not df_a.empty:
                    st.plotly_chart(candlestick_chart(df_a, symbol=sym_a), use_container_width=True, config=PLOTLY_CONFIG)
            if sym_b:
                with r:
                    df_b = ohlc_df[ohlc_df["stock_symbol"] == sym_b].sort_values("window_start")
                    if not df_b.empty:
                        st.plotly_chart(candlestick_chart(df_b, symbol=sym_b), use_container_width=True, config=PLOTLY_CONFIG)
    else:
        for sym in selected_symbols:
            df_s = ohlc_df[ohlc_df["stock_symbol"] == sym].sort_values("window_start")
            if not df_s.empty:
                st.plotly_chart(candlestick_chart(df_s, symbol=sym), use_container_width=True, config=PLOTLY_CONFIG)