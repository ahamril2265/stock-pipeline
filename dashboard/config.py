import os

# =====================================================
# Dashboard
# =====================================================

AUTO_REFRESH_SECONDS = 30

AUTO_REFRESH_MS = AUTO_REFRESH_SECONDS * 1000

PAGE_TITLE = "Stock Analytics Dashboard"

PAGE_ICON = "📈"

LAYOUT = "wide"

SIDEBAR_STATE = "expanded"

CHART_HEIGHT = 420

CHART_HEIGHT_SMALL = 320

CHART_HEIGHT_LARGE = 520

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

ACCENT = "#F78166"

# =====================================================
# Plotly
# =====================================================

PLOTLY_CONFIG = {
    "displaylogo":             False,
    "responsive":              True,
    "scrollZoom":              True,
    "modeBarButtonsToRemove":  ["lasso2d", "select2d", "zoomIn2d", "zoomOut2d"],
}

# =====================================================
# Alerts
# =====================================================

LATENCY_THRESHOLD   = 25

PRICE_SPIKE_PERCENT = 5

VOLUME_SPIKE        = 500_000

# =====================================================
# Refresh
# =====================================================

REFRESH_TEXT = f"Every {AUTO_REFRESH_SECONDS} Seconds"

# =====================================================
# Service URLs  (inside Docker network)
# =====================================================

SERVICE_URLS = {
    "Spark Master":      "http://spark-master:8080",
    "Airflow":           "http://airflow-webserver:8080",
    "MinIO":             "http://minio:9000",
    "Schema Registry":   "http://schema-registry:8081",
    "ClickHouse HTTP":   "http://clickhouse:8123",
}

# =====================================================
# PostgreSQL  (matching docker-compose)
# =====================================================

POSTGRES_HOST     = os.getenv("POSTGRES_HOST",     "postgres")
POSTGRES_PORT     = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB       = os.getenv("POSTGRES_DB",       "stockdb")
POSTGRES_USER     = os.getenv("POSTGRES_USER",     "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")