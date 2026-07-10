import streamlit as st


def metric_card(title, value, icon):

    with st.container(border=True):

        c1, c2 = st.columns([1, 4])

        with c1:
            st.markdown(
                f"<h1 style='text-align:center;'>{icon}</h1>",
                unsafe_allow_html=True
            )

        with c2:
            st.caption(title)

            st.markdown(
                f"""
                <div style="
                    font-size:30px;
                    font-weight:700;
                    color:white;
                    margin-top:-8px;
                ">
                    {value}
                </div>
                """,
                unsafe_allow_html=True
            )