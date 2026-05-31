# Governed & Corrective Streaming Lakehouse Platform

A multi-version, production-grade real-time market data platform engineered with a strict tiered lakehouse architecture. The system scales from raw, schema-governed stream ingestion to incremental analytical calculation, supporting stateful stream processing, dynamic schema resolution, and point-in-time replayability.

---

## 🚀 Architectural Evolution

```text
====================================== PHASE 1: GOVERNED BRONZE INGESTION ======================================

  Unified Avro Market Producer ────> Kafka Topics (price_ticks, trade_events) ────> Confluent Schema Registry
                                                                                            │
                                                                                            ▼
  Delta Bronze Lake (MinIO S3) <──── Namespace Routing <──── Unified Ingestion Spark Streaming Engine
                │
                └─> Per-Schema Quarantine Isolation Path

=================================== PHASE 2: CORRECTIVE ANALYTICAL SILVER LAYER ===================================

  Delta Bronze Lake (MinIO S3 Source of Truth)
                │
                ▼
  Incremental Silver Processors (Price & Trade Engines)
                │
                ├─► Validation (Schema conformance & payload sanity checks)
                ├─► Deduplication (Deterministic business keys)
                ├─► Watermarking & Stateless/Stateful Windows (Sliding OHLC, VWAP, Latency Profiles)
                ▼
  Optimized Delta Silver Storage ◄──── Delta MERGE Upserts & Automated Adaptive Optimization (Compaction + ZORDER)
                │
                └─► Point-In-Time Engine (Replay Suite for target timeframes / symbols) ──► Gold Ready Format

```

---

## 🛠 Multi-Phase Unified Tech Stack

| Operational Layer | Technology Component | Profile & Functionality |
| --- | --- | --- |
| **Streaming Broker** | Apache Kafka | Multi-topic partition fabric (price_ticks, trade_events) |
| **Coordination** | ZooKeeper | Broker state and topology management |
| **Processing Engine** | Apache Spark | Structured Streaming & incremental DataFrame API execution |
| **Serialization** | Apache Avro | Binary payload compaction with schema fingerprinting |
| **Governance** | Confluent Schema Registry | Runtime schema validation, caching, and TTL handling |
| **Lakehouse Format** | Delta Lake | ACID transactions, unified batch/streaming matrix, MERGE engine |
| **Object Storage** | MinIO | S3 API-compatible infrastructure staging layer |
| **Relational Storage** | PostgreSQL | Control plane, checkpoint tracking, and diagnostic metadata |
| **Containerization** | Docker | Immutable architecture definitions (docker-compose) |
| **Runtime OS** | WSL2 Ubuntu | Linux kernel execution layer |
| **Implementation Core** | Python / PySpark | End-to-end pipeline scripting and test harnesses |

---

## 📂 Project Structure

```text
stock-pipeline/
│
├── docker-compose.yml              # Cluster definition (Kafka, Schema Registry, Spark, MinIO, Postgres)
│
├── producer/
│   ├── unified_avro_producer.py    # Asynchronous, multi-threaded market trace simulation engine
│   └── schemas/
│       ├── price_tick.avsc         # Avro schema mapping bid/ask/spread telemetry 
│       └── trade_event.avsc        # Avro schema mapping execution parties and latency metrics
│
├── spark/
│   ├── unified_bronze_stream.py    # Ingestion runtime handling multi-topic discovery & schema checking
│   ├── silver_price_processor.py   # State-driven pipeline for sliding metrics, cleaning, and OHLC data
│   ├── silver_trade_processor.py   # Analytical parser computing streaming metrics and VWAP trends
│   ├── silver_replay.py            # Point-in-time state repair suite using Bronze historical data
│   └── optimize_silver.py          # Maintenance script running compaction, file pruning, and ZORDERing
│
├── scripts/
│   ├── register_price_schema.py    # Control script publishing tick schemas to the registry
│   └── register_trade_schema.py    # Control script publishing trade schemas to the registry
│
└── README.md                       # Comprehensive platform documentation

```

---

# 🏆 Phase 1: Governed Bronze Streaming Lakehouse

Phase 1 establishes the ingestion fabric, focusing on zero data loss, strict schema compliance, and low-latency storage using an advanced unified ingestion design.

### 📦 Kafka Ingestion Specifications

* **price_ticks**: Market quote and liquidity update stream. Partition count: 6.
* **trade_events**: Executed transaction verification data. Partition count: 3.
* **dlq_events**: System dead-letter queue for dead poison-pill payloads. Partition count: 1.

### 🧠 Strategic Engineering Decisions

* **Serialization**: **Apache Avro** to ensure payload compaction and wire efficiency.
* **Governance**: **Schema Registry** validation prevents schema corruption down-stream.
* **Streaming Strategy**: **Multi-topic combined stream parsing**. A single Spark worker reads directly from multiple topics, identifying schema attributes dynamically.
* **Fault Isolation**: **Per-schema quarantine directories** separate invalid payloads without failing the stream processing tasks.

---

### 🗄️ Bronze Warehouse File Layout

```text
bronze/
 ├── namespace=com.stock.price_ticks.v1/
 │      └── event_date=YYYY-MM-DD/      # Dynamic batch ingestion split
 │             └── *.parquet
 └── namespace=com.stock.trade_events.v1/
        └── event_date=YYYY-MM-DD/      # Partition isolated by system ingest date
               └── *.parquet
               
quarantine/                             # Corrupted rows are isolated here
 ├── com.stock.price_ticks.v1/
 └── com.stock.trade_events.v1/

```

---

### 🚀 Launching Phase 1

