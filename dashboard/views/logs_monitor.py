import streamlit as st
import pandas as pd
from log_metrics import containers, logs
from components.cards import section_header, metric_card, page_title

LEVEL_COLORS = {
    "ERROR":   "#FF5252",
    "WARNING": "#FACC15",
    "SUCCESS": "#00E676",
    "INFO":    "#8B949E",
}

def render():
    page_title("📜 Live Logs", "Container Log Feed — Real-time")

    # ── Filters ───────────────────────────────────────────
    container_list = containers()
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        service = st.selectbox("📦 Service", container_list)
    with col2:
        level_filter = st.multiselect(
            "🎚 Log Level",
            ["INFO", "WARNING", "ERROR", "SUCCESS"],
            default=["INFO", "WARNING", "ERROR", "SUCCESS"],
        )
    with col3:
        lines = st.number_input("Lines", min_value=10, max_value=200, value=50, step=10)

    if st.button("🔄 Refresh Logs", type="primary"):
        st.cache_data.clear()

    st.divider()

    # ── Fetch & Parse ─────────────────────────────────────
    from log_metrics import CONTAINERS, container_logs, parse_logs
    raw  = container_logs(CONTAINERS.get(service, service), lines=int(lines))
    data = parse_logs(raw)
    df   = pd.DataFrame(data)

    if df.empty:
        st.info("No log entries found.")
        return

    # ── Stats ─────────────────────────────────────────────
    section_header(f"📊 Log Summary — {service}")
    counts = df["Level"].value_counts().to_dict()
    k1, k2, k3, k4 = st.columns(4)
    with k1: metric_card("Total Lines", str(len(df)),             "📜")
    with k2: metric_card("Errors",   str(counts.get("ERROR",0)), "🔴", color="error"   if counts.get("ERROR",0)   else "primary")
    with k3: metric_card("Warnings", str(counts.get("WARNING",0)),"⚠", color="warning" if counts.get("WARNING",0) else "primary")
    with k4: metric_card("Info",     str(counts.get("INFO",0)),   "ℹ")

    st.divider()

    # ── Filtered Table ────────────────────────────────────
    section_header("📋 Log Entries")
    filtered = df[df["Level"].isin(level_filter)] if level_filter else df

    def colorize_row(row):
        color = LEVEL_COLORS.get(row["Level"], "#8B949E")
        return [f"color: {color}"] * len(row)

    st.dataframe(
        filtered.style.apply(colorize_row, axis=1),
        hide_index=True,
        use_container_width=True,
        height=500,
    )