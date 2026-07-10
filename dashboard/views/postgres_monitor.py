import streamlit as st
import pandas as pd

from postgres_metrics import (
    postgres_alive,
    postgres_summary,
    bytes_to_human
)

from components.cards import metric_card


def render():

    st.title("🐘 PostgreSQL Monitor")

    st.caption(
        "Real-time monitoring of the PostgreSQL metadata database"
    )

    # =====================================================
    # Connection
    # =====================================================

    if not postgres_alive():

        st.error(
            "❌ Unable to connect to PostgreSQL."
        )

        st.info(
            "Verify that the PostgreSQL container is running."
        )

        return

    summary = postgres_summary()

    st.success(
        "🟢 PostgreSQL Connected"
    )

    st.divider()

    # =====================================================
    # KPI Cards
    # =====================================================

    st.subheader("📊 Database Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        metric_card(
            "Database Size",
            bytes_to_human(summary["database_size"]),
            "💾"
        )

    with c2:

        metric_card(
            "Connections",
            summary["connections"],
            "🔗"
        )

    with c3:

        metric_card(
            "Tables",
            summary["tables"],
            "📋"
        )

    with c4:

        metric_card(
            "Indexes",
            summary["indexes"],
            "⚡"
        )

    st.divider()

    # =====================================================
    # Database Details
    # =====================================================

    st.subheader("📋 Database Information")

    details = pd.DataFrame({

        "Property": [

            "Status",

            "Database Size",

            "Connections",

            "Tables",

            "Indexes",

            "Version"

        ],

        "Value": [

            "🟢 Healthy",

            bytes_to_human(summary["database_size"]),

            summary["connections"],

            summary["tables"],

            summary["indexes"],

            summary["version"]

        ]

    })

    st.dataframe(

        details,

        hide_index=True,

        use_container_width=True

    )

    st.divider()

    # =====================================================
    # Health
    # =====================================================

    st.subheader("❤️ Database Health")

    st.success("🟢 PostgreSQL is reachable.")

    if summary["connections"] > 50:

        st.warning(
            f"⚠ High connection count ({summary['connections']})."
        )

    else:

        st.success(
            f"🟢 {summary['connections']} active connection(s)."
        )

    if summary["tables"] == 0:

        st.warning(
            "⚠ No tables found in the public schema."
        )

    else:

        st.success(
            f"🟢 {summary['tables']} table(s) available."
        )

    if summary["indexes"] == 0:

        st.warning(
            "⚠ No indexes found."
        )

    else:

        st.success(
            f"🟢 {summary['indexes']} index(es) available."
        )