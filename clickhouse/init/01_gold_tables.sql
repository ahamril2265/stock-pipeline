CREATE TABLE IF NOT EXISTS stock_analytics.gold_symbol_summary
(
    stock_symbol String,
    latest_price Float64,
    daily_volume UInt64,
    vwap Float64,
    avg_spread Float64,
    avg_latency Float64,
    buy_volume UInt64,
    sell_volume UInt64,
    last_updated DateTime
)
ENGINE = MergeTree()
ORDER BY stock_symbol;