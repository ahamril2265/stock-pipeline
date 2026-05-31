# 🚀 Real-Time Governed Streaming Lakehouse Pipeline

## 📌 Project Overview

This project implements a complete real-time data engineering platform for stock market analytics using modern lakehouse architecture principles.

The platform ingests simulated market events through Apache Kafka, validates schemas using Schema Registry and Avro serialization, processes streaming data using Apache Spark Structured Streaming, stores data in Delta Lake on MinIO object storage, and serves curated analytical datasets through ClickHouse.

The project follows a Medallion Architecture:

```text
Kafka
  ↓
Bronze Layer (Raw Delta Lake)
  ↓
Silver Layer (Business Analytics)
  ↓
Gold Layer (Serving Layer)
  ↓
Dashboard (Upcoming)
```

---

# 🏗 Architecture

```text
+--------------------+
| Avro Producers     |
|--------------------|
| Trade Events       |
| Price Ticks        |
+---------+----------+
          |
          v
+--------------------+
| Apache Kafka       |
+---------+----------+
          |
          v
+--------------------+
| Schema Registry    |
+---------+----------+
          |
          v
+--------------------+
| Spark Structured   |
| Streaming          |
+---------+----------+
          |
          v
+--------------------+
| Delta Lake         |
| Bronze Layer       |
+---------+----------+
          |
          v
+--------------------+
| Silver Layer       |
| Analytics          |
+---------+----------+
          |
          v
+--------------------+
| ClickHouse         |
| Gold Layer         |
+---------+----------+
          |
          v
+--------------------+
| Dashboard          |
| (Next Phase)       |
+--------------------+
```

---

# 🛠 Technology Stack

## Streaming

* Apache Kafka
* Apache ZooKeeper
* Confluent Schema Registry
* Avro Serialization

## Processing

* Apache Spark Structured Streaming
* Delta Lake

## Storage

* MinIO (S3 Compatible Object Storage)

## Analytics

* ClickHouse

## Infrastructure

* Docker
* Docker Compose
* WSL2 Ubuntu

## Language

* Python 3.12

---

# 📂 Data Model

## Trade Event Schema

```json
{
  "trade_id": "...",
  "stock_symbol": "...",
  "trade_price": 0,
  "trade_quantity": 0,
  "trade_type": "BUY/SELL",
  "event_timestamp": "...",
  "exchange_timestamp": "..."
}
```

## Price Tick Schema

```json
{
  "stock_symbol": "...",
  "price": 0,
  "spread": 0,
  "volume": 0,
  "event_timestamp": "..."
}
```

---

# 🥉 Bronze Layer

## Objective

Store raw immutable events exactly as received from Kafka.

## Storage Location

```text
s3://stock-data/bronze/
```

## Tables

### Trade Events

```text
bronze/namespace=com.stock.trade_events.v1
```

### Price Ticks

```text
bronze/namespace=com.stock.price_ticks.v1
```

## Characteristics

* Raw data
* Partitioned by event date
* Delta Lake format
* Replayable source of truth

---

# 🥈 Silver Layer

## Objective

Transform raw events into business-ready analytical datasets.

---

## Trade Events

```text
silver/trade_events
```

### Enhancements

* Schema validation
* Data cleansing
* Event standardization

---

## Price Events

```text
silver/price_events
```

### Enhancements

* Schema validation
* Data cleansing
* Event standardization

---

## VWAP Metrics

```text
silver/trade_vwap_metrics
```

Metrics:

* VWAP
* Total Volume

---

## Volume Metrics

```text
silver/trade_volume_metrics
```

Metrics:

* Buy Volume
* Sell Volume

---

## Latency Metrics

```text
silver/trade_latency_metrics
```

Metrics:

* Average Latency
* Maximum Latency
* P95 Latency

---

## OHLC Metrics

```text
silver/price_ohlc_1m
```

Metrics:

* Open
* High
* Low
* Close
* Total Volume

Window:

```text
1 Minute Tumbling Window
```

---

# 🔄 Replay Framework

Implemented:

```text
silver_replay.py
```

Capabilities:

* Rebuild Silver tables
* Recover failed partitions
* Backfill historical data

---

# ⚡ Optimization Framework

Implemented:

```text
optimize_silver.py
```

Capabilities:

* Delta Lake maintenance
* File compaction
* Storage optimization

---

# 🥇 Gold Layer

Gold datasets are served through ClickHouse.

---

## Gold Symbol Summary

Table:

```text
gold_symbol_summary
```

Metrics:

* Latest Price
* VWAP
* Daily Volume
* Average Spread
* Average Latency
* Buy Volume
* Sell Volume

Purpose:

```text
Per-symbol analytical summary
```

---

## Gold Market KPIs

Table:

```text
gold_market_kpis
```

Metrics:

* Total Market Volume
* Total Buy Volume
* Total Sell Volume
* Market VWAP
* Average Market Price
* Average Market Latency
* Active Symbols

Purpose:

```text
Market-wide executive dashboard metrics
```

---

## Gold Top Symbols

Table:

```text
gold_top_symbols
```

Metrics:

* Volume Ranking
* VWAP
* Latest Price
* Buy/Sell Volume

Purpose:

```text
Leaderboard and ranking analytics
```

---

## Gold OHLC

Table:

```text
gold_ohlc
```

Metrics:

* Open
* High
* Low
* Close
* Total Volume

Purpose:

```text
Charting and visualization layer
```

---

# 📊 Current Project Status

## Completed

✅ Kafka Infrastructure

✅ Schema Registry

✅ Avro Producers

✅ Trade Event Streaming

✅ Price Tick Streaming

✅ Bronze Delta Lake

✅ Silver Analytics Layer

✅ Replay Framework

✅ Optimization Framework

✅ ClickHouse Integration

✅ Gold Layer

---

# 🚧 Next Phase

## Dashboard Layer

Planned Features:

### Overview

* Market KPIs
* System Health

### Top Symbols

* Volume Rankings
* VWAP Rankings

### Symbol Analysis

* Candlestick Charts
* OHLC Visualization
* Volume Trends

### Monitoring

* Pipeline Health
* Processing Metrics
* Streaming Statistics

---

# 🎯 Learning Outcomes

This project demonstrates:

* Real-Time Streaming Architecture
* Event-Driven Data Engineering
* Schema Governance
* Structured Streaming
* Delta Lake Operations
* Medallion Architecture
* S3-Based Data Lake Design
* Analytical Data Modeling
* ClickHouse Analytics
* Failure Recovery Strategies
* Production-Oriented Data Pipelines

---

# Version

Current Version:

```text
V3.0
```

Status:

```text
Bronze ✅
Silver ✅
Gold ✅
Dashboard 🚧 Next
```
