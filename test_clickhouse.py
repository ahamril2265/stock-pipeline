# test_clickhouse.py

import clickhouse_connect

client = clickhouse_connect.get_client(
    host="localhost",   # use localhost first
    port=8123,
    username="admin",
    password="admin123",
    database="stock_analytics"
)

print(client.command("SELECT 1"))