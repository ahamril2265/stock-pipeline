import streamlit as st
import pandas as pd
from recovery import (
    get_recovery_metrics, bronze_status, silver_status,
    gold_status, pipeline_flow, failure_events, recovery_statistics, alerts,
)
from components.cards import metric_card, status_badge, section_header, page_title

def render():
    page_title("🛡 Failure Recovery", "Pipeline Resilience & Recovery Metrics")

    kpis      = get_recovery_metrics()
    rec_stats = recovery_statistics()
    flow      = pipeline_flow()
    events    = failure_events()
    alert_list= alerts()

    st.divider()

    # ── Recovery KPIs ──────────────────────────────────────
    section_header("📊 Recovery Overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Recovered Messages", str(kpis["recovered_messages"]),  "✅", color="success")
    with c2:
        metric_card("Retry Queue",        str(kpis["retry_queue"]),          "🔁", color="warning" if kpis["retry_queue"] > 0 else "primary")
    with c3:
        metric_card("Dead Letter Queue",  str(kpis["dead_letter_queue"]),    "💀", color="error" if kpis["dead_letter_queue"] > 0 else "primary")
    with c4:
        metric_card("Success Rate",       f'{kpis["recovery_success"]:.1f}%',"📈", color="success" if kpis["recovery_success"] >= 99 else "warning")

    st.write("")
    r1, r2, r3 = st.columns(3)
    with r1:
        metric_card("Avg Recovery Time",  f'{rec_stats["avg_recovery"]:.2f}s', "⏱")
    with r2:
        metric_card("Max Recovery Time",  f'{rec_stats["max_recovery"]:.2f}s', "⏰", color="warning")
    with r3:
        metric_card("Total Recoveries",   str(rec_stats["total_recoveries"]),  "♻")

    st.divider()

    # ── Pipeline Flow Health ───────────────────────────────
    section_header("🔄 Pipeline Stage Status (Live)")
    flow_cols = st.columns(len(flow))
    for col, stage in zip(flow_cols, flow):
        with col:
            healthy = stage["healthy"]
            icon    = "✅" if healthy else "❌"
            color   = "#00E676" if healthy else "#FF5252"
            st.markdown(
                f"""
                <div style="text-align:center;background:rgba(22,27,34,0.85);
                    border:1px solid {'rgba(0,230,118,0.3)' if healthy else 'rgba(255,82,82,0.3)'};
                    border-radius:12px;padding:14px 8px;">
                    <div style="font-size:1.6rem;">{icon}</div>
                    <div style="font-size:0.82rem;font-weight:700;color:{color};margin-top:4px;">{stage['name']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Layer Status ──────────────────────────────────────
    section_header("🗄 Data Layer Status (from ClickHouse)")
    bronze = bronze_status()
    silver = silver_status()
    gold   = gold_status()

    l1, l2, l3 = st.columns(3)
    with l1:
        st.markdown("**🗻 Bronze Layer**")
        metric_card("Records",   str(bronze["records"]),                "📦")
        metric_card("Checkpoint",str("✅" if bronze["checkpoint"] else "❌"), "💾",
                    color="success" if bronze["checkpoint"] else "error")
    with l2:
        st.markdown("**🥈 Silver Layer**")
        metric_card("Processed",  str(silver["processed"]),             "✅")
        metric_card("Duplicates", str(silver["duplicates"]),            "🔁",
                    color="warning" if silver["duplicates"] > 0 else "success")
    with l3:
        st.markdown("**🥇 Gold Layer**")
        metric_card("Tables",     str(gold["tables"]),                  "📋")
        metric_card("Total Rows", str(gold["rows"]),                    "🔢",
                    color="success" if gold["rows"] > 0 else "error")

    st.divider()

    # ── Failure Events ────────────────────────────────────
    section_header("🚨 Active Failure Events")
    if events:
        df = pd.DataFrame(events)
        for _, row in df.iterrows():
            status_color = "#FF5252" if row.get("status") == "OFFLINE" else "#00E676"
            st.markdown(
                f"""
                <div style="background:rgba(255,82,82,0.06);border:1px solid rgba(255,82,82,0.2);
                    border-radius:10px;padding:12px 16px;margin-bottom:8px;
                    display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="font-weight:700;color:#F0F6FC;">{row['component']}</span>
                        <span style="color:#8B949E;margin-left:10px;font-size:0.85rem;">{row['event']}</span>
                    </div>
                    <span style="color:{status_color};font-weight:700;font-size:0.82rem;">{row['status']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("✅ No active failure events.")

    # ── Alerts ────────────────────────────────────────────
    if alert_list:
        st.divider()
        section_header("⚠ System Alerts")
        for alert in alert_list:
            st.warning(alert)