import json
import requests

SCHEMA_REGISTRY_URL = "http://localhost:8081"

SUBJECT = "com.stock.price_ticks.v1"

with open("spark/schemas/price_tick.avsc") as f:
    schema_str = f.read()

payload = {
    "schema": schema_str
}

response = requests.post(
    f"{SCHEMA_REGISTRY_URL}/subjects/{SUBJECT}/versions",
    headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
    data=json.dumps(payload)
)

print(response.status_code)
print(response.text)