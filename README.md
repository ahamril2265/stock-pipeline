# Real-Time Governed Stock Market Lakehouse

A production-inspired streaming data platform that ingests, validates, governs, processes, and stores real-time stock market events using Apache Kafka, Schema Registry, Spark Structured Streaming, Delta Lake, and MinIO.

---

## Overview

Financial market platforms process millions of events daily.

This project demonstrates how modern data engineering systems:

- Govern event schemas
- Process real-time streams
- Handle schema evolution
- Store data in a Delta Lake architecture
- Support replay and backfill operations
- Generate analytics-ready datasets

---

## Architecture

```text
                  ┌────────────────────┐
                  │ Market Producer    │
                  │ Avro Events        │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Apache Kafka       │
                  │ price_ticks        │
                  │ trade_events       │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Schema Registry    │
                  │ Governance Layer   │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Spark Streaming    │
                  │ Bronze Engine      │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Delta Bronze Lake  │
                  │ MinIO Storage      │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Silver Processing  │
                  │ Validation         │
                  │ Deduplication      │
                  │ Window Analytics   │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Delta Silver Lake  │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Replay Engine      │
                  │ Historical Recovery│
                  └────────────────────┘
```

---

## Key Features

### Event Streaming

- Multi-topic Kafka ingestion
- High-throughput event pipelines
- Partitioned message processing

### Schema Governance

- Avro serialization
- Schema Registry integration
- Dynamic schema resolution
- Schema evolution support

### Bronze Layer

- Immutable raw storage
- Delta Lake tables
- Failure isolation

### Silver Layer

- Data validation
- Deduplication
- Windowed analytics
- VWAP calculations
- OHLC aggregation

### Replay Engine

- Point-in-time reconstruction
- Historical backfills
- Recovery workflows

### Optimization

- Delta MERGE operations
- File compaction
- Z-Ordering

---

## Tech Stack

| Layer | Technology |
|---------|-----------|
| Streaming | Apache Kafka |
| Schema Governance | Confluent Schema Registry |
| Processing | Apache Spark Structured Streaming |
| Storage | Delta Lake |
| Object Storage | MinIO |
| Analytics Store | PostgreSQL |
| Containerization | Docker |

---

## Engineering Concepts Demonstrated

- Event-Driven Architecture
- Data Contracts
- Schema Evolution
- Medallion Architecture
- Stream Processing
- Stateful Analytics
- Delta Lake Optimization
- Data Replayability
- Lakehouse Design

---

## Future Enhancements

- Gold Analytics Layer
- Grafana Monitoring
- Prometheus Metrics
- Airflow Orchestration
- Kubernetes Deployment
- Data Quality Framework
