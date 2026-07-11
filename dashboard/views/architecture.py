import streamlit as st
from health import all_services, pipeline_summary
from components.cards import section_header, status_badge

PIPELINE_STAGES = [
    ("🐍", "Producer",    "Python + Avro"),
    ("📨", "Kafka",       "Confluent 7.5"),
    ("⚡", "Spark",       "Structured Streaming"),
    ("🗻", "Bronze",      "MinIO Delta Lake"),
    ("🥈", "Silver",      "Validated Data"),
    ("🥇", "Gold",        "ClickHouse Aggregated"),
    ("📊", "Dashboard",   "Streamlit + Plotly"),
]

STACK_INVENTORY = [
    ("Kafka",           "confluentinc/cp-kafka:7.5.0",              "9092",  "Message broker"),
    ("Zookeeper",       "confluentinc/cp-zookeeper:7.5.0",          "2181",  "Kafka coordination"),
    ("Schema Registry", "confluentinc/cp-schema-registry:7.5.0",    "8081",  "Avro schema store"),
    ("Spark Master",    "custom (Dockerfile.spark-master)",          "8080",  "Cluster manager"),
    ("Spark Worker",    "custom (Dockerfile.spark-worker)",          "-",     "Processing node"),
    ("ClickHouse",      "clickhouse/clickhouse-server:latest",       "8123",  "Analytical DB"),
    ("PostgreSQL",      "postgres:15",                               "5432",  "Metadata store"),
    ("MinIO",           "minio/minio",                               "9000",  "Object storage (S3)"),
    ("Airflow",         "custom (airflow/Dockerfile)",               "8080",  "Workflow orchestrator"),
    ("Producer",        "custom (Dockerfile.producer)",              "-",     "Market event emitter"),
    ("Dashboard",       "custom (dashboard/Dockerfile)",             "8501",  "Streamlit UI"),
]

def render():
    st.markdown('<div class="dashboard-title">🏗 Architecture</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Pipeline Overview & Stack Inventory</div>', unsafe_allow_html=True)

    try:
        services = all_services()
        pipeline = pipeline_summary()
    except Exception:
        services = {}
        pipeline = {"healthy": 0, "total": 0, "health_percentage": 0}

    st.divider()

    # ── Pipeline Flow (using st.columns for proper horizontal layout) ─────────
    section_header("🔄 Data Pipeline Flow")

    stage_cols = st.columns(len(PIPELINE_STAGES) * 2 - 1)
    for i, (icon, name, tech) in enumerate(PIPELINE_STAGES):
        col_idx = i * 2
        with stage_cols[col_idx]:
            st.markdown(
                f"""
                <div style="text-align:center;background:#161B22;border:1px solid #30363D;
                    border-radius:10px;padding:12px 6px;min-height:80px;">
                    <div style="font-size:1.6rem;">{icon}</div>
                    <div style="font-size:0.78rem;font-weight:700;color:#F0F6FC;">{name}</div>
                    <div style="font-size:0.65rem;color:#8B949E;margin-top:2px;">{tech}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        # Arrow between stages
        if i < len(PIPELINE_STAGES) - 1:
            with stage_cols[col_idx + 1]:
                st.markdown(
                    '<div style="text-align:center;font-size:1.5rem;color:#58A6FF;padding-top:22px;">→</div>',
                    unsafe_allow_html=True,
                )

    st.divider()

    # ── Service Status ─────────────────────────────────────
    section_header("🔌 Live Service Status")
    svc_items = list(services.items())
    cols = st.columns(min(4, len(svc_items))) if svc_items else st.columns(1)
    for i, (name, ok) in enumerate(svc_items):
        with cols[i % len(cols)]:
            status_badge(name, ok)

    st.divider()

    # ── Stack Inventory ───────────────────────────────────
    section_header("📦 Stack Inventory")
    import pandas as pd
    status_map = {
        "Kafka":           services.get("Kafka"),
        "Spark Master":    services.get("Spark"),
        "ClickHouse":      services.get("ClickHouse"),
        "PostgreSQL":      services.get("PostgreSQL"),
        "MinIO":           services.get("MinIO"),
        "Airflow":         services.get("Airflow"),
        "Schema Registry": services.get("Schema Registry"),
    }
    inv_rows = []
    for svc, image, port, role in STACK_INVENTORY:
        ok = status_map.get(svc)
        status = "🟢 Online" if ok is True else ("🔴 Offline" if ok is False else "⚪ Unknown")
        inv_rows.append({"Service": svc, "Image": image, "Port": port, "Role": role, "Status": status})
    st.dataframe(pd.DataFrame(inv_rows), hide_index=True, use_container_width=True)

    st.divider()

    # ── Service UI Links ─────────────────────────────────
    section_header("🔗 Service UIs")
    links = [
        ("📊 Dashboard",     "http://localhost:8501"),
        ("⚡ Spark Master",  "http://localhost:8080"),
        ("🌬 Airflow",       "http://localhost:8088"),
        ("🗄 MinIO Console", "http://localhost:9001"),
        ("📜 Schema Reg.",   "http://localhost:8081"),
        ("🗃 ClickHouse",    "http://localhost:8123"),
    ]
    link_cols = st.columns(3)
    for i, (label, url) in enumerate(links):
        with link_cols[i % 3]:
            st.link_button(label, url, use_container_width=True)