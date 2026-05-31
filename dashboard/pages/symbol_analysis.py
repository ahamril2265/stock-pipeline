from dash import html, dcc
from db import get_symbols

def layout():

    symbols = get_symbols()

    return html.Div([

        html.H2("Symbol Analysis"),

        dcc.Dropdown(
            id="symbol-dropdown",

            options=[
                {
                    "label": s,
                    "value": s
                }
                for s in symbols["stock_symbol"]
            ],

            value=symbols["stock_symbol"].iloc[0]
        ),

        html.Div(id="symbol-summary"),

        dcc.Graph(id="ohlc-chart")

    ])