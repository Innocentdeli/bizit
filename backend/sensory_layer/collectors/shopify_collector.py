import asyncio
import aiohttp
from typing import AsyncGenerator
from ..event_encoder import EventEncoder, UnifiedEvent

class ShopifyCollector:
    """
    Real-time Shopify event collector using Webhooks and Admin API.
    Captures: orders, inventory updates, customer events.
    """
    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url
        self.access_token = access_token
        self.api_version = "2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
    
    async def collect_stream(self) -> AsyncGenerator[UnifiedEvent, None]:
        """Poll Shopify Admin API for new orders and inventory changes."""
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    # Fetch recent orders
                    orders_url = f"{self.shop_url}/admin/api/{self.api_version}/orders.json?status=any&limit=10"
                    async with session.get(orders_url, headers=self.headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            for order in data.get("orders", []):
                                event = EventEncoder.encode(
                                    source="SHOPIFY",
                                    event_type="ORDER_PLACED",
                                    data={
                                        "order_id": order["id"],
                                        "value": float(order["total_price"]),
                                        "currency": order["currency"],
                                        "customer_email": order.get("email"),
                                        "line_items": len(order.get("line_items", []))
                                    },
                                    priority=3
                                )
                                yield event
                    
                    await asyncio.sleep(30)  # Poll every 30 seconds
                    
                except Exception as e:
                    print(f"[SHOPIFY] Collection error: {e}")
                    await asyncio.sleep(60)
