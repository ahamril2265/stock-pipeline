import os
import streamlit as st
import clickhouse_connect
import pandas as pd


# ==========================================================
# ClickHouse Client  (cached for the whole session)
# ==========================================================

@st.cache_resource
def get_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST",     "clickhouse"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER",     "admin"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "admin123"),
        database=os.getenv("CLICKHOUSE_DATABASE", "stock_analytics"),
    )


def query_dataframe(sql: str) -> pd.DataFrame:
    """Run a ClickHouse query and return a DataFrame. Silently returns empty on error."""
    try:
        client = get_client()
        result = client.query(sql)
        return pd.DataFrame(result.result_rows, columns=result.column_names)
    except Exception:
        return pd.DataFrame()


# ==========================================================
# Gold Table Queries  (cached 10 s for polling)
# ==========================================================

@st.cache_data(ttl=10)
def get_market_kpis() -> pd.DataFrame:
    return query_dataframe("""
        SELECT *
        FROM gold_market_kpis
        ORDER BY updated_at DESC
        LIMIT 1
    """)


@st.cache_data(ttl=10)
def get_top_symbols() -> pd.DataFrame:
    return query_dataframe("""
        SELECT *
        FROM gold_top_symbols
        ORDER BY volume_rank
    """)


@st.cache_data(ttl=10)
def get_symbol_summary() -> pd.DataFrame:
    return query_dataframe("""
        SELECT *
        FROM gold_symbol_summary
    """)


@st.cache_data(ttl=10)
def get_ohlc() -> pd.DataFrame:
    return query_dataframe("""
        SELECT *
        FROM gold_ohlc
        ORDER BY stock_symbol, window_start
    """)


@st.cache_data(ttl=10)
def get_ohlc_for_symbol(symbol: str) -> pd.DataFrame:
    return query_dataframe(f"""
        SELECT *
        FROM gold_ohlc
        WHERE stock_symbol = '{symbol}'
        ORDER BY window_start
    """)


@st.cache_data(ttl=10)
def get_symbol_detail(symbol: str) -> pd.DataFrame:
    return query_dataframe(f"""
        SELECT *
        FROM gold_symbol_summary
        WHERE stock_symbol = '{symbol}'
        LIMIT 1
    """)


def get_gold_freshness() -> dict:
    """Return latest updated_at per gold table."""
    tables = {
        "Market KPIs":     "gold_market_kpis",
        "Symbol Summary":  "gold_symbol_summary",
        "Top Symbols":     "gold_top_symbols",
        "OHLC":            "gold_ohlc",
    }
    result = {}
    for label, table in tables.items():
        df = query_dataframe(f"SELECT max(updated_at) AS ts, count() AS rows FROM {table}")
        if not df.empty:
            result[label] = {
                "ts":   df.iloc[0]["ts"],
                "rows": int(df.iloc[0]["rows"]),
            }
        else:
            result[label] = {"ts": None, "rows": 0}
    return result