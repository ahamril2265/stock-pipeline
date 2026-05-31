

# 🚀 Real-Time Stock Data Pipeline (DE Core)

## 📌 Overview

This project implements a **real-time data pipeline** simulating stock market events using:

* Kafka → Streaming ingestion
* Spark → Processing (Structured Streaming)
* MinIO (S3) → Data lake storage
* Docker → Environment orchestration

---

# 🧱 Architecture

```
Producer (Python)
        ↓
Kafka (price_ticks, trade_events)
        ↓
Spark Structured Streaming
        ↓
MinIO (S3)
   ├── bronze/
   └── checkpoints/
```

---

## 🔁 Data Flow

1. Producer generates events (`price_tick`, `trade_executed`)
2. Kafka stores events in topics
3. Spark consumes from Kafka
4. Spark parses + writes to MinIO (Bronze layer)
5. Checkpoints maintain fault tolerance

---

# ⚙️ Tech Stack

| Layer             | Technology                 |
| ----------------- | -------------------------- |
| Producer          | Python + confluent-kafka   |
| Streaming         | Kafka                      |
| Processing        | Spark Structured Streaming |
| Storage           | MinIO (S3-compatible)      |
| Orchestration     | Docker                     |
| Database (future) | PostgreSQL                 |

---

# 📦 Kafka Topics

| Topic          | Purpose                            |
| -------------- | ---------------------------------- |
| `price_ticks`  | High-frequency stock price updates |
| `trade_events` | Executed trades                    |
| `dlq_events`   | Failed / invalid records (future)  |

---

# 🐳 Docker Services

* Zookeeper
* Kafka
* Spark Master + Worker
* MinIO
* PostgreSQL

---

# 🚀 SETUP INSTRUCTIONS (FROM SCRATCH)

## 🔹 1. Clean Environment

```bash
docker-compose down -v
docker system prune -a --volumes -f
```

---

## 🔹 2. Start Services

```bash
docker-compose up -d
```

---

## 🔹 3. Verify Containers

```bash
docker ps
```

---

## 🔹 4. Create Kafka Topics

```bash
docker exec -it kafka kafka-topics --create \
--topic price_ticks \
--bootstrap-server kafka:29092 \
--partitions 50 \
--replication-factor 1

docker exec -it kafka kafka-topics --create \
--topic trade_events \
--bootstrap-server kafka:29092 \
--partitions 25 \
--replication-factor 1
```

---

## 🔹 5. Setup MinIO Bucket

```bash
docker exec -it minio sh
mc alias set myminio http://localhost:9000 admin admin123
mc mb myminio/stock-data
exit
```

---

## 🔹 6. Run Producer

```bash
python producer.py
```

✔ Expected:

```
📤 Produced: price_tick → price_ticks
🚀 Throughput: X events/sec
```

---

## 🔹 7. Run Spark Streaming

```bash
docker exec -it spark-master /spark/bin/spark-submit \
  --master local[*] \
  --driver-memory 4G \
  --executor-memory 8G \
  --executor-cores 4 \
  --conf spark.sql.shuffle.partitions=100 \
  --conf spark.default.parallelism=100 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.hadoop:hadoop-aws:3.3.1 \
  /opt/spark/work-dir/bronze_stream.py
```

---

# 📂 Output Structure (MinIO)

```
stock-data/
 ├── bronze/
 │    └── price_ticks/
 │         ├── stock_symbol=AAPL/
 │         ├── stock_symbol=TSLA/
 │
 └── checkpoints/
```

---

# 🧠 KEY IMPLEMENTATION DETAILS

## ✔ Kafka Configuration (Dual Listener)

```yaml
KAFKA_LISTENERS: PLAINTEXT://:29092,PLAINTEXT_HOST://:9092
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
```

| Client            | Address        |
| ----------------- | -------------- |
| Producer (host)   | localhost:9092 |
| Spark (container) | kafka:29092    |

---

## ✔ Spark Streaming Config

* Uses Structured Streaming (not DStreams)
* Micro-batch execution
* Backpressure handled automatically

---

## ✔ S3 (MinIO) Integration

```python
.config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
.config("spark.hadoop.fs.s3a.access.key", "admin")
.config("spark.hadoop.fs.s3a.secret.key", "admin123")
.config("spark.hadoop.fs.s3a.path.style.access", "true")
.config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
```

---

# ⚠️ COMMON ERRORS + FIXES

## ❌ `localhost:9092` inside Spark

👉 Fix Kafka advertised listeners

---

## ❌ `NoSuchBucket`

👉 Create bucket manually in MinIO

---

## ❌ `403 Forbidden`

👉 Check:

* credentials
* path-style access
* bucket exists

---

## ❌ `BufferError: Queue full`

👉 Add:

```python
producer.poll(0)
```

---

## ❌ Spark slow / lagging

```text
Current batch is falling behind
```

👉 Not an error — system under load

---

# ⚡ PERFORMANCE TUNING

| Parameter            | Value                    |
| -------------------- | ------------------------ |
| maxOffsetsPerTrigger | 100 → increase for scale |
| trigger interval     | 10 sec                   |
| partitions           | 50 (price_ticks)         |
| Spark memory         | 12GB total               |

---

# 📈 CURRENT CAPABILITIES

✔ Real-time ingestion
✔ Structured streaming
✔ S3-based data lake
✔ Backpressure handling
✔ Partitioned storage

---

# 🚧 NEXT STEPS (NOT DONE YET)

## 🔥 Silver Layer

* Deduplication (event_id + event_time)
* Watermark (2 min)
* Late data handling
* DLQ routing

---

## 🔥 Gold Layer

* Aggregations (rolling average)
* Anomaly detection
* Business metrics

---

## 🔥 Dashboard

* HTML + CSS frontend
* Real-time charts

---

# 🧠 KEY LEARNINGS

* Kafka advertised listeners are critical
* Docker networking ≠ localhost
* Structured Streaming ≠ DStreams
* S3 requires manual bucket creation
* Backpressure is automatic in Spark

---

# 🎯 FINAL STATUS

| Layer        | Status |
| ------------ | ------ |
| Producer     | ✅      |
| Kafka        | ✅      |
| Spark        | ✅      |
| MinIO        | ✅      |
| Bronze Layer | ✅      |
| Silver Layer | ⏳ Next |

---

# 🧭 HOW TO RESUME LATER

If you return after months:

1. Run Docker
2. Create topics
3. Create MinIO bucket
4. Run producer
5. Run Spark

👉 Pipeline will work again

