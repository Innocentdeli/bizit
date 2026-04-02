import asyncio
import aiohttp
from typing import AsyncGenerator
from ..event_encoder import EventEncoder, UnifiedEvent

class SAPERPCollector:
    """
    Real-time SAP ERP event collector using OData API.
    Captures: purchase orders, inventory movements, financial transactions.
    """
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.auth = aiohttp.BasicAuth(username, password)
        self.headers = {"Accept": "application/json"}
    
    async def collect_stream(self) -> AsyncGenerator[UnifiedEvent, None]:
        """Poll SAP OData API for business events."""
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    # Fetch recent purchase orders
                    po_url = f"{self.base_url}/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder?$top=10&$orderby=CreationDate desc"
                    
                    async with session.get(po_url, headers=self.headers, auth=self.auth) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            for po in data.get("d", {}).get("results", []):
                                event = EventEncoder.encode(
                                    source="SAP_ERP",
                                    event_type="PURCHASE_ORDER_CREATED",
                                    data={
                                        "po_number": po.get("PurchaseOrder"),
                                        "value": float(po.get("TotalNetAmount", 0)),
                                        "currency": po.get("DocumentCurrency"),
                                        "vendor": po.get("Supplier"),
                                        "creation_date": po.get("CreationDate")
                                    },
                                    priority=5
                                )
                                yield event
                    
                    await asyncio.sleep(120)  # Poll every 2 minutes
                    
                except Exception as e:
                    print(f"[SAP_ERP] Collection error: {e}")
                    await asyncio.sleep(180)
