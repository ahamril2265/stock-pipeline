import streamlit as st
import pandas as pd

from log_metrics import (
    containers,
    logs
)


def render():

    st.title("📜 Live Logs")

    st.caption(
        "Real-time logs from all pipeline services"
    )

    # =====================================================
    # Sidebar Filters
    # =====================================================

    left, middle, right = st.columns([2, 2, 3])

    with left:

        service = st.selectbox(

            "Service",

            containers()

        )

    with middle:

        level = st.selectbox(

            "Log Level",

            [

                "ALL",

                "INFO",

                "WARNING",

                "ERROR",

                "SUCCESS"

            ]

        )

    with right:

        search = st.text_input(

            "Search"

        )

    st.divider()

    # =====================================================
    # Load Logs
    # =====================================================

    df = pd.DataFrame(

        logs(service)

    )

    if df.empty:

        st.warning(
            "No logs available."
        )

        return

    # =====================================================
    # Filtering
    # =====================================================

    if level != "ALL":

        df = df[

            df["Level"] == level

        ]

    if search:

        df = df[

            df["Message"]

            .str.contains(

                search,

                case=False,

                na=False

            )

        ]

    # =====================================================
    # Statistics
    # =====================================================

    st.subheader("📊 Log Statistics")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(

            "Total",

            len(df)

        )

    with c2:

        st.metric(

            "Errors",

            len(

                df[

                    df["Level"] == "ERROR"

                ]

            )

        )

    with c3:

        st.metric(

            "Warnings",

            len(

                df[

                    df["Level"] == "WARNING"

                ]

            )

        )

    with c4:

        st.metric(

            "Info",

            len(

                df[

                    df["Level"] == "INFO"

                ]

            )

        )

    st.divider()

    # =====================================================
    # Download
    # =====================================================

    st.download_button(

        "⬇ Download Logs",

        df.to_csv(

            index=False

        ),

        file_name=f"{service.lower()}_logs.csv",

        mime="text/csv"

    )

    st.divider()

    # =====================================================
    # Table
    # =====================================================

    st.subheader("📋 Log Viewer")

    st.dataframe(

        df,

        hide_index=True,

        use_container_width=True,

        height=550

    )

    st.divider()

    # =====================================================
    # Live Tail
    # =====================================================

    st.subheader("🖥 Live Tail")

    with st.container(

        border=True

    ):

        latest = df.tail(15)

        for _, row in latest.iterrows():

            if row["Level"] == "ERROR":

                st.error(

                    f"[{row['Time']}] {row['Message']}"

                )

            elif row["Level"] == "WARNING":

                st.warning(

                    f"[{row['Time']}] {row['Message']}"

                )

            elif row["Level"] == "SUCCESS":

                st.success(

                    f"[{row['Time']}] {row['Message']}"

                )

            else:

                st.text(

                    f"[{row['Time']}] {row['Message']}"

                )