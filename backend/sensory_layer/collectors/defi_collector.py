import threading
import time
import random
import logging
from typing import Callable, List
from core.state import OrganismState

logger = logging.getLogger(__name__)

class DeFiCollector:
    """
    Tier 7: DeFi Sensory Pulse.
    Injects "On-Chain" (Synthetic/DEX) pricing into the BIZIT Sensory Stream.
    Simulates high-utility decentralized price feeds.
    """
    def __init__(self, pairs: List[str] = ["BTC_USD", "ETH_USD", "LINK_USD"], callback: Callable = None):
        self.pairs = pairs
        self.callback = callback
        self.running = True
        self.state = OrganismState()
        # Seed initial prices
        self.prices = {
            "BTC_USD": 95000.0,
            "ETH_USD": 2500.0,
            "LINK_USD": 18.0
        }

    def start(self):
        print(f"💎 [SENSORY] Starting DeFi Pulse (On-Chain Mock) for {self.pairs}")
        threading.Thread(target=self._simulate_feed, daemon=True).start()

    def _simulate_feed(self):
        while self.running:
            try:
                for pair in self.pairs:
                    # Mock volatility
                    change = random.uniform(-0.002, 0.002)
                    self.prices[pair] *= (1 + change)
                    
                    price = self.prices[pair]
                    
                    # 1. Update Core State (Grounding)
                    self.state.update_defi_quote(pair, price)
                    
                    # 2. Emit Sensory Event (Reasoning Trigger)
                    if self.callback:
                        self.callback({
                            "event_type": "DEFI_TICK",
                            "source": "CHAINLINK_MOCK",
                            "payload": {
                                "instrument": pair,
                                "price": price,
                                "change": change,
                                "slippage_estimate": random.uniform(0.0001, 0.0005),
                                "gas_priority": random.choice(["LOW", "MEDIUM", "HIGH"])
                            },
                            "timestamp": time.time(),
                            "tags": ["sovereign_defi"]
                        })
                
                time.sleep(8) # Slightly slower than raw forex to simulate block times
            except Exception as e:
                logger.error(f"DeFi Pulse Error: {e}")
                time.sleep(10)

    def stop(self):
        self.running = False
