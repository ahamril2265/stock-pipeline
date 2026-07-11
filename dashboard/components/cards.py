import streamlit as st


# ── Color palette ──────────────────────────────────────────────────────────────
_COLORS = {
    "primary": "#58A6FF",
    "success": "#00E676",
    "warning": "#FACC15",
    "error":   "#FF5252",
    "muted":   "#8B949E",
}

# ==========================================================
# Metric Card
# NOTE: HTML must be ONE unbroken string — Streamlit 1.46
# sanitises multi-line HTML and leaks closing </div> tags.
# ==========================================================

def metric_card(title: str, value, icon: str, delta=None, delta_label: str = "", color: str = "primary"):
    accent = _COLORS.get(color, _COLORS["primary"])

    if delta is not None:
        symbol = "▲" if delta >= 0 else "▼"
        dc = _COLORS["success"] if delta >= 0 else _COLORS["error"]
        delta_html = f'<div style="font-size:0.78rem;color:{dc};font-weight:600;margin-top:2px;">{symbol} {abs(delta):.1f}{delta_label}</div>'
    else:
        delta_html = ""

    html = (
        f'<div style="background:rgba(22,27,34,0.9);border:1px solid #30363D;border-radius:14px;'
        f'padding:16px 18px;margin-bottom:4px;box-shadow:0 4px 16px rgba(0,0,0,0.4);">'
        f'<div style="display:flex;align-items:flex-start;gap:12px;">'
        f'<div style="font-size:1.8rem;color:{accent};line-height:1;">{icon}</div>'
        f'<div style="flex:1;">'
        f'<div style="color:#8B949E;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;">{title}</div>'
        f'<div style="font-size:1.6rem;font-weight:700;color:{accent};line-height:1.1;margin-top:2px;">{value}</div>'
        f'{delta_html}'
        f'</div></div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ==========================================================
# Status Badge
# ==========================================================

def status_badge(name: str, healthy: bool, description: str = ""):
    dot_color   = "#00E676" if healthy else "#FF5252"
    pill_bg     = "rgba(0,230,118,0.10)" if healthy else "rgba(255,82,82,0.10)"
    pill_border = "rgba(0,230,118,0.30)" if healthy else "rgba(255,82,82,0.30)"
    pill_color  = "#00E676" if healthy else "#FF5252"
    label       = "ONLINE" if healthy else "OFFLINE"
    desc_html   = f'<div style="font-size:0.74rem;color:#8B949E;margin-top:2px;">{description}</div>' if description else ""

    html = (
        f'<div style="background:rgba(22,27,34,0.85);border:1px solid #30363D;border-radius:12px;'
        f'padding:12px 14px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;">'
        f'<div><div style="font-weight:600;font-size:0.88rem;color:#F0F6FC;">{name}</div>{desc_html}</div>'
        f'<span style="display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:20px;'
        f'font-size:0.74rem;font-weight:700;background:{pill_bg};border:1px solid {pill_border};color:{pill_color};">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:{dot_color};display:inline-block;"></span>'
        f'{label}</span></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ==========================================================
# Score Card
# ==========================================================

def score_card(score: float, rating: str, stars: str):
    color = "#00E676" if score >= 90 else ("#FACC15" if score >= 75 else "#FF5252")

    html = (
        f'<div style="background:rgba(88,166,255,0.06);border:1px solid rgba(88,166,255,0.2);'
        f'border-radius:14px;padding:24px;text-align:center;">'
        f'<div style="font-size:3.6rem;font-weight:800;color:{color};line-height:1;">{score}</div>'
        f'<div style="font-size:1.1rem;font-weight:700;color:#F0F6FC;margin-top:4px;">{rating}</div>'
        f'<div style="font-size:1.3rem;color:#FACC15;margin-top:4px;">{stars}</div>'
        f'<div style="color:#8B949E;font-size:0.78rem;margin-top:6px;">Benchmark Score / 100</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ==========================================================
# Section Header
# ==========================================================

def section_header(text: str):
    html = (
        f'<div style="font-size:1.05rem;font-weight:700;color:#F0F6FC;'
        f'border-left:3px solid #58A6FF;padding-left:10px;margin-bottom:12px;margin-top:4px;">'
        f'{text}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ==========================================================
# Page Title
# ==========================================================

def page_title(title: str, subtitle: str = ""):
    html = (
        f'<div style="margin-bottom:8px;">'
        f'<div style="font-size:2rem;font-weight:800;'
        f'background:linear-gradient(135deg,#58A6FF,#7C3AED);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        f'background-clip:text;letter-spacing:-0.5px;line-height:1.2;">{title}</div>'
        f'<div style="color:#8B949E;font-size:0.88rem;margin-top:2px;">{subtitle}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)