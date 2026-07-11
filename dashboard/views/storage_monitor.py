import streamlit as st
from storage_metrics import storage_summary, bytes_to_human
from postgres_metrics import postgres_summary
from components.cards import metric_card, status_badge, section_header, page_title
from components.charts import minio_bucket_chart
from config import PLOTLY_CONFIG

def render():
    page_title("💾 Storage Monitor", "ClickHouse · MinIO · PostgreSQL")

    data     = storage_summary()
    ch       = data["clickhouse"]
    minio    = data["minio"]
    postgres = data.get("postgres") or postgres_summary()

    st.divider()

    # ── Overall Status ─────────────────────────────────────
    section_header("🔌 Storage Health")
    h1, h2, h3 = st.columns(3)
    with h1:
        status_badge("ClickHouse", ch["healthy"],  "Analytics DB")
    with h2:
        status_badge("MinIO",     minio["healthy"], "Object Storage")
    with h3:
        status_badge("PostgreSQL",postgres["healthy"],"Metadata Store")

    st.divider()

    # ── ClickHouse ─────────────────────────────────────────
    section_header("🗃 ClickHouse")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Tables",         str(ch["tables"]),                     "📋")
    with c2:
        metric_card("Rows",           f'{ch["rows"]:,}',                     "🔢")
    with c3:
        metric_card("DB Size",        bytes_to_human(ch["database_size"]),   "💽", color="primary")
    with c4:
        metric_card("Active Queries", str(ch["active_queries"]),             "⚡")
    with c5:
        metric_card("Parts",          str(ch["parts"]),                      "🧩")

    st.divider()

    # ── MinIO ─────────────────────────────────────────────
    section_header("🗄 MinIO Object Storage")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Buckets",        str(minio["buckets"]),                  "🪣")
    with m2:
        metric_card("Objects",        f'{minio["objects"]:,}',                "📦")
    with m3:
        metric_card("Total Storage",  bytes_to_human(minio["storage_used"]), "💾", color="primary")
    with m4:
        metric_card("Largest Bucket", minio["largest_bucket"],                "🏆", color="success")

    if minio["usage"]:
        chart = minio_bucket_chart(minio["usage"])
        if chart:
            st.plotly_chart(chart, use_container_width=True, config=PLOTLY_CONFIG)

    st.divider()

    # ── PostgreSQL ────────────────────────────────────────
    section_header("🐘 PostgreSQL")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        metric_card("Tables",      str(postgres["tables"]),                     "📋")
    with p2:
        metric_card("Connections", str(postgres["connections"]),                "🔌")
    with p3:
        metric_card("DB Size",     bytes_to_human(postgres["database_size"]),   "💽", color="primary")
    with p4:
        metric_card("Indexes",     str(postgres["indexes"]),                    "📇")

    if "version" in postgres and postgres["healthy"]:
        st.markdown(
            f'<div style="color:#8B949E;font-size:0.78rem;margin-top:4px;">Version: {postgres["version"][:60]}</div>',
            unsafe_allow_html=True,
        )