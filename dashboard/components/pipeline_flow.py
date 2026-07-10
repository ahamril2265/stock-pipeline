import streamlit as st


STATUS = {

    "healthy": {
        "icon": "🟢",
        "text": "Healthy",
        "color": "#00E676"
    },

    "warning": {
        "icon": "🟡",
        "text": "Warning",
        "color": "#FACC15"
    },

    "failed": {
        "icon": "🔴",
        "text": "Failed",
        "color": "#FF5252"
    }

}


def stage(stage_name, state="healthy"):

    item = STATUS.get(state, STATUS["healthy"])

    st.markdown(

        f"""
        <div style="
            background:#161B22;
            border:2px solid {item['color']};
            border-radius:12px;
            padding:18px;
            text-align:center;
            min-height:120px;
        ">

            <div style="font-size:34px;">
                {item['icon']}
            </div>

            <div style="
                font-size:18px;
                font-weight:bold;
                color:white;
                margin-top:10px;
            ">
                {stage_name}
            </div>

            <div style="
                color:{item['color']};
                margin-top:8px;
                font-weight:bold;
            ">
                {item['text']}
            </div>

        </div>
        """,

        unsafe_allow_html=True

    )


def connector():

    st.markdown(

        """
        <div style="
            text-align:center;
            font-size:30px;
            color:#58A6FF;
            padding-top:45px;
        ">
            ➜
        </div>
        """,

        unsafe_allow_html=True

    )


def render(flow):

    st.subheader("🚀 Pipeline Flow")

    total = len(flow)

    columns = st.columns(total * 2 - 1)

    column_index = 0

    for i, stage_info in enumerate(flow):

        with columns[column_index]:

            state = "healthy"

            if not stage_info["healthy"]:

                state = "failed"

            stage(

                stage_info["name"],

                state

            )

        column_index += 1

        if i != total - 1:

            with columns[column_index]:

                connector()

            column_index += 1