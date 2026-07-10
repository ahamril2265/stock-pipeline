import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from performance_metrics import (
    pipeline_performance,
    resource_performance,
    stage_throughput,
    pipeline_latency,
    availability,
    recovery_metrics,
    trend,
    benchmark_score
)

from components.cards import metric_card


def line_chart(title, x, y, ylabel):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(width=3),
            fill="tozeroy"
        )
    )

    fig.update_layout(
        title=title,
        template="plotly_dark",
        height=350,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        xaxis_title="Time",
        yaxis_title=ylabel
    )

    return fig


def render():

    st.title("📊 Performance Benchmark")

    st.caption(
        "Performance analysis of the real-time stock analytics pipeline"
    )

    # =====================================================
    # Load Metrics
    # =====================================================

    performance = pipeline_performance()

    resources = resource_performance()

    throughput = stage_throughput()

    latency = pipeline_latency()

    recovery = recovery_metrics()

    uptime = availability()

    trends = trend()

    score = benchmark_score()

    # =====================================================
    # Executive KPIs
    # =====================================================

    st.subheader("📈 Executive Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Throughput",
            f"{performance['throughput']:,} msg/s",
            "🚀"
        )

    with c2:
        metric_card(
            "Latency",
            f"{performance['latency']:.2f} ms",
            "⚡"
        )

    with c3:
        metric_card(
            "Availability",
            f"{performance['availability']}%",
            "🟢"
        )

    with c4:
        metric_card(
            "Recovery",
            f"{performance['recovery']:.2f} sec",
            "♻️"
        )

    st.divider()

    # =====================================================
    # Benchmark Score
    # =====================================================

    st.subheader("🏆 Pipeline Score")

    left, right = st.columns([1, 2])

    with left:

        st.metric(
            "Score",
            f"{score['score']}/100"
        )

        st.metric(
            "Rating",
            score["rating"]
        )

        st.success(score["stars"])

    with right:

        st.progress(score["score"] / 100)

        st.info(
            f"""
Generated

{score['generated'].strftime('%d %b %Y %H:%M:%S')}
"""
        )

    st.divider()

    # =====================================================
    # Resource Utilization
    # =====================================================

    st.subheader("💻 Resource Usage")

    r1, r2, r3 = st.columns(3)

    with r1:

        st.metric(
            "CPU",
            f"{resources['cpu']}%"
        )

        st.progress(resources["cpu"] / 100)

    with r2:

        st.metric(
            "Memory",
            f"{resources['memory']}%"
        )

        st.progress(resources["memory"] / 100)

    with r3:

        st.metric(
            "Disk",
            f"{resources['disk']}%"
        )

        st.progress(resources["disk"] / 100)

    st.divider()

    # =====================================================
    # Charts
    # =====================================================

    st.subheader("📈 Performance Trends")

    left, right = st.columns(2)

    with left:

        st.plotly_chart(
            line_chart(
                "Pipeline Throughput",
                trends["time"],
                trends["throughput"],
                "Messages/sec"
            ),
            use_container_width=True
        )

    with right:

        st.plotly_chart(
            line_chart(
                "Pipeline Latency",
                trends["time"],
                trends["latency"],
                "Latency (ms)"
            ),
            use_container_width=True
        )

    left, right = st.columns(2)

    with left:

        st.plotly_chart(
            line_chart(
                "CPU Utilization",
                trends["time"],
                trends["cpu"],
                "%"
            ),
            use_container_width=True
        )

    with right:

        st.plotly_chart(
            line_chart(
                "Recovery Time",
                trends["time"],
                trends["recovery"],
                "Seconds"
            ),
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # Stage Throughput
    # =====================================================

    st.subheader("🚀 Stage Throughput")

    throughput_df = pd.DataFrame({

        "Stage": throughput.keys(),

        "Messages/sec": throughput.values()

    })

    st.bar_chart(
        throughput_df,
        x="Stage",
        y="Messages/sec",
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # Pipeline Latency
    # =====================================================

    st.subheader("⚡ Stage Latency")

    latency_df = pd.DataFrame({

        "Stage": latency.keys(),

        "Latency (ms)": latency.values()

    })

    st.dataframe(
        latency_df,
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # Availability
    # =====================================================

    st.subheader("🟢 Service Availability")

    availability_df = pd.DataFrame({

        "Service": uptime.keys(),

        "Availability (%)": uptime.values()

    })

    st.dataframe(
        availability_df,
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # Recovery Statistics
    # =====================================================

    st.subheader("♻️ Recovery Statistics")

    a, b, c, d = st.columns(4)

    with a:
        st.metric(
            "Avg Recovery",
            f"{recovery['avg_recovery']} sec"
        )

    with b:
        st.metric(
            "Max Recovery",
            f"{recovery['max_recovery']} sec"
        )

    with c:
        st.metric(
            "Successful Retries",
            recovery["successful_retries"]
        )

    with d:
        st.metric(
            "Failed Retries",
            recovery["failed_retries"]
        )

    st.divider()

    # =====================================================
    # Summary
    # =====================================================

    if score["score"] >= 90:

        st.success(
            "✅ Pipeline performance is excellent."
        )

    elif score["score"] >= 75:

        st.warning(
            "⚠ Pipeline is healthy but has room for optimization."
        )

    else:

        st.error(
            "❌ Pipeline requires optimization."
        )