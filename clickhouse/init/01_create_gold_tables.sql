CREATE DATABASE IF NOT EXISTS stock_analytics;

-- =====================================================
-- GOLD SYMBOL SUMMARY
-- =====================================================

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

-- =====================================================
-- GOLD MARKET KPIS
-- =====================================================

CREATE TABLE IF NOT EXISTS stock_analytics.gold_market_kpis
(
    total_market_volume UInt64,

    total_buy_volume UInt64,
    total_sell_volume UInt64,

    avg_market_price Float64,
    market_vwap Float64,

    avg_market_latency Float64,

    active_symbols UInt32,

    updated_at DateTime
)
ENGINE = MergeTree()
ORDER BY updated_at;

-- =====================================================
-- GOLD TOP SYMBOLS
-- =====================================================

CREATE TABLE IF NOT EXISTS stock_analytics.gold_top_symbols
(
    stock_symbol String,

    latest_price Float64,

    total_volume UInt64,

    buy_volume UInt64,
    sell_volume UInt64,

    vwap Float64,

    volume_rank UInt32,

    updated_at DateTime
)
ENGINE = MergeTree()
ORDER BY (volume_rank, stock_symbol);

-- =====================================================
-- GOLD OHLC
-- =====================================================

CREATE TABLE IF NOT EXISTS stock_analytics.gold_ohlc
(
    window_start DateTime,
    window_end DateTime,

    stock_symbol String,

    open_price Float64,
    high_price Float64,
    low_price Float64,
    close_price Float64,

    total_volume UInt64,

    updated_at DateTime
)
ENGINE = MergeTree()
ORDER BY (stock_symbol, window_start);