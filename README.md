# 📈 Real-Time Stock Market Analytics Pipeline

An end-to-end real-time stock market data engineering platform built using Kafka, Spark, Delta Lake, MinIO, ClickHouse, and Airflow.

The project simulates real-time stock market events, processes them through a Bronze-Silver-Gold architecture, and produces analytical datasets for reporting and visualization.

---

## 🚀 Project Overview

This project demonstrates a modern Data Engineering architecture capable of:

* Real-time event ingestion
* Streaming and batch processing
* Delta Lake storage
* Data quality and aggregation layers
* Analytical serving through ClickHouse
* Workflow orchestration with Airflow

---

## 🏗️ Architecture

```text
Stock Event Producers
        │
        ▼
      Kafka
        │
        ▼
  Bronze Layer
 (Raw Delta Tables)
        │
        ▼
  Silver Layer
 (Business Metrics)
        │
        ▼
   Gold Layer
(Analytics Tables)
        │
        ▼
   ClickHouse
        │
        ▼
 Dashboard / BI
```

---

## 🛠️ Technology Stack

| Component              | Technology                |
| ---------------------- | ------------------------- |
| Language               | Python                    |
| Streaming              | Apache Kafka              |
| Schema Management      | Confluent Schema Registry |
| Processing             | Apache Spark              |
| Storage                | Delta Lake                |
| Object Storage         | MinIO                     |
| Analytics Database     | ClickHouse                |
| Workflow Orchestration | Apache Airflow            |
| Containerization       | Docker & Docker Compose   |

---

## 📂 Project Structure

```text
stock-pipeline/
│
├── airflow/
│   ├── dags/
│   ├── logs/
│   └── plugins/
│
├── clickhouse/
│   └── init/
│
├── dashboard/
│
├── producers/
│   ├── stock_price_producer.py
│   └── stock_trade_producer.py
│
├── schemas/
│
├── spark/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── conf/
│
├── scripts/
│   ├── run_pipeline.sh
│   ├── run_silver.sh
│   └── run_gold.sh
│
├── Dockerfile.spark
├── docker-compose.yml
└── README.md
```

---

# Bronze Layer

The Bronze layer stores raw events exactly as received from Kafka.

### Datasets

* Price Events
* Trade Events

### Storage

```text
MinIO
└── Delta Tables
```

### Purpose

* Preserve source data
* Enable replayability
* Support downstream transformations

---

# Silver Layer

The Silver layer performs business-level transformations and metric calculations.

### Silver Datasets

#### Price Events

Processed stock price stream.

#### Trade VWAP Metrics

Calculates:

```text
VWAP = Σ(price × quantity)
       -------------------
         Σ(quantity)
```

#### Trade Volume Metrics

Computes:

* Buy Volume
* Sell Volume
* Total Volume

#### Trade Latency Metrics

Computes average processing latency.

---

# Gold Layer

The Gold layer contains business-ready analytical datasets.

## gold_symbol_summary

Per-stock analytical summary:

* Latest Price
* Daily Volume
* VWAP
* Average Spread
* Average Latency
* Buy Volume
* Sell Volume

---

## gold_market_kpis

Market-wide KPIs:

* Total Market Volume
* Total Buy Volume
* Total Sell Volume
* Market VWAP
* Average Market Price
* Average Market Latency
* Active Symbols

---

## gold_top_symbols

Top traded symbols ranked by volume.

---

## gold_ohlc

OHLC candlestick dataset:

* Open
* High
* Low
* Close
* Volume

---

# Workflow Orchestration

Apache Airflow orchestrates the complete pipeline.

### DAG Flow

```text
silver_trade
        │
        ▼
silver_price
        │
        ▼
gold_symbol_summary
        │
        ▼
gold_market_kpis
        │
        ▼
gold_top_symbols
        │
        ▼
gold_ohlc
```

### Features

* Scheduled execution
* Dependency management
* Retry handling
* Centralized monitoring

---

# Infrastructure Components

## Kafka

Used for real-time event streaming.

Topics:

```text
stock_prices
stock_trades
```

---

## Schema Registry

Manages Avro schemas and ensures schema compatibility.

---

## MinIO

S3-compatible object storage used for Delta Lake datasets.

---

## Spark

Responsible for:

* Streaming ingestion
* Silver transformations
* Gold aggregations

---

## ClickHouse

Serves analytical datasets for dashboards and reporting.

Tables:

```text
gold_symbol_summary
gold_market_kpis
gold_top_symbols
gold_ohlc
```

---

# Running the Project

## Start Infrastructure

```bash
docker compose up -d
```

---

## Run Producers

```bash
python producers/stock_price_producer.py
```

```bash
python producers/stock_trade_producer.py
```

---

## Execute Pipeline

```bash
bash scripts/run_pipeline.sh
```

---

## Access Services

### Airflow

```text
http://localhost:8088
```

### Spark UI

```text
http://localhost:8080
```

### MinIO Console

```text
http://localhost:9001
```

### ClickHouse

```text
http://localhost:8123
```

---

# Key Engineering Concepts Demonstrated

* Real-Time Data Streaming
* Event-Driven Architecture
* Bronze-Silver-Gold Design Pattern
* Delta Lake Storage
* Data Aggregation Pipelines
* Workflow Orchestration
* Containerized Data Platforms
* Analytical Data Serving

---

# Future Enhancements

* Interactive Dashboard (Dash/Plotly)
* Monitoring & Alerting
* Data Quality Validation
* CI/CD Pipeline
* Kubernetes Deployment
* Prometheus & Grafana Integration
* Real Market Data Integration

---

# Author

**Ahamed Rilwan Mohaaideen**

* LinkedIn: https://www.linkedin.com/in/ahamedrilwan
* GitHub: https://github.com/ahamril2265

---

⭐ If you found this project interesting, consider giving it a star.
