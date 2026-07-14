import streamlit as st
from datetime import datetime

from health import all_services, pipeline_summary


PAGES = {
    "📊 Market": [
        "📈 Market Overview",
        "🏆 Top Symbols",
        "🔍 Symbol Analysis",
        "🕯 OHLC",
    ],
    "🔬 Infrastructure": [
        "⚙ Pipeline Health",
        "⚡ Spark Cluster",
        "🌬 Airflow Monitor",
        "📨 Kafka Cluster",
        "💾 Storage Monitor",
        "📜 Live Logs",
    ],
    "⚙ Operations": [
        "🏗 Architecture",
        "📊 Performance Benchmark",
        "🛡 Failure Recovery",
        "🚨 Incident & Recovery Center",
    ],
}


def render():
    # --------------------------------------------------
    # Branding
    # --------------------------------------------------
    st.sidebar.markdown(
        """
        <div style="padding:8px 0 4px;">
            <div style="font-size:1.5rem;font-weight:800;background:linear-gradient(135deg,#58A6FF,#7C3AED);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                📈 Stock Analytics
            </div>
            <div style="color:#8B949E;font-size:0.78rem;margin-top:2px;">Real-Time Market Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    # --------------------------------------------------
    # Live service health
    # --------------------------------------------------
    try:
        services = all_services()
        pipeline = pipeline_summary()
        healthy  = pipeline["healthy"]
        total    = pipeline["total"]
    except Exception:
        services = {}
        healthy  = 0
        total    = 0

    if total > 0:
        pct = healthy / total
        badge_color = "#00E676" if pct == 1.0 else ("#FACC15" if pct >= 0.7 else "#FF5252")
        st.sidebar.markdown(
            f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                background:rgba(22,27,34,0.8);border:1px solid #30363D;border-radius:10px;
                padding:8px 12px;margin-bottom:10px;">
                <span style="font-size:0.82rem;color:#8B949E;font-weight:500;">Pipeline Status</span>
                <span style="font-size:0.82rem;font-weight:700;color:{badge_color};">
                    {healthy}/{total} Online
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Service pills
    with st.sidebar.expander("🔌 Service Status", expanded=False):
        for service, ok in services.items():
            dot   = "dot-online"  if ok else "dot-offline"
            pill  = "status-online" if ok else "status-offline"
            label = "ONLINE"      if ok else "OFFLINE"
            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:5px 0;border-bottom:1px solid #21262D;">
                    <span style="font-size:0.82rem;">{service}</span>
                    <span class="status-pill {pill}">
                        <span class="status-dot {dot}"></span>{label}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.sidebar.divider()

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------
    all_pages = []
    for group, pages in PAGES.items():
        st.sidebar.markdown(
            f'<div style="font-size:0.7rem;font-weight:700;color:#8B949E;text-transform:uppercase;'
            f'letter-spacing:1px;padding:6px 0 2px;">{group}</div>',
            unsafe_allow_html=True,
        )
        for p in pages:
            all_pages.append(p)

    page = st.sidebar.radio(
        "Navigation",
        options=[p for group in PAGES.values() for p in group],
        label_visibility="collapsed",
    )

    st.sidebar.divider()

    # --------------------------------------------------
    # Footer
    # --------------------------------------------------
    now = datetime.now().strftime("%H:%M:%S")
    st.sidebar.markdown(
        f"""
        <div style="font-size:0.73rem;color:#8B949E;text-align:center;padding:4px 0;">
            <div>🔄 Auto-refresh every 30s</div>
            <div style="margin-top:3px;">🕒 Last loaded: {now}</div>
            <div style="margin-top:8px;font-weight:600;color:#58A6FF;">Ahamed Rilwan</div>
            <div style="font-size:0.68rem;color:#8B949E;">v2.0.0</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return page