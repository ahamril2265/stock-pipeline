import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =====================================================
# Theme
# =====================================================

BG      = "#0E1117"
PAPER   = "#0E1117"
GRID    = "#30363D"
TEXT    = "#F0F6FC"
MUTED   = "#8B949E"

PRIMARY   = "#58A6FF"
SUCCESS   = "#00E676"
DANGER    = "#FF5252"
ACCENT    = "#7C3AED"
WARNING   = "#FACC15"
ACCENT2   = "#F78166"


# =====================================================
# Shared Layout
# =====================================================

def apply_layout(fig, title="", height=420):
    fig.update_layout(
        title=dict(text=title, x=0.02, xanchor="left", font=dict(size=14, color=TEXT)),
        template="plotly_dark",
        height=height,
        paper_bgcolor=PAPER,
        plot_bgcolor=BG,
        font=dict(family="Inter, Arial", size=13, color=TEXT),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    return fig


# =====================================================
# Top Symbols Bar
# =====================================================

def top_symbols_chart(df, n=10):
    df = df.head(n).sort_values("total_volume")
    fig = px.bar(
        df, x="total_volume", y="stock_symbol",
        orientation="h",
        color="total_volume",
        color_continuous_scale=[[0, "#1C2128"], [1, PRIMARY]],
        text="total_volume",
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Volume: %{x:,.0f}<extra></extra>",
    )
    fig.update_coloraxes(showscale=False)
    return apply_layout(fig, "📊 Trading Volume by Symbol")


# =====================================================
# Buy vs Sell Donut
# =====================================================

def buy_sell_chart(df):
    row = df.iloc[0]
    fig = go.Figure(data=[go.Pie(
        labels=["Buy", "Sell"],
        values=[row["total_buy_volume"], row["total_sell_volume"]],
        hole=0.6,
        marker=dict(colors=[SUCCESS, DANGER]),
        textinfo="label+percent",
        textfont=dict(size=13),
    )])
    return apply_layout(fig, "📈 Buy vs Sell Distribution")


# =====================================================
# VWAP Comparison Bar
# =====================================================

def vwap_chart(df):
    fig = px.bar(
        df.sort_values("vwap", ascending=False).head(15),
        x="stock_symbol", y="vwap",
        color="vwap",
        color_continuous_scale=[[0, "#1C2128"], [1, ACCENT]],
        text="vwap",
    )
    fig.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
    fig.update_coloraxes(showscale=False)
    return apply_layout(fig, "💰 VWAP Comparison")


# =====================================================
# Market Share Treemap
# =====================================================

def market_share_chart(df):
    fig = px.treemap(
        df, path=["stock_symbol"], values="total_volume",
        color="total_volume",
        color_continuous_scale=[[0, "#1C2128"], [0.5, "#2C4A7C"], [1, PRIMARY]],
    )
    fig.update_traces(textinfo="label+percent root+value")
    fig.update_coloraxes(showscale=False)
    return apply_layout(fig, "🌍 Market Share by Volume", height=520)


# =====================================================
# Volume Timeline
# =====================================================

def volume_timeline(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["window_start"], y=df["total_volume"],
        mode="lines+markers",
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(88,166,255,0.07)",
    ))
    return apply_layout(fig, "📈 Volume Timeline")


# =====================================================
# Candlestick (OHLC) + Volume subplot
# =====================================================

