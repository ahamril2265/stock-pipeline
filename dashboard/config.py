import streamlit as st

# =====================================================
# Dashboard
# =====================================================

AUTO_REFRESH_MS = 5000

PAGE_TITLE = "Stock Analytics Dashboard"

PAGE_ICON = "📈"

LAYOUT = "wide"

SIDEBAR_STATE = "expanded"

# =====================================================
# Theme
# =====================================================

BACKGROUND = "#0E1117"

CARD = "#161B22"

BORDER = "#30363D"

TEXT = "#F0F6FC"

SUCCESS = "#00E676"

WARNING = "#FACC15"

ERROR = "#FF5252"

PRIMARY = "#58A6FF"

SECONDARY = "#7C3AED"

# =====================================================
# Plotly
# =====================================================

PLOTLY_CONFIG = {

    "displaylogo": False,

    "responsive": True,

    "scrollZoom": True,

    "modeBarButtonsToRemove": [

        "lasso2d",

        "select2d",

        "zoomIn2d",

        "zoomOut2d"

    ]
}

# =====================================================
# Alerts
# =====================================================

LATENCY_THRESHOLD = 25

PRICE_SPIKE_PERCENT = 5

VOLUME_SPIKE = 500000

# =====================================================
# Refresh
# =====================================================

REFRESH_TEXT = "Every 5 Seconds"