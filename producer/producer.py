import json
import time
import uuid
import random
from datetime import datetime, UTC
from confluent_kafka import Producer

# Kafka config
conf = {
    'bootstrap.servers': 'localhost:9092',
    'enable.idempotence': True,
    'acks': 'all',
    'linger.ms': 5,
    'batch.size': 32768,
    'queue.buffering.max.messages': 100000
}

producer = Producer(conf)

STOCKS = ["AAPL", "GOOG", "TSLA", "AMZN", "MSFT", "NFLX", "NVDA"]

def generate_event(event_type):
    stock = random.choice(STOCKS)
    price = round(random.uniform(100, 1000), 2)
    volume = random.randint(1, 1000)

    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_time": datetime.now(UTC).isoformat(),
        "stock_symbol": stock,
        "price": price,
        "volume": volume
    }

def delivery_report(err, msg):
    if err:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [{msg.partition()}]")

def safe_produce(topic, event):
    while True:
        try:
            producer.produce(
                topic=topic,
                key=event["stock_symbol"],
                value=json.dumps(event),
                callback=delivery_report
            )
            print(f"📤 Produced: {event['event_type']} → {topic}")
            break
        except BufferError:
            print("⚠️ Buffer full, waiting...")
            producer.poll(0.1)

def produce_events():
    count = 0
    start_time = time.time()

    while True:
        safe_produce("price_ticks", generate_event("price_tick"))
        safe_produce("trade_events", generate_event("trade_executed"))

        producer.poll(0)

        count += 2

        # Print throughput every second
        if time.time() - start_time >= 1:
            print(f"🚀 Throughput: {count} events/sec")
            count = 0
            start_time = time.time()

if __name__ == "__main__":
    try:
        print("🔥 Starting producer...")
        produce_events()
    except KeyboardInterrupt:
        print("🛑 Stopping producer...")
    finally:
        producer.flush()