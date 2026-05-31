import clickhouse_connect
from datetime import datetime

client = clickhouse_connect.get_client(
    host="clickhouse",
    port=8123,
    username="admin",
    password="admin123",
    database="stock_analytics"
)

sample_data = [
    [
        'AAPL',
        192.45,
        125000,
        191.92,
        0.03,
        15.4,
        datetime.now()
    ],
    [
        'TSLA',
        246.11,
        98000,
        245.80,
        0.04,
        18.2,
        datetime.now()
    ]
]

client.insert(
    'gold_symbol_summary',
    sample_data,
    column_names=[
        'stock_symbol',
        'latest_price',
        'daily_volume',
        'vwap',
        'avg_spread',
        'avg_latency',
        'last_updated'
    ]
)

print("Gold load complete")