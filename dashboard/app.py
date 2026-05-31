from dash import Dash, html
from db import get_market_kpis

app = Dash(__name__)


def build_dashboard():

    try:

        df = get_market_kpis()

        if df.empty:

            return html.Div([
                html.H1("Stock Analytics Dashboard"),
                html.H3("No KPI data found")
            ])

        row = df.iloc[0]

        return html.Div([

            html.H1(
                "📈 Real-Time Stock Analytics Dashboard"
            ),

            html.Hr(),

            html.H2(
                f"Market Volume: {int(row['total_market_volume']):,}"
            ),

            html.H2(
                f"Market VWAP: {round(row['market_vwap'], 2)}"
            ),

            html.H2(
                f"Average Latency: {round(row['avg_market_latency'], 2)} ms"
            ),

            html.H2(
                f"Active Symbols: {row['active_symbols']}"
            ),

            html.H2(
                f"Buy Volume: {int(row['total_buy_volume']):,}"
            ),

            html.H2(
                f"Sell Volume: {int(row['total_sell_volume']):,}"
            )

        ])

    except Exception as e:

        return html.Div([

            html.H1("Dashboard Error"),

            html.Pre(str(e))
        ])


app.layout = build_dashboard()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8050,
        debug=True
    )