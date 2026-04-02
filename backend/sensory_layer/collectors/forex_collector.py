import threading
import time
import logging
from typing import Callable, List
from api_integrations.forex_client import ForexClient
from core.state import OrganismState

logger = logging.getLogger(__name__)

class ForexCollector:
    """
    Level 37: Forex Sensory Pulse.
    Injects real-time OANDA pricing into the BIZIT Sensory Stream.
    """
    def __init__(self, pairs: List[str] = ["EUR_USD", "GBP_USD", "USD_JPY"], callback: Callable = None):
        self.pairs = pairs
        self.callback = callback
        self.running = True
        self.client = ForexClient()
        self.state = OrganismState()

    def start(self):
        print(f"📈 [SENSORY] Starting Forex Pulse for {self.pairs}")
        threading.Thread(target=self._pull_quotes, daemon=True).start()

    def _pull_quotes(self):
        while self.running:
            try:
                quotes = self.client.get_live_quotes(self.pairs)
                if quotes:
                    for pair, data in quotes.items():
                        # 1. Update Core State (Grounding)
                        self.state.update_market_quote(pair, data)
                        
                        # 2. Emit Sensory Event (Reasoning Trigger)
                        if self.callback:
                            self.callback({
                                "event_type": "FOREX_TICK",
                                "source": "OANDA",
                                "payload": {
                                    "instrument": pair,
                                    "bid": data["bid"],
                                    "ask": data["ask"],
                                    "mid": (data["bid"] + data["ask"]) / 2,
                                    "timestamp": data["timestamp"]
                                }
                            })
                
                time.sleep(5) # Poll every 5 seconds
            except Exception as e:
                logger.error(f"Forex Pulse Error: {e}")
                time.sleep(10)

    def stop(self):
        self.running = False
