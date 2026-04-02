import asyncio
from typing import AsyncGenerator, List
from .event_encoder import UnifiedEvent
from .collectors.shopify_collector import ShopifyCollector
from .collectors.salesforce_collector import SalesforceCollector
from .collectors.sap_erp_collector import SAPERPCollector
from .collectors.iot_collector import IoTCollector
from .collectors.metabolic_collector import MetabolicCollector # Level 37
from .collectors.mock_collector import MockCollector
from .collectors.pulse_collector import PulseCollector # Level 59

class UnifiedCollector:
    """
    Orchestrates multiple data sources into a single unified event stream.
    Merges events from Shopify, Salesforce, SAP, IoT, and other sources.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.collectors = []
        self.push_queue = asyncio.Queue()  # Level 11: Support for external push events
        self._initialize_collectors()
    
    def _initialize_collectors(self):
        """Initialize all configured collectors."""
        # Add real collectors if enabled and credentials are provided
        shopify_config = self.config.get("shopify", {})
        if shopify_config.get("enabled"):
            self.collectors.append(
                ShopifyCollector(
                    shop_url=shopify_config.get("shop_url"),
                    access_token=shopify_config.get("access_token")
                )
            )
        
        sf_config = self.config.get("salesforce", {})
        if sf_config.get("enabled"):
            self.collectors.append(
                SalesforceCollector(
                    instance_url=sf_config.get("instance_url"),
                    access_token=sf_config.get("access_token")
                )
            )
        
        sap_config = self.config.get("sap", {})
        if sap_config.get("enabled"):
            self.collectors.append(
                SAPERPCollector(
                    base_url=sap_config.get("base_url"),
                    username=sap_config.get("username"),
                    password=sap_config.get("password")
                )
            )
        
        # Always include IoT collector (defaults to simulation if enabled)
        iot_config = self.config.get("iot", {})
        if iot_config.get("enabled", True):
            self.collectors.append(IoTCollector(
                mqtt_broker=iot_config.get("broker", "localhost"),
                topics=iot_config.get("topics")
            ))
        
        # Always include Metabolic Monitoring (Level 37)
        self.collectors.append(MetabolicCollector())
        
        # Level 59: The Intelligence Lobe (Pulse)
        self.collectors.append(PulseCollector())
        
        # Fallback to mock if no real collectors configured
        if not self.collectors:
            print("[UNIFIED] No real collectors configured. Using MockCollector.")
            self.collectors.append(MockCollector())
    
    def push_event(self, event: UnifiedEvent):
        """
        Level 11: Manually inject an event into the unified stream (Thread-Safe).
        """
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(self.push_queue.put_nowait, event)
        except RuntimeError:
            # Fallback for when loop isn't running yet
            self.push_queue.put_nowait(event)

    async def collect_stream(self) -> AsyncGenerator[UnifiedEvent, None]:
        """
        Merge all collector streams into a single unified stream.
        Uses asyncio.gather to run collectors concurrently.
        """
        async def merge_streams():
            queues = [asyncio.Queue() for _ in self.collectors]
            queues.append(self.push_queue) # Add the manual push queue
            
            # Start all collectors
            async def collector_task(collector, queue):
                async for event in collector.collect_stream():
                    await queue.put(event)
            
            tasks = [
                asyncio.create_task(collector_task(collector, queue))
                for collector, queue in zip(self.collectors, queues[:-1]) # Don't start task for push_queue
            ]
            
            # Yield events as they arrive from any collector
            while True:
                for queue in queues:
                    if not queue.empty():
                        event = await queue.get()
                        yield event
                await asyncio.sleep(0.1)
        
        async for event in merge_streams():
            yield event
