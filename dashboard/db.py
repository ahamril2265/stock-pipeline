import clickhouse_connect


def get_market_kpis():

    client = clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="admin",
        password="admin123",
        database="stock_analytics"
    )

    return client.query_df("""
        SELECT *
        FROM gold_market_kpis
        ORDER BY updated_at DESC
        LIMIT 1
    """)