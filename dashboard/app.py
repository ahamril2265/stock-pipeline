import streamlit as st

# ── Page Config (MUST BE FIRST) ───────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auto-Refresh ──────────────────────────────────────────────────────────────
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=30_000, key="global_refresh")

# ── Imports ───────────────────────────────────────────────────────────────────
from components.sidebar    import render as sidebar
from components.header     import render as header
from components.status_bar import render as status_bar
from components.footer     import render as footer

from views.market_overview      import render as overview
from views.top_symbols          import render as top_symbols
from views.symbol_analysis      import render as symbol_analysis
from views.ohlc                 import render as ohlc
from views.pipeline_health      import render as pipeline_health
from views.failure_recovery     import render as failure_recovery
from views.spark_monitor        import render as spark_monitor
from views.airflow_monitor      import render as airflow_monitor
from views.kafka_monitor        import render as kafka_monitor
from views.storage_monitor      import render as storage_monitor
from views.logs_monitor         import render as logs_monitor
from views.architecture         import render as architecture
from views.performance_benchmark import render as performance_benchmark


# ── CSS ───────────────────────────────────────────────────────────────────────
def load_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass   # silently skip if missing

load_css()

# ── Shell ─────────────────────────────────────────────────────────────────────
page = sidebar()
header()
status_bar()

# ── Routing ───────────────────────────────────────────────────────────────────
if   page == "📈 Market Overview":       overview()
elif page == "🏆 Top Symbols":           top_symbols()
elif page == "🔍 Symbol Analysis":       symbol_analysis()
elif page == "🕯 OHLC":                  ohlc()
elif page == "⚙ Pipeline Health":        pipeline_health()
elif page == "🛡 Failure Recovery":      failure_recovery()
elif page == "⚡ Spark Cluster":         spark_monitor()
elif page == "🌬 Airflow Monitor":       airflow_monitor()
elif page == "📨 Kafka Cluster":         kafka_monitor()
elif page == "💾 Storage Monitor":       storage_monitor()
elif page == "📜 Live Logs":             logs_monitor()
elif page == "🏗 Architecture":          architecture()
elif page == "📊 Performance Benchmark": performance_benchmark()

footer()