def candlestick_chart(df, symbol=""):
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.04,
    )

    # Candles
    fig.add_trace(go.Candlestick(
        x=df["window_start"],
        open=df["open_price"],
        high=df["high_price"],
        low=df["low_price"],
        close=df["close_price"],
        increasing_line_color=SUCCESS,
        decreasing_line_color=DANGER,
        increasing_fillcolor="rgba(0,230,118,0.7)",
        decreasing_fillcolor="rgba(255,82,82,0.7)",
        name="OHLC",
    ), row=1, col=1)

    # Volume bars
    df = df.copy()
    df["color"] = df.apply(
        lambda r: SUCCESS if r["close_price"] >= r["open_price"] else DANGER, axis=1
    )
    fig.add_trace(go.Bar(
        x=df["window_start"], y=df["total_volume"],
        marker_color=df["color"],
        opacity=0.6,
        name="Volume",
    ), row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PAPER, plot_bgcolor=BG,
        height=500,
        font=dict(family="Inter, Arial", size=13, color=TEXT),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False,
        xaxis_rangeslider_visible=False,
        title=dict(text=f"🕯 OHLC — {symbol}", x=0.02, font=dict(size=14, color=TEXT)),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig


# =====================================================
# Gauge Chart (CPU / Memory / Disk)
# =====================================================

def gauge_chart(value: float, max_val: float, title: str, height=260):
    if value >= max_val * 0.9:
        bar_color = DANGER
    elif value >= max_val * 0.7:
        bar_color = WARNING
    else:
        bar_color = SUCCESS

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix="%", font=dict(size=32, color=TEXT, family="Inter")),
        title=dict(text=title, font=dict(size=14, color=MUTED, family="Inter")),
        gauge=dict(
            axis=dict(range=[0, max_val], tickcolor=MUTED, tickfont=dict(color=MUTED)),
            bar=dict(color=bar_color, thickness=0.6),
            bgcolor=BG,
            borderwidth=0,
            steps=[
                dict(range=[0, max_val * 0.7],  color="#1A2332"),
                dict(range=[max_val * 0.7, max_val * 0.9],  color="#2C2B1A"),
                dict(range=[max_val * 0.9, max_val], color="#2C1A1A"),
            ],
            threshold=dict(
                line=dict(color=DANGER, width=3),
                thickness=0.8,
                value=max_val * 0.9,
            ),
        ),
    ))
    fig.update_layout(
        paper_bgcolor=PAPER, height=height,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family="Inter, Arial"),
    )
    return fig


# =====================================================
# Radar / Spider  (for benchmark)
# =====================================================

def radar_chart(categories, values, title=""):
    # Close the polygon
    cats = categories + [categories[0]]
    vals = values + [values[0]]

    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats,
        fill="toself",
        line=dict(color=PRIMARY, width=2),
        fillcolor="rgba(88,166,255,0.12)",
        marker=dict(size=6, color=PRIMARY),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=BG,
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color=MUTED)),
            angularaxis=dict(tickfont=dict(color=TEXT)),
        ),
        paper_bgcolor=PAPER,
        font=dict(family="Inter, Arial", color=TEXT),
        height=400,
        margin=dict(l=30, r=30, t=50, b=30),
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=14, color=TEXT)),
    )
    return fig


# =====================================================
# Stacked Cluster Bar (Spark cores / memory)
# =====================================================

def cluster_bar(categories, used_vals, free_vals, title=""):
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Used", x=categories, y=used_vals, marker_color=PRIMARY))
    fig.add_trace(go.Bar(name="Free", x=categories, y=free_vals, marker_color=GRID))
    fig.update_layout(barmode="stack")
    return apply_layout(fig, title)


# =====================================================
# Horizontal Stage Throughput
# =====================================================

def stage_throughput_chart(stages: dict):
    names  = list(stages.keys())
    values = list(stages.values())
    colors = [PRIMARY, ACCENT, SUCCESS, WARNING, ACCENT2]

    fig = go.Figure(go.Bar(
        x=values, y=names,
        orientation="h",
        marker=dict(color=colors[:len(names)]),
        text=[f"{v:,.0f}" for v in values],
        textposition="outside",
    ))
    return apply_layout(fig, "⚡ Pipeline Stage Throughput")


# =====================================================
# MinIO Bucket Bar
# =====================================================

def minio_bucket_chart(usage: dict):
    if not usage:
        return None
    names  = list(usage.keys())
    sizes  = [v["size"] / (1024 ** 2) for v in usage.values()]  # MB
    fig = px.bar(x=names, y=sizes, color=sizes,
                 color_continuous_scale=[[0, "#1C2128"], [1, PRIMARY]],
                 labels={"x": "Bucket", "y": "Size (MB)"})
    fig.update_coloraxes(showscale=False)
    return apply_layout(fig, "🗄 Bucket Storage (MB)")