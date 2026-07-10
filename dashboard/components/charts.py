import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# Theme
# =====================================================

BACKGROUND = "#0E1117"
PAPER = "#0E1117"
GRID = "#30363D"
TEXT = "#F0F6FC"

PRIMARY = "#58A6FF"
SUCCESS = "#00E676"
DANGER = "#FF5252"
ACCENT = "#7C3AED"


# =====================================================
# Shared Layout
# =====================================================

def apply_layout(fig, title, height=420):

    fig.update_layout(

        title=dict(
            text=title,
            x=0.02,
            xanchor="left"
        ),

        template="plotly_dark",

        height=height,

        paper_bgcolor=PAPER,
        plot_bgcolor=BACKGROUND,

        font=dict(
            family="Arial",
            size=14,
            color=TEXT
        ),

        hovermode="x unified",

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),

        legend=dict(
            orientation="h",
            y=1.05,
            x=1,
            xanchor="right"
        )
    )

    fig.update_xaxes(

        showgrid=True,
        gridcolor=GRID,
        zeroline=False

    )

    fig.update_yaxes(

        showgrid=True,
        gridcolor=GRID,
        zeroline=False

    )

    return fig


# =====================================================
# Top Symbols
# =====================================================

def top_symbols_chart(df):

    fig = px.bar(

        df,

        x="total_volume",

        y="stock_symbol",

        orientation="h",

        color_discrete_sequence=[PRIMARY],

        text="total_volume"

    )

    fig.update_traces(

        texttemplate="%{text:,.0f}",

        textposition="outside",

        hovertemplate=(
            "<b>%{y}</b><br>"
            "Volume: %{x:,.0f}<extra></extra>"
        )

    )

    return apply_layout(
        fig,
        "📊 Trading Volume"
    )


# =====================================================
# Buy vs Sell
# =====================================================

def buy_sell_chart(df):

    fig = go.Figure(

        data=[

            go.Pie(

                labels=["Buy", "Sell"],

                values=[

                    df["total_buy_volume"].iloc[0],

                    df["total_sell_volume"].iloc[0]

                ],

                hole=0.55,

                marker=dict(

                    colors=[
                        SUCCESS,
                        DANGER
                    ]

                ),

                textinfo="label+percent"

            )

        ]

    )

    return apply_layout(
        fig,
        "📈 Buy vs Sell Distribution"
    )


# =====================================================
# VWAP
# =====================================================

def vwap_chart(df):

    fig = px.bar(

        df,

        x="stock_symbol",

        y="vwap",

        color_discrete_sequence=[ACCENT],

        text="vwap"

    )

    fig.update_traces(

        texttemplate="$%{text:.2f}",

        textposition="outside"

    )

    return apply_layout(
        fig,
        "💰 VWAP Comparison"
    )


# =====================================================
# Market Share
# =====================================================

def market_share_chart(df):

    fig = px.treemap(

        df,

        path=["stock_symbol"],

        values="total_volume",

        color="total_volume",

        color_continuous_scale="Blues"

    )

    return apply_layout(
        fig,
        "🌍 Market Share",
        height=500
    )


# =====================================================
# Volume Timeline
# =====================================================

def volume_timeline(df):

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=df["window_start"],

            y=df["total_volume"],

            mode="lines+markers",

            line=dict(
                color=PRIMARY,
                width=3
            ),

            marker=dict(
                size=7
            )

        )

    )

    return apply_layout(
        fig,
        "📈 Trading Volume Timeline"
    )