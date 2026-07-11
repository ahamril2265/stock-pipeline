import streamlit as st
from db import get_market_kpis, get_top_symbols, get_ohlc
from components.cards import metric_card, section_header, page_title
from components.charts import top_symbols_chart, buy_sell_chart, volume_timeline
from formatter import number, price, latency, percent
from notifications import render_notifications
from config import PLOTLY_CONFIG

def render():
    page_title("📈 Market Overview", "Real-Time Market Summary • Auto-Refresh: 30s")

    # ── Data ──────────────────────────────────────────────
    market_df  = get_market_kpis()
    top_df     = get_top_symbols()
    ohlc_df    = get_ohlc()

    if market_df.empty:
        st.warning("⏳ No market KPI data yet. The pipeline may still be warming up.")
        return

    row = market_df.iloc[0]

    # ── Top KPIs ──────────────────────────────────────────
    st.write("")
    section_header("📊 Market KPIs")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Market Volume",    number(row["total_market_volume"]),  "📊", color="primary")
    with c2:
        metric_card("Active Symbols",   number(row["active_symbols"]),       "📈", color="success")
    with c3:
        metric_card("Market VWAP",      price(row["market_vwap"]),           "💰", color="accent" if False else "primary")
    with c4:
        metric_card("Avg Latency",      latency(row["avg_market_latency"]),  "⚡", color="warning" if row["avg_market_latency"] > 25 else "success")

    st.write("")
    c5, c6, c7 = st.columns(3)
    with c5:
        metric_card("Buy Volume",  number(row["total_buy_volume"]),  "🟢", color="success")
    with c6:
        metric_card("Sell Volume", number(row["total_sell_volume"]), "🔴", color="error")
    with c7:
        metric_card("Avg Price",   price(row["avg_market_price"]),  "💵", color="primary")

    st.markdown(
        f'<div style="color:#8B949E;font-size:0.78rem;margin-top:4px;">🕒 Last Updated: {row["updated_at"]}</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Charts ────────────────────────────────────────────
    section_header("📊 Market Analytics")
    left, right = st.columns(2)

    if not top_df.empty:
        with left:
            st.plotly_chart(top_symbols_chart(top_df), use_container_width=True, config=PLOTLY_CONFIG)
    else:
        with left:
            st.info("Top symbols data not yet available.")

    with right:
        st.plotly_chart(buy_sell_chart(market_df), use_container_width=True, config=PLOTLY_CONFIG)

    if not ohlc_df.empty:
        st.divider()
        section_header("📈 Volume Timeline (OHLC windows)")
        timeline_df = ohlc_df.groupby("window_start", as_index=False)["total_volume"].sum()
        st.plotly_chart(volume_timeline(timeline_df), use_container_width=True, config=PLOTLY_CONFIG)

    st.divider()

    # ── Leaderboard ───────────────────────────────────────
    section_header("🏆 Market Leaderboard")

    if not top_df.empty:
        lb = top_df[["volume_rank","stock_symbol","latest_price","total_volume","buy_volume","sell_volume","vwap"]].copy()
        lb.columns = ["Rank","Symbol","Price","Volume","Buy Vol","Sell Vol","VWAP"]
        lb["Buy %"]  = (lb["Buy Vol"]  / lb["Volume"] * 100).round(1).astype(str) + "%"
        lb["Sell %"] = (lb["Sell Vol"] / lb["Volume"] * 100).round(1).astype(str) + "%"
        st.dataframe(lb, hide_index=True, use_container_width=True)
    else:
        st.info("Leaderboard data not yet available.")

    # ── Activity Feed ─────────────────────────────────────
    if not ohlc_df.empty:
        st.divider()
        section_header("🔴 Live Activity Feed (Recent OHLC Windows)")
        feed = ohlc_df.sort_values("window_start", ascending=False).head(10)[
            ["window_start","stock_symbol","open_price","high_price","low_price","close_price","total_volume"]
        ].rename(columns={
            "window_start":"Time","stock_symbol":"Symbol",
            "open_price":"Open","high_price":"High","low_price":"Low",
            "close_price":"Close","total_volume":"Volume",
        })
        st.dataframe(feed, hide_index=True, use_container_width=True)

    st.divider()
    render_notifications()
    st.markdown("</div>", unsafe_allow_html=True)