import streamlit as st
from performance_metrics import (
    benchmark_score, pipeline_performance, resource_performance,
    stage_throughput, pipeline_latency, availability,
)
from components.cards import metric_card, score_card, section_header, page_title
from components.charts import radar_chart, stage_throughput_chart, gauge_chart
from config import PLOTLY_CONFIG

def render():
    page_title("📊 Performance Benchmark", "System Performance Analysis & Scoring")

    bscore  = benchmark_score()
    perf    = pipeline_performance()
    res     = resource_performance()
    stages  = stage_throughput()
    latency = pipeline_latency()
    avail   = availability()

    st.divider()

    # ── Benchmark Score ───────────────────────────────────
    col_score, col_metrics = st.columns([1, 2])
    with col_score:
        section_header("🏆 Benchmark Score")
        score_card(bscore["score"], bscore["rating"], bscore["stars"])
        st.markdown(
            f'<div style="color:#8B949E;font-size:0.75rem;text-align:center;margin-top:6px;">'
            f'Generated: {bscore["generated"].strftime("%H:%M:%S")}</div>',
            unsafe_allow_html=True,
        )

    with col_metrics:
        section_header("⚡ Pipeline KPIs")
        k1, k2 = st.columns(2)
        with k1:
            metric_card("Throughput",   f'{perf["throughput"]:,}',   "📊")
            metric_card("CPU Usage",    f'{res["cpu"]}%',             "🖥",
                        color="warning" if res["cpu"] > 80 else "primary")
        with k2:
            metric_card("Avg Latency",  f'{perf["latency"]} ms',     "⚡",
                        color="warning" if perf["latency"] > 25 else "success")
            metric_card("Disk Usage",   f'{res["disk"]}%',            "💾",
                        color="warning" if res["disk"] > 80 else "primary")

    st.divider()

    # ── Radar Chart ───────────────────────────────────────
    section_header("🕸 Performance Radar")
    radar_cats = ["CPU", "Memory", "Disk", "Throughput", "Latency Score", "Recovery"]
    cpu_score     = max(0, 100 - res["cpu"])
    mem_score     = max(0, 100 - res["memory"])
    disk_score    = max(0, 100 - res["disk"])
    tput_score    = min(100, perf["throughput"] / 1000)
    lat_score     = max(0, 100 - perf["latency"] * 2)
    recovery_score= max(0, 100 - perf.get("recovery", 0) * 10)
    radar_vals = [cpu_score, mem_score, disk_score, tput_score, lat_score, recovery_score]
    st.plotly_chart(radar_chart(radar_cats, radar_vals, "System Performance Radar"), use_container_width=True, config=PLOTLY_CONFIG)

    st.divider()

    # ── Stage Throughput ─────────────────────────────────
    section_header("📈 Pipeline Stage Throughput")
    st.plotly_chart(stage_throughput_chart(stages), use_container_width=True, config=PLOTLY_CONFIG)

    st.divider()

    # ── Latency Breakdown ─────────────────────────────────
    section_header("⏱ Pipeline Latency Breakdown (ms)")
    cols = st.columns(len(latency))
    for col, (stage, ms) in zip(cols, latency.items()):
        with col:
            metric_card(stage, f"{ms} ms", "⚡", color="success" if ms < 10 else "warning")

    st.divider()

    # ── Service Availability ──────────────────────────────
    section_header("✅ Service Availability")
    import pandas as pd
    avail_df = pd.DataFrame([
        {"Service": svc, "Availability": f"{pct}%", "Status": "🟢 Online" if pct == 100 else "🔴 Offline"}
        for svc, pct in avail.items()
    ])
    st.dataframe(avail_df, hide_index=True, use_container_width=True)