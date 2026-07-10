import streamlit as st

from components.cards import metric_card

from recovery import (
    get_recovery_metrics,
    bronze_status,
    silver_status,
    gold_status,
    pipeline_flow,
    failure_events,
    recovery_statistics,
    alerts
)

from components.pipeline_flow import render as pipeline_flow_chart
from notifications import render_notifications


def stage_icon(status):

    return "🟢" if status else "🔴"


def render():

    

    st.title("🛡 Failure Recovery")

    st.caption(
        "Monitoring pipeline resilience, retries and recovery operations."
    )

    # ==========================================================
    # Load Data
    # ==========================================================

    metrics = get_recovery_metrics()

    bronze = bronze_status()

    silver = silver_status()

    gold = gold_status()

    recovery = recovery_statistics()

    flow = pipeline_flow()

    events = failure_events()

    active_alerts = alerts()

    # ==========================================================
    # Recovery KPIs
    # ==========================================================

    st.subheader("📊 Recovery Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        metric_card(
            "Recovered",
            metrics["recovered_messages"],
            "♻️"
        )

    with c2:

        metric_card(
            "Retry Queue",
            metrics["retry_queue"],
            "🔁"
        )

    with c3:

        metric_card(
            "Dead Letter Queue",
            metrics["dead_letter_queue"],
            "📦"
        )

    with c4:

        metric_card(
            "Recovery Success",
            f"{metrics['recovery_success']}%",
            "✅"
        )

    st.divider()

    # ==========================================================
    # Pipeline Flow
    # ==========================================================

    pipeline_flow_chart(flow)


    # ==========================================================
    # Layer Status
    # ==========================================================

    left, middle, right = st.columns(3)

    with left:

        st.subheader("🥉 Bronze")

        st.metric(
            "Records",
            bronze["records"]
        )

        st.metric(
            "Latency",
            f"{bronze['latency']} sec"
        )

        st.metric(
            "Quarantined",
            bronze["quarantined"]
        )

        st.metric(
            "Checkpoint",
            "Healthy" if bronze["checkpoint"] else "Failed"
        )

    with middle:

        st.subheader("🥈 Silver")

        st.metric(
            "Processed",
            silver["processed"]
        )

        st.metric(
            "Latency",
            f"{silver['latency']} sec"
        )

        st.metric(
            "Duplicates",
            silver["duplicates"]
        )

        st.metric(
            "Rejected",
            silver["rejected"]
        )

    with right:

        st.subheader("🥇 Gold")

        st.metric(
            "Tables",
            gold["tables"]
        )

        st.metric(
            "Rows",
            gold["rows"]
        )

        st.metric(
            "Failures",
            gold["failures"]
        )

        st.metric(
            "Refresh",
            gold["refresh"].strftime("%H:%M:%S")
        )

    st.divider()

    # ==========================================================
    # Recovery Statistics
    # ==========================================================

    st.subheader("📈 Recovery Statistics")

    s1, s2, s3 = st.columns(3)

    with s1:

        st.metric(
            "Average Recovery",
            f"{recovery['avg_recovery']} sec"
        )

    with s2:

        st.metric(
            "Maximum Recovery",
            f"{recovery['max_recovery']} sec"
        )

    with s3:

        st.metric(
            "Total Recoveries",
            recovery["total_recoveries"]
        )

    st.divider()

    # ==========================================================
    # Retry Statistics
    # ==========================================================

    r1, r2 = st.columns(2)

    with r1:

        st.metric(
            "Successful Retries",
            recovery["successful_retries"]
        )

    with r2:

        st.metric(
            "Failed Retries",
            recovery["failed_retries"]
        )

    st.divider()

    # ==========================================================
    # Failure Timeline
    # ==========================================================

    st.subheader("🕒 Failure Timeline")

    timeline = []

    for event in events:

        timeline.append({

            "Time": event["time"].strftime("%H:%M:%S"),

            "Component": event["component"],

            "Event": event["event"],

            "Status": event["status"]

        })

    st.dataframe(

        timeline,

        hide_index=True,

        use_container_width=True

    )

    st.divider()

    # ==========================================================
    # Active Alerts
    # ==========================================================

    st.subheader("🚨 Active Alerts")

    if active_alerts:

        for alert in active_alerts:

            st.warning(alert)

    else:

        st.success(
            "✅ No active alerts."
        )

    render_notifications()