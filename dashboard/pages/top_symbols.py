from dash import html, dash_table
from db import get_top_symbols

def layout():

    df = get_top_symbols()

    return html.Div([

        html.H2("Top Symbols"),

        dash_table.DataTable(
            data=df.to_dict("records"),

            columns=[
                {"name": col, "id": col}
                for col in df.columns
            ],

            page_size=10,

            sort_action="native",

            style_table={
                "overflowX": "auto"
            }
        )
    ])