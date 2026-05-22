import uuid
import random
import time
import threading

from datetime import datetime, UTC

from confluent_kafka.avro import AvroProducer

# -----------------------------------
# Kafka + Schema Registry
# -----------------------------------

BOOTSTRAP_SERVERS = "localhost:9092"

SCHEMA_REGISTRY_URL = "http://localhost:8081"

# -----------------------------------
# Load Schemas
# -----------------------------------

price_tick_schema = open(
    "spark/schemas/price_tick.avsc"
).read()

trade_event_schema = open(
    "spark/schemas/trade_event.avsc"
).read()

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

    # Random drift
    drift = random.uniform(-1.5, 1.5)

    new_price = round(current_price + drift, 2)

    MARKET[symbol] = new_price

    spread = round(random.uniform(0.01, 0.10), 2)

    bid_price = round(new_price - spread/2, 2)

    ask_price = round(new_price + spread/2, 2)

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

    while True:

        for symbol in MARKET.keys():

            event = generate_price_tick(symbol)

            producer.produce(
                topic="price_ticks",
                value=event,
                value_schema=price_tick_schema,
                callback=delivery_report
            )

            print(
                f"📈 PRICE "
                f"{symbol} "
                f"${event['price']}"
            )

            producer.poll(0)

        time.sleep(0.5)

# -----------------------------------
# Trade Event Thread
# -----------------------------------

def trade_event_stream():

    while True:

        symbol = random.choice(list(MARKET.keys()))

        event = generate_trade_event(symbol)

        producer.produce(
            topic="trade_events",
            value=event,
            value_schema=trade_event_schema,
            callback=delivery_report
        )

        print(
            f"💰 TRADE "
            f"{symbol} "
            f"{event['trade_type']} "
            f"${event['price']}"
        )

        producer.poll(0)

        time.sleep(1)

# -----------------------------------
# Main
# -----------------------------------

if __name__ == "__main__":

    try:

        print("🔥 Starting Unified Market Producer")

        tick_thread = threading.Thread(
            target=price_tick_stream
        )

        trade_thread = threading.Thread(
            target=trade_event_stream
        )

        tick_thread.start()

        trade_thread.start()

        tick_thread.join()

        trade_thread.join()

    except KeyboardInterrupt:

        print("🛑 Shutting down producer")

    finally:

        producer.flush()