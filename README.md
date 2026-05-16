# Real-Time Governed Streaming Lakehouse Pipeline

## 📌 Project Overview

This project is a real-time governed streaming data platform built using:

* Apache Kafka
* Apache Spark Structured Streaming
* Schema Registry
* Avro Serialization
* Delta Lake
* MinIO (S3-compatible object storage)
* PostgreSQL
* Docker + WSL2

The system simulates a realistic stock market event platform capable of:

* Ingesting multiple event streams
* Dynamically resolving schemas
* Governed Avro event serialization
* Multi-topic stream processing
* Bronze Lakehouse ingestion
* Quarantine-based failure isolation

---

## 🧠 Architecture

```text
                ┌────────────────────┐
                │ Unified Avro       │
                │ Market Producer    │
                └─────────┬──────────┘
                          │
          ┌───────────────┴──────────────── biographies ┐
          │                                             │
          ▼                                             ▼

   Kafka Topic:                                  Kafka Topic:
     price_ticks                                  trade_events

          │                                             │
          └───────────────┬─────────────────────────────┘
                          ▼

              ┌─────────────────────┐
              │ Schema Registry     │
              │ Dynamic Resolution  │
              └─────────┬───────────┘
                        ▼

          ┌────────────────────────────┐
          │ Unified Spark Bronze Engine│
          │                            │
          │ - Dynamic topic discovery  │
          │ - Schema introspection     │
          │ - Avro decoding            │
          │ - Delta Bronze writes      │
          │ - Quarantine isolation     │
          └─────────────┬──────────────┘
                        ▼

             ┌──────────────────┐
             │ Delta Bronze Lake│
             │      MinIO       │
             └──────────────────┘

```

---

## 🧱 Tech Stack

| Component | Technology |
| --- | --- |
| **Streaming Broker** | Apache Kafka |
| **Coordination** | ZooKeeper |
| **Stream Processing** | Apache Spark Structured Streaming |
| **Serialization** | Apache Avro |
| **Schema Governance** | Confluent Schema Registry |
| **Lakehouse Format** | Delta Lake |
| **Object Storage** | MinIO |
| **Database** | PostgreSQL |
| **Containerization** | Docker |
| **Linux Runtime** | WSL2 Ubuntu |
| **Language** | Python |

---

## 📂 Project Structure

```text
stock-pipeline/
│
├── docker-compose.yml
│
├── producer/
│   ├── unified_avro_producer.py
│   └── schemas/
│       ├── trade_event.avsc
│       └── price_tick.avsc
│
├── spark/
│   ├── unified_bronze_stream.py
│   └── schemas/
│       ├── trade_event.avsc
│       └── price_tick.avsc
│
├── scripts/
│   ├── register_trade_schema.py
│   └── register_price_schema.py
│
└── README.md

```

---

## 🚀 Event Streams

### 1️⃣ `price_ticks`

High-frequency market price updates.

#### Features

* Bid/ask spread simulation
* Market status tracking
* Exchange routing
* Realistic drift simulation

#### Example Event

```json
{
  "schema_version": "v1",
  "event_id": "uuid",
  "event_type": "price_tick",
  "event_time": "2026-05-17T12:00:00Z",
  "stock_symbol": "AAPL",
  "price": 212.44,
  "volume": 1400,
  "bid_price": 212.40,
  "ask_price": 212.48,
  "spread": 0.08,
  "exchange": "NASDAQ",
  "tick_type": "QUOTE_UPDATE",
  "market_status": "OPEN"
}

```

### 2️⃣ `trade_events`

Executed trade events.

#### Features

* Buyer/seller tracking
* Trade execution metadata
* Order types
* Execution latency simulation

#### Example Event

```json
{
  "schema_version": "v1",
  "event_id": "uuid",
  "trade_id": "uuid",
  "event_type": "trade_executed",
  "event_time": "2026-05-17T12:00:00Z",
  "stock_symbol": "TSLA",
  "price": 311.22,
  "volume": 500,
  "buyer_id": "BUYER_1001",
  "seller_id": "SELLER_2001",
  "trade_type": "BUY",
  "exchange": "NASDAQ",
  "order_type": "LIMIT",
  "execution_latency_ms": 12
}

```

---

## 🧠 Key Engineering Decisions

| Area | Decision |
| --- | --- |
| **Serialization** | Avro |
| **Governance** | Schema Registry |
| **Streaming Format** | Multi-topic |
| **Spark Architecture** | Unified ingestion engine |
| **Schema Resolution** | Dynamic schema ID introspection |
| **Failure Handling** | Per-schema quarantine |
| **Storage Format** | Delta Lake |
| **Routing Strategy** | Namespace + event_date |
| **Schema Cache** | In-memory rich cache |
| **Cache Refresh** | TTL refresh |
| **Parsing Strategy** | Group-by-schema-id |
| **Producer Model** | Async threaded dispatch |

---

## 📦 Kafka Topics

