import random
import asyncio
from typing import List, Dict, Any
from ..event_encoder import EventEncoder, UnifiedEvent

class MockCollector:
    def __init__(self):
        self.sources = ["SAP_ERP", "SALESFORCE", "SHOPIFY", "LOGISTICS_HUB"]
        self.event_types = ["ORDER_PLACED", "INVENTORY_LOW", "SHIPMENT_DELAYED", "PAYMENT_RECEIVED"]

    async def collect_stream(self):
        """Simulates a stream of business events."""
        while True:
            source = random.choice(self.sources)
            event_type = random.choice(self.event_types)
            data = {
                "id": random.randint(10000, 99999),
                "value": round(random.uniform(100.0, 10000.0), 2),
                "currency": "USD",
                "status": "pending"
            }
            priority = random.randint(1, 5)
            
            event = EventEncoder.encode(source, event_type, data, priority)
            yield event
            
            await asyncio.sleep(random.uniform(1.0, 3.0))
