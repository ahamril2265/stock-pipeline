import streamlit as st
import pandas as pd
import plotly.express as px

from storage_metrics import (
    storage_summary,
    bytes_to_human
)

from components.cards import metric_card


# ==========================================================
# Service Card
# ==========================================================

def service_card(name, healthy, metrics):

    with st.container(border=True):

        left, right = st.columns([4, 1])

        with left:
            st.subheader(name)

        with right:

            if healthy:
                st.success("🟢")
            else:
                st.error("🔴")

        # ClickHouse
        if name.startswith("🗄"):

            st.metric("Tables", metrics["tables"])
            st.metric("Rows", f"{metrics['rows']:,}")
            st.metric(
                "Database Size",
                bytes_to_human(metrics["database_size"])
            )
            st.metric(
                "Active Queries",
                metrics["active_queries"]
            )
            st.metric(
                "Parts",
                metrics["parts"]
            )

        # MinIO
        elif name.startswith("🪣"):

            st.metric(
                "Buckets",
                metrics["buckets"]
            )

            st.metric(
                "Objects",
                f"{metrics['objects']:,}"
            )

            st.metric(
                "Storage Used",
                bytes_to_human(
                    metrics.get(
                        "storage_used",
                        0
                    )
                )
            )

            st.metric(
                "Largest Bucket",
                metrics.get(
                    "largest_bucket",
                    "-"
                )
            )
        # PostgreSQL
        elif name.startswith("🐘"):

            st.metric(
                "Tables",
                metrics["tables"]
            )

            st.metric(
                "Connections",
                metrics["connections"]
            )

            st.metric(
                "Database Size",
                bytes_to_human(
                    metrics["database_size"]
                )
            )

            st.metric(
                "Indexes",
                metrics["indexes"]
            )



# ==========================================================
# Page
# ==========================================================

def render():

    st.title("💾 Storage Monitor")

    st.caption(
        "Real-time monitoring of storage and analytics services"
    )

    storage = storage_summary()

    clickhouse = storage["clickhouse"]
    minio = storage["minio"]
    #postgres = storage["postgres"]

    # =====================================================
    # Overview
    # =====================================================

    st.subheader("📊 Storage Overview")

    c1, c2 = st.columns(2)

    with c1:

        metric_card(
            "Services",
            storage["services"],
            "💾"
        )

    with c2:

        metric_card(
            "Healthy",
            storage["healthy"],
            "🟢"
        )

    '''with c3:

        metric_card(
            "Health %",
            f"{storage['healthy']/storage['services']*100:.0f}%",
            "❤️"
        )'''

    st.divider()


    # =====================================================
    # Services
    # =====================================================

    left, middle, right = st.columns(3)

    with left:

        service_card(
            "🗄 ClickHouse",
            clickhouse["healthy"],
            clickhouse
        )

    with middle:

        service_card(
            "🪣 MinIO",
            minio["healthy"],
            minio
        )

    '''with right:

        service_card(
            "🐘 PostgreSQL",
            postgres["healthy"],
            postgres
        )'''

    st.divider()

    # =====================================================
    # Bucket Usage
    # =====================================================

    if minio["healthy"] and minio["usage"]:

        st.subheader("🪣 Bucket Usage")

        usage_df = pd.DataFrame(

    [

        {

            "Bucket": bucket,

            "Objects": stats["objects"],

            "Size (MB)": round(

                stats["size"] /

                1024 /

                1024,

                2

            )

        }

        for bucket, stats in minio["usage"].items()

    ]

)

        fig = px.bar(

    usage_df,

    x="Bucket",

    y="Size (MB)",

    color="Size (MB)",

    text="Size (MB)",

    template="plotly_dark"

)

        fig.update_layout(

            height=450,

            xaxis_title="Bucket",

            yaxis_title="Objects"

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # Summary Table
    # =====================================================

    st.subheader("📋 Storage Summary")

    summary = pd.DataFrame({

        "Service": [

            "ClickHouse",

            "MinIO",

            #"PostgreSQL"

        ],

        "Status": [

            "🟢 Healthy" if clickhouse["healthy"] else "🔴 Offline",

            "🟢 Healthy" if minio["healthy"] else "🔴 Offline",

            #"🟢 Healthy" if postgres["healthy"] else "🔴 Offline"

        ],

        "Details": [

            f"{clickhouse['tables']} tables | "
            f"{clickhouse['rows']:,} rows | "
            f"{bytes_to_human(clickhouse['database_size'])}",

            f"{minio['buckets']} buckets | "
            f"{minio['objects']:,} objects | "
            f"{bytes_to_human(minio['storage_used'])}",

            #f"{postgres['tables']} tables"

        ]

    })

    st.dataframe(

        summary,

        hide_index=True,

        use_container_width=True

    )

    st.divider()

    st.subheader("📈 Storage Distribution")

    chart = pd.DataFrame({

        "Service": [

            "ClickHouse",

            "MinIO"

        ],

        "Storage (MB)": [

            clickhouse["database_size"] / 1024 / 1024,

            minio["storage_used"] / 1024 / 1024

        ]

    })

    fig = px.pie(

        chart,

        names="Service",

        values="Storage (MB)",

        hole=0.45,

        template="plotly_dark"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    # =====================================================
    # Overall Status
    # =====================================================

    if storage["healthy"] == storage["services"]:

        st.success(
            "✅ All storage services are healthy."
        )

    elif storage["healthy"] > 0:

        st.warning(
            "⚠ Some storage services require attention."
        )

    else:

        st.error(
            "❌ No storage services are reachable."
        )