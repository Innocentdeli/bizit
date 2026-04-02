import httpx
import asyncio
import random
from datetime import datetime

API_URL = "http://localhost:8000/events"

EVENT_TYPES = ["SALE", "INVENTORY_LOW", "MARKET_SHIFT", "SUPPLY_DELAY", "CUSTOMER_FEEDBACK"]
SOURCES = ["SHOPIFY", "SAP_ERP", "SALESFORCE", "LOGISTICS_HUB", "TWITTER_SENTIMENT"]

async def send_event():
    async with httpx.AsyncClient() as client:
        event = {
            "source": random.choice(SOURCES),
            "event_type": random.choice(EVENT_TYPES),
            "data": {
                "id": random.randint(1000, 9999),
                "value": round(random.uniform(10.0, 5000.0), 2),
                "status": "active"
            },
            "priority": random.randint(1, 5)
        }
        try:
            response = await client.post(API_URL, json=event)
            print(f"Sent {event['event_type']} from {event['source']}: {response.status_code}")
        except Exception as e:
            print(f"Failed to send event: {e}")

async def main():
    print("Starting event simulation...")
    for _ in range(10):
        await send_event()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
