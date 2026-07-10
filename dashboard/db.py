import os
import clickhouse_connect
import pandas as pd

HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
DATABASE = os.getenv("CLICKHOUSE_DATABASE", "stock_analytics")
USERNAME = os.getenv("CLICKHOUSE_USER", "admin")
PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "admin123")


client = clickhouse_connect.get_client(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    database=DATABASE
)


def query_dataframe(sql):
    result = client.query(sql)

    return pd.DataFrame(
        result.result_rows,
        columns=result.column_names
    )


def get_market_kpis():

    df = query_dataframe("""
        SELECT *
        FROM gold_market_kpis
        ORDER BY updated_at DESC
        LIMIT 1
    """)

    return df


def get_top_symbols():

    return query_dataframe("""
        SELECT *
        FROM gold_top_symbols
        ORDER BY volume_rank
    """)


def get_symbol_summary():

    return query_dataframe("""
        SELECT *
        FROM gold_symbol_summary
    """)


def get_ohlc():

    return query_dataframe("""
        SELECT *
        FROM gold_ohlc
    """)