| Topic | Purpose | Partitions |
| --- | --- | --- |
| `price_ticks` | Market tick stream | 6 |
| `trade_events` | Trade execution stream | 3 |
| `dlq_events` | Dead-letter queue | 1 |

---

## 🗄️ Bronze Lake Structure

```text
bronze/
 ├── namespace=com.stock.price_ticks.v1/
 │      └── event_date=YYYY-MM-DD/
 │
 └── namespace=com.stock.trade_events.v1/
        └── event_date=YYYY-MM-DD/

```

---

## ⚠️ Quarantine Structure

Malformed or failed records are isolated seamlessly.

```text
quarantine/
 ├── com.stock.price_ticks.v1/
 └── com.stock.trade_events.v1/

```

---

## 🚀 Setup Instructions

### 1️⃣ Start Docker Services

```bash
docker compose up -d

```

### 2️⃣ Verify Containers

```bash
docker ps

```

**Expected Output Containers:**

* `kafka`
* `zookeeper`
* `schema-registry`
* `spark-master`
* `spark-worker`
* `postgres`
* `minio`

### 3️⃣ Create MinIO Bucket

Enter MinIO container shell:

```bash
docker exec -it minio sh

```

Configure local alias:

```bash
mc alias set myminio http://localhost:9000 admin admin123

```

Create the target storage bucket:

```bash
mc mb myminio/stock-data

```

### 4️⃣ Create Kafka Topics

* **price_ticks**
```bash
docker exec -it kafka kafka-topics \
--create \
--topic price_ticks \
--bootstrap-server localhost:9092 \
--partitions 6 \
--replication-factor 1

```


* **trade_events**

```bash
    docker exec -it kafka kafka-topics \
    --create \
    --topic trade_events \
    --bootstrap-server localhost:9092 \
    --partitions 3 \
    --replication-factor 1
    ```

### 5️⃣ Register Schemas
*   **Register trade schema:**
    ```bash
    python register_trade_schema.py
    ```
*   **Register price tick schema:**
    ```bash
    python register_price_schema.py
    ```

### 6️⃣ Start Unified Producer
```bash
python unified_avro_producer.py

```

**Expected stdout:**

```text
📈 PRICE AAPL $211.22
💰 TRADE TSLA BUY $310.45

```

### 7️⃣ Start Unified Bronze Engine

```bash
docker exec -it spark-master /spark/bin/spark-submit \
  --master local[2] \
  --driver-memory 1G \
  --executor-memory 2G \
  --executor-cores 2 \
  --conf spark.sql.shuffle.partitions=8 \
  --conf spark.default.parallelism=4 \
  --conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension \
  --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog \
  --packages \
org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,\
org.apache.spark:spark-avro_2.12:3.3.0,\
io.delta:delta-core_2.12:2.1.0,\
org.apache.hadoop:hadoop-aws:3.3.1 \
  /opt/spark/work-dir/unified_bronze_stream.py

```

### 🔍 Verify Bronze Data

```bash
docker exec -it minio sh
mc alias set myminio http://localhost:9000 admin admin123
mc ls myminio/stock-data/bronze

```

---

## 🧠 Current System Capabilities

### ✅ Implemented

* Real-time Kafka ingestion
* Multi-topic streaming
* Avro serialization
* Schema Registry integration
* Dynamic schema resolution
* Unified Spark ingestion engine
* Delta Bronze lakehouse
* Namespace-based routing
* Quarantine isolation
* Async market simulation
* Schema caching
* Grouped schema parsing

### 🚧 Planned Future Work

* **Silver Layer**
* Deduplication
* Watermarking
* Late event handling
* Aggregations


* **Gold Layer**
* Dashboards
* Analytics
* Trading KPIs
* Volatility metrics


* **Advanced Features**
* Replay engine
* CDC Ingestion
* ML anomaly detection
* Data quality framework
* Observability stack
* Airflow orchestration
* Kubernetes deployment



---

## ⚡ Performance Notes

### Local Development Profile

Recommended minimum configurations:

* **WSL memory limit:** 8GB
* **Spark driver memory:** 1G
* **Executor memory:** 2G

---

## 🛠 Useful Commands

* **Shutdown WSL:**
```bash
wsl --shutdown

```


* **Restart Docker Stack:**
```bash
docker compose down -v
docker compose up -d

```


* **Check Active Kafka Topics:**

```bash
    docker exec -it kafka kafka-topics \
    --bootstrap-server localhost:9092 \
    --list
    ```

---

## 📚 Concepts Covered
This project demonstrates operational competency in:
*   Event-driven architecture
*   Schema governance
*   Streaming ingestion
*   Lakehouse architecture
*   Dynamic schema resolution
*   Structured streaming
*   Delta Lake engineering
*   Distributed systems design
*   Failure isolation
*   Real-time analytics foundations

---

## 🎯 Final Goal
Build a production-grade real-time market data platform capable of enterprise-grade reliability, low-latency processing, replayable pipelines, scalable ingestion, and governed event streaming.

```