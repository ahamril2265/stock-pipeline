import streamlit as st
from health import all_services


def render():
    try:
        services = all_services()
    except Exception:
        services = {}

    pills = []
    for name, ok in services.items():
        dot_cls  = "dot-online"    if ok else "dot-offline"
        pill_cls = "status-online" if ok else "status-offline"
        label    = "ONLINE"        if ok else "OFFLINE"
        pills.append(
            f'<span class="status-pill {pill_cls}" style="font-size:0.72rem;padding:3px 10px;">'
            f'<span class="status-dot {dot_cls}"></span>{name}&nbsp;·&nbsp;{label}</span>'
        )

    bar = "".join(pills)
    st.markdown(
        f'<div class="status-bar-wrap">{bar}</div>',
        unsafe_allow_html=True,
    )