```bash
# 1. Bring up the distributed container network
docker compose up -d

# 2. Register schemas to verify your metadata contracts
python register_price_tick_schema.py
python register_trade_schema.py

# 3. Boot the market event simulation process
python producer/unified_avro_producer.py

```

Submit the streaming engine payload to the target Spark cluster:

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

---

# 🥈 Phase 2: Corrective Analytical Silver Lakehouse

Phase 2 reads raw events out of the **Bronze Delta** layer and runs transformations to produce highly polished, deduplicated, and windowed analytical data models.

```text
[Bronze Storage Table] ──► Read Stream ──► Window / Stateful Aggregations ──► Delta MERGE Upsert ──► [Optimized Silver Models]

```

### 📊 Engineered Metrics and Analytical Layouts

#### Price Analytics

* **OHLC Vector Model**: Calculated using dynamic sliding windows. Tracks open, high, low, and close values across custom spans.
* **Spread Analytics**: Calculates structural liquidity profiles over rolling windows. Logs running indicators for average spread, maximum spread, and minimum spread.

#### Trade Analytics

* **VWAP Engine**: Evaluates volume-weighted average price patterns across continuous periods.

$$\text{VWAP} = \frac{\sum (\text{Quantity} \times \text{Price})}{\sum \text{Quantity}}$$


* **Imbalance Profiling**: Gauges real-time order book velocity mismatch by cross-checking buy volume against sell volume.
* **Latency Analysis**: Calculates performance health checks for downstream execution pipelines, outputting continuous metrics for average latency, p95 latency, and maximum system latency.

---

### 📂 Silver Object Storage Topography

```text
silver/
 ├── price_events/              # Deduped and validated atomic tick records
 ├── price_ohlc_1m/             # 1-minute partitioned analytical rollups
 ├── price_ohlc_5m/             # 5-minute analytical intervals
 ├── price_ohlc_15m/            # 15-minute analytical intervals
 ├── price_ohlc_1h/             # Hourly aggregated analytical rollups
 ├── price_spread_metrics/      # Rolling spread liquidity indicators
 ├── trade_events/              # Enriched transactional row records
 ├── trade_vwap_metrics/        # Continuous Volume-Weighted Average Price metrics
 └── trade_latency_metrics/     # Continuous execution performance markers

```

---

### 🧠 V2 Engineering Decisions

* **Processing Engine Pattern**: Fully incremental **Delta-to-Delta structured streaming loops**.
* **Late Ingestion Defenses**: Implemented a **1-minute watermark matrix** paired with an explicit **10-second aggregation trigger macro**, forcing late-arriving events into historical processing slots.
* **Write Strategy**: Atomic **Delta Lake MERGE actions** to prevent row duplication on late arrivals or pipeline restarts.
* **Layout Optimizations**: Systematic file compaction and **Z-Order indexing using compound keys (stock_symbol, event_time)** to keep lookup performance stable over long intervals.

---

### 🚀 Running Phase 2 Engines

To process the analytical data layers, execute the price and trade stream transformers:

```bash
# Run the incremental streaming engines
docker exec -it spark-master /spark/bin/spark-submit \
  --master local[2] \
  --driver-memory 1G \
  --executor-memory 2G \
  --executor-cores 2 \
  /opt/spark/work-dir/silver_price_processor.py

docker exec -it spark-master /spark/bin/spark-submit \
  --master local[2] \
  --driver-memory 1G \
  --executor-memory 2G \
  --executor-cores 2 \
  /opt/spark/work-dir/silver_trade_processor.py

```

#### Running a Historical State Repair Task

If you find data errors or need to backfill metrics for past dates, run the point-in-time replay suite:

```bash
spark-submit spark/silver_replay.py --date 2026-05-22 --symbol AAPL

```

#### Triggering Storage Optimization Maintenance

To perform file compaction, remove dead transaction records, and rewrite data vectors for better query performance, execute:

```bash
spark-submit spark/optimize_silver.py

```

---

## 📈 Functional Maturity Verification

| Capability Module | Verification Status | Functional Scope |
| --- | --- | --- |
| **Multi-Topic Ingestion** | ✅ Implemented | Discovers dynamic messaging headers across multiple inputs |
| **Contract Governance** | ✅ Implemented | Validates schemas at runtime via Schema Registry mappings |
| **Dynamic Resolution** | ✅ Implemented | Automatically extracts schema IDs from binary data streams |
| **ACID Lakehouse Storage** | ✅ Implemented | Guarantees data consistency through Delta transaction logs |
| **Quarantine Isolation** | ✅ Implemented | Isolates malformed or corrupted rows to separate storage |
| **Stream Deduplication** | ✅ Implemented | Uses unique business keys to guarantee exactly-once writing |
| **Sliding Aggregations** | ✅ Implemented | Computes running real-time values like VWAP and OHLC bars |
| **Incremental Replaying** | ✅ Implemented | Rebuilds state history correctly on demand from raw records |
| **Adaptive Optimization** | ✅ Implemented | Combines small storage files and applies Z-Order indexing |

---

## 🔮 Next Phase: Gold OLAP Serving

The next stage of development expands on the Silver layer to build a high-performance **Gold Analytical Mart Layer**:

```text
[Optimized Silver Delta Layer] ──► Dynamic CDC Export ──► ClickHouse OLAP Vector Clustered Tables ──► Real-Time Business Dashboard Visuals

```

* **ClickHouse Integration**: High-speed, low-latency analytical data delivery via localized engine arrays.
* **Real-Time Dashboards**: Directly surfaces sub-second trading KPIs, volatility matrix grids, and performance trends.
* **Kubernetes Orchestration**: Migrates all streaming engines and processing workers to a cloud-native architecture managed by Airflow.