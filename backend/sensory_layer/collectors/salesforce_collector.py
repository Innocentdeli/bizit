import asyncio
import aiohttp
from typing import AsyncGenerator
from ..event_encoder import EventEncoder, UnifiedEvent

class SalesforceCollector:
    """
    Real-time Salesforce CRM event collector using REST API and Streaming API.
    Captures: leads, opportunities, account changes.
    """
    def __init__(self, instance_url: str, access_token: str):
        self.instance_url = instance_url
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def collect_stream(self) -> AsyncGenerator[UnifiedEvent, None]:
        """Query Salesforce for recent opportunities and leads."""
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    # Query recent opportunities
                    query = "SELECT Id, Name, Amount, StageName, CloseDate FROM Opportunity WHERE LastModifiedDate = TODAY ORDER BY LastModifiedDate DESC LIMIT 10"
                    query_url = f"{self.instance_url}/services/data/v58.0/query/?q={query}"
                    
                    async with session.get(query_url, headers=self.headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            for record in data.get("records", []):
                                event = EventEncoder.encode(
                                    source="SALESFORCE",
                                    event_type="OPPORTUNITY_UPDATED",
                                    data={
                                        "opportunity_id": record["Id"],
                                        "name": record["Name"],
                                        "value": float(record.get("Amount", 0)),
                                        "stage": record["StageName"],
                                        "close_date": record.get("CloseDate")
                                    },
                                    priority=4
                                )
                                yield event
                    
                    await asyncio.sleep(60)  # Poll every minute
                    
                except Exception as e:
                    print(f"[SALESFORCE] Collection error: {e}")
                    await asyncio.sleep(120)
