import streamlit as st
from datetime import datetime, UTC


SERVICES = [
    {
        "name": "Kafka",
        "status": True,
        "role": "Streaming"
    },
    {
        "name": "Spark",
        "status": True,
        "role": "Processing"
    },
    {
        "name": "Airflow",
        "status": True,
        "role": "Scheduler"
    },
    {
        "name": "ClickHouse",
        "status": True,
        "role": "Analytics"
    },
    {
        "name": "MinIO",
        "status": True,
        "role": "Lakehouse"
    }
]


def render():

    st.subheader("🚀 Pipeline Status")

    cols = st.columns(len(SERVICES) + 1)

    # ==========================================
    # Service Cards
    # ==========================================

    for col, service in zip(cols[:-1], SERVICES):

        with col:

            with st.container(border=True):

                status = "🟢 Online" if service["status"] else "🔴 Offline"

                st.markdown(f"### {service['name']}")

                st.caption(service["role"])

                if service["status"]:
                    st.success(status)
                else:
                    st.error(status)

    # ==========================================
    # Refresh Card
    # ==========================================

    with cols[-1]:

        with st.container(border=True):

            st.markdown("### 🔄")

            st.caption("Auto Refresh")

            st.info("Every 5 Seconds")

            st.caption(
                datetime.now(UTC).strftime(
                    "%H:%M:%S UTC"
                )
            )

    st.divider()