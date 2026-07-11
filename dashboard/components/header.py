import streamlit as st
from datetime import datetime

from notifications import notification_badge
from health import pipeline_summary


def render():
    try:
        pipeline = pipeline_summary()
        healthy  = pipeline["healthy"]
        total    = pipeline["total"]
        pct      = pipeline["health_percentage"]
    except Exception:
        healthy = total = pct = 0

    try:
        badge = notification_badge()
        n_err  = badge["errors"]
        n_warn = badge["warnings"]
    except Exception:
        n_err = n_warn = 0

    if pct == 100:
        health_color = "#00E676"
        health_label = "✅ Healthy"
    elif pct >= 70:
        health_color = "#FACC15"
        health_label = "⚠ Degraded"
    else:
        health_color = "#FF5252"
        health_label = "❌ Critical"

    alert_html = ""
    if n_err > 0:
        alert_html += f'<span style="background:rgba(255,82,82,0.15);color:#FF5252;border:1px solid rgba(255,82,82,0.3);border-radius:8px;padding:2px 10px;font-size:0.75rem;font-weight:700;">🚨 {n_err} Error{"s" if n_err > 1 else ""}</span> '
    if n_warn > 0:
        alert_html += f'<span style="background:rgba(250,204,21,0.15);color:#FACC15;border:1px solid rgba(250,204,21,0.3);border-radius:8px;padding:2px 10px;font-size:0.75rem;font-weight:700;">⚠ {n_warn} Warning{"s" if n_warn > 1 else ""}</span>'

    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    st.markdown(
        f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
            padding:12px 0 8px;border-bottom:1px solid #30363D;margin-bottom:16px;">
            <div>
                <div class="dashboard-title">Stock Analytics Dashboard</div>
                <div class="dashboard-subtitle">Real-Time Market Intelligence Platform</div>
            </div>
            <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
                {alert_html}
                <span style="background:rgba(22,27,34,0.9);border:1px solid #30363D;border-radius:10px;
                    padding:6px 14px;font-size:0.8rem;font-weight:700;color:{health_color};">
                    {health_label} &nbsp;{healthy}/{total}
                </span>
                <span style="color:#8B949E;font-size:0.78rem;">🕒 {now}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )