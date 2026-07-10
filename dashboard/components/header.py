import streamlit as st

from datetime import datetime, UTC

from notifications import notification_badge


def render():

    left, right = st.columns([5, 1])

    

    with left:

        st.title("📈 Stock Analytics Dashboard")

        st.caption(
            "End-to-End Real-Time Data Pipeline with Failure Recovery"
        )

        st.caption(
            "Apache Kafka • Apache Spark • Delta Lake • "
            "ClickHouse • Airflow • MinIO"
        )

    with right:

        badge = notification_badge()

        with st.container(border=True):

            st.success("🟢 LIVE")

            st.info(
    f"""
🚨 {badge['errors']}

⚠ {badge['warnings']}

ℹ {badge['infos']}
"""
)

            st.caption(
                datetime.now(UTC).strftime(
                    "%d %b %Y"
                )
            )

            st.caption(
                datetime.now(UTC).strftime(
                    "%H:%M:%S UTC"
                )
            )

            st.info("🔄 Every 5 sec")

    st.divider()