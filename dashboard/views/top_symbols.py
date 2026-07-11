import streamlit as st
from db import get_top_symbols, get_symbol_summary
from components.cards import metric_card, section_header, page_title
from components.charts import top_symbols_chart, vwap_chart, market_share_chart
from formatter import number, price
from config import PLOTLY_CONFIG

def render():
    page_title("🏆 Top Symbols", "Volume-Ranked Market Leaders")

    top_df = get_top_symbols()
    if top_df.empty:
        st.warning("⏳ No top symbols data yet.")
        return

    # ── Filters ───────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([3, 2, 2])
    with col_f1:
        search = st.text_input("🔍 Search symbol", placeholder="e.g. AAPL")
    with col_f2:
        if len(top_df) > 5:
            top_n = st.slider("Top N symbols", min_value=5, max_value=len(top_df), value=min(10, len(top_df)), step=5)
        else:
            top_n = len(top_df)
            st.info(f"Showing all {top_n} symbols")
    with col_f3:
        sort_by = st.selectbox("Sort by", ["Volume", "VWAP", "Buy Volume", "Sell Volume"], index=0)

    sort_col_map = {"Volume": "total_volume", "VWAP": "vwap", "Buy Volume": "buy_volume", "Sell Volume": "sell_volume"}
    sort_col = sort_col_map[sort_by]

    filtered = top_df.copy()
    if search:
        filtered = filtered[filtered["stock_symbol"].str.upper().str.contains(search.upper())]
    filtered = filtered.sort_values(sort_col, ascending=False).head(top_n)

    st.divider()

    # ── Summary KPIs ─────────────────────────────────────
    section_header("📊 Summary")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("Symbols", number(len(top_df)), "📈")
    with k2:
        metric_card("Total Volume", number(int(top_df["total_volume"].sum())), "📊")
    with k3:
        top_sym = top_df.iloc[0]["stock_symbol"] if not top_df.empty else "—"
        metric_card("Top Symbol", top_sym, "🥇", color="success")
    with k4:
        avg_vwap = round(top_df["vwap"].mean(), 2)
        metric_card("Avg VWAP", price(avg_vwap), "💰")

    st.divider()

    # ── Charts ────────────────────────────────────────────
    section_header("📊 Visual Analysis")
    l, r = st.columns(2)
    with l:
        st.plotly_chart(top_symbols_chart(filtered, n=top_n), use_container_width=True, config=PLOTLY_CONFIG)
    with r:
        st.plotly_chart(market_share_chart(filtered), use_container_width=True, config=PLOTLY_CONFIG)

    st.divider()
    section_header("💰 VWAP Comparison")
    st.plotly_chart(vwap_chart(filtered), use_container_width=True, config=PLOTLY_CONFIG)

    st.divider()

    # ── Ranked Table ─────────────────────────────────────
    section_header("📋 Ranked Table")
    table = filtered[[
        "volume_rank","stock_symbol","latest_price","total_volume",
        "buy_volume","sell_volume","vwap","updated_at"
    ]].copy()

    table["Buy %"]  = (table["buy_volume"]  / table["total_volume"] * 100).round(1).astype(str) + "%"
    table["Sell %"] = (table["sell_volume"] / table["total_volume"] * 100).round(1).astype(str) + "%"
    table.rename(columns={
        "volume_rank": "Rank", "stock_symbol": "Symbol",
        "latest_price": "Price", "total_volume": "Volume",
        "buy_volume": "Buy Vol", "sell_volume": "Sell Vol",
        "vwap": "VWAP", "updated_at": "Updated",
    }, inplace=True)

    st.dataframe(table, hide_index=True, use_container_width=True)