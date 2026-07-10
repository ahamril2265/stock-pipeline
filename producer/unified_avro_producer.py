import uuid
import random
import time
import threading
import signal

from datetime import datetime, UTC

from confluent_kafka.avro import AvroProducer

# -----------------------------------
# Kafka + Schema Registry
# -----------------------------------

BOOTSTRAP_SERVERS = "kafka:29092"
SCHEMA_REGISTRY_URL = "http://schema-registry:8081"

# -----------------------------------
# Load Schemas
# -----------------------------------

with open("spark/schemas/price_tick.avsc") as f:
    price_tick_schema = f.read()

with open("spark/schemas/trade_event.avsc") as f:
    trade_event_schema = f.read()

# -----------------------------------
# Avro Producer
# -----------------------------------

producer = AvroProducer(
    {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "schema.registry.url": SCHEMA_REGISTRY_URL,

        "enable.idempotence": True,
        "acks": "all",

        "linger.ms": 5,
        "batch.size": 32768,

        "queue.buffering.max.messages": 100000
    }
)

# -----------------------------------
# Shutdown Event
# -----------------------------------

shutdown_event = threading.Event()

# -----------------------------------
# Market State
# -----------------------------------

MARKET = {
    "AAPL": 210.0,
    "TSLA": 310.0,
    "NVDA": 950.0,
    "MSFT": 420.0,
    "AMZN": 180.0
}

EXCHANGES = ["NASDAQ", "NYSE"]

MARKET_STATUS = ["OPEN"]

TICK_TYPES = [
    "QUOTE_UPDATE",
    "TRADE_UPDATE"
]

ORDER_TYPES = [
    "MARKET",
    "LIMIT"
]

TRADE_TYPES = [
    "BUY",
    "SELL"
]

# -----------------------------------
# Signal Handler
# -----------------------------------

def shutdown(signum, frame):
    print("\n🛑 Shutdown signal received...")
    shutdown_event.set()

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

# -----------------------------------
# Delivery Callback
# -----------------------------------

def delivery_report(err, msg):

    if err:
        print(f"❌ Delivery failed: {err}")

# -----------------------------------
# Price Tick Generator
# -----------------------------------

def generate_price_tick(symbol):

    current_price = MARKET[symbol]

    drift = random.uniform(-1.5, 1.5)

    new_price = round(current_price + drift, 2)

    MARKET[symbol] = new_price

    spread = round(random.uniform(0.01, 0.10), 2)

    bid_price = round(new_price - spread / 2, 2)

    ask_price = round(new_price + spread / 2, 2)

    return {

        "schema_version": "v1",

        "event_id": str(uuid.uuid4()),

        "event_type": "price_tick",

        "event_time": datetime.now(UTC).isoformat(),

        "stock_symbol": symbol,

        "price": new_price,

        "volume": random.randint(100, 5000),

        "bid_price": bid_price,

        "ask_price": ask_price,

        "spread": spread,

        "exchange": random.choice(EXCHANGES),

        "tick_type": random.choice(TICK_TYPES),

        "market_status": random.choice(MARKET_STATUS)
    }

# -----------------------------------
# Trade Event Generator
# -----------------------------------

def generate_trade_event(symbol):

    current_price = MARKET[symbol]

    return {

        "schema_version": "v1",

        "event_id": str(uuid.uuid4()),

        "trade_id": str(uuid.uuid4()),

        "event_type": "trade_executed",

        "event_time": datetime.now(UTC).isoformat(),

        "stock_symbol": symbol,

        "price": current_price,

        "volume": random.randint(1, 5000),

        "buyer_id": f"BUYER_{random.randint(1000,9999)}",

        "seller_id": f"SELLER_{random.randint(1000,9999)}",

        "trade_type": random.choice(TRADE_TYPES),

        "exchange": random.choice(EXCHANGES),

        "order_type": random.choice(ORDER_TYPES),

        "execution_latency_ms": random.randint(1, 50)
    }

# -----------------------------------
# Price Tick Thread
# -----------------------------------

def price_tick_stream():

    while not shutdown_event.is_set():

        for symbol in MARKET.keys():

            if shutdown_event.is_set():
                break

            event = generate_price_tick(symbol)

            try:

                producer.produce(
                    topic="price_ticks",
                    value=event,
                    value_schema=price_tick_schema,
                    callback=delivery_report
                )

                print(
                    f"📈 PRICE {symbol} ${event['price']}"
                )

            except BufferError:
                producer.poll(1)

            producer.poll(0)

        shutdown_event.wait(0.5)

    print("✅ Price thread stopped.")

# -----------------------------------
# Trade Event Thread
# -----------------------------------

def trade_event_stream():

    while not shutdown_event.is_set():

        symbol = random.choice(list(MARKET.keys()))

        event = generate_trade_event(symbol)

        try:

            producer.produce(
                topic="trade_events",
                value=event,
                value_schema=trade_event_schema,
                callback=delivery_report
            )

            print(
                f"💰 TRADE {symbol} "
                f"{event['trade_type']} "
                f"${event['price']}"
            )

        except BufferError:
            producer.poll(1)

        producer.poll(0)

        shutdown_event.wait(1)

    print("✅ Trade thread stopped.")

# -----------------------------------
# Main
# -----------------------------------

if __name__ == "__main__":

    print("=" * 50)
    print("🔥 STARTING UNIFIED MARKET PRODUCER")
    print("=" * 50)

    tick_thread = threading.Thread(
        target=price_tick_stream,
        name="PriceThread"
    )

    trade_thread = threading.Thread(
        target=trade_event_stream,
        name="TradeThread"
    )

    tick_thread.start()
    trade_thread.start()

    try:

        while not shutdown_event.is_set():
            time.sleep(1)

    finally:

        print("\nWaiting for worker threads...")

        tick_thread.join()
        trade_thread.join()

        print("Flushing producer...")

        producer.flush(10)

        print("✅ Kafka producer flushed.")

        print("🛑 Unified Market Producer stopped successfully.")