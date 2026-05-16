import uuid
import random
import time

from datetime import datetime, UTC

from confluent_kafka.avro import AvroProducer
from confluent_kafka.avro.cached_schema_registry_client import CachedSchemaRegistryClient

# -----------------------------
# Kafka + Schema Registry Config
# -----------------------------

BOOTSTRAP_SERVERS = "localhost:9092"

SCHEMA_REGISTRY_URL = "http://localhost:8081"

TOPIC = "trade_events"

# -----------------------------
# Schema Registry Client
# -----------------------------

schema_registry = CachedSchemaRegistryClient(
    {"url": SCHEMA_REGISTRY_URL}
)

# -----------------------------
# Load Avro Schema
# -----------------------------

value_schema_str = open("../spark/schemas/trade_event.avsc").read()

# -----------------------------
# Avro Producer
# -----------------------------

producer = AvroProducer(
    {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "schema.registry.url": SCHEMA_REGISTRY_URL,

        # Reliability
        "enable.idempotence": True,
        "acks": "all",

        # Throughput
        "linger.ms": 5,
        "batch.size": 32768,

        # Stability
        "queue.buffering.max.messages": 100000
    },
    default_value_schema=value_schema_str
)

# -----------------------------
# Mock Data
# -----------------------------

STOCKS = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"]

EXCHANGES = ["NASDAQ", "NYSE"]

ORDER_TYPES = ["MARKET", "LIMIT"]

TRADE_TYPES = ["BUY", "SELL"]

# -----------------------------
# Event Generator
# -----------------------------

def generate_trade_event():

    return {
        "schema_version": "v1",

        "event_id": str(uuid.uuid4()),

        "trade_id": str(uuid.uuid4()),

        "event_type": "trade_executed",

        "event_time": datetime.now(UTC).isoformat(),

        "stock_symbol": random.choice(STOCKS),

        "price": round(random.uniform(100, 1000), 2),

        "volume": random.randint(1, 5000),

        "buyer_id": f"BUYER_{random.randint(1000,9999)}",

        "seller_id": f"SELLER_{random.randint(1000,9999)}",

        "trade_type": random.choice(TRADE_TYPES),

        "exchange": random.choice(EXCHANGES),

        "order_type": random.choice(ORDER_TYPES),

        "execution_latency_ms": random.randint(1, 50)
    }

# -----------------------------
# Delivery Callback
# -----------------------------

def delivery_report(err, msg):

    if err:
        print(f"❌ Delivery failed: {err}")

    else:
        print(
            f"✅ Delivered "
            f"topic={msg.topic()} "
            f"partition={msg.partition()} "
            f"offset={msg.offset()}"
        )

# -----------------------------
# Producer Loop
# -----------------------------

def produce_events():

    count = 0

    start = time.time()

    while True:

        event = generate_trade_event()

        producer.produce(
            topic=TOPIC,
            value=event,
            callback=delivery_report
        )

        producer.poll(0)

        count += 1

        print(
            f"📤 Produced "
            f"{event['stock_symbol']} "
            f"{event['trade_type']} "
            f"${event['price']}"
        )

        if time.time() - start >= 1:

            print(f"🚀 Throughput: {count} events/sec")

            count = 0

            start = time.time()

# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":

    try:

        print("🔥 Starting Avro Trade Producer")

        produce_events()

    except KeyboardInterrupt:

        print("🛑 Stopping Producer")

    finally:

        producer.flush()