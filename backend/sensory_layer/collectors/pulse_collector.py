import threading
import time
import random
import logging
from typing import Callable, List

logger = logging.getLogger(__name__)

class PulseCollector:
    """
    Level 59: Sovereign Intelligence Pulse.
    Injects Nigerian/African macro-economic signals (FX, Policy, News) 
    into the BIZIT Sensory Stream.
    """
    def __init__(self, callback: Callable = None):
        self.callback = callback
        self.running = True
        self.last_fx_rate = 1450.0  # NGN/USD
        
        # Mock Nigerian News Bank
        self.news_pool = [
            {"title": "CBN Announces Policy Rate Increase", "impact": "Hawkish", "trust": 0.98},
            {"title": "Naira Gains Strength in Parallel Market", "impact": "Positive", "trust": 0.95},
            {"title": "Fuel Subsidy Removal Debate Intensifies", "impact": "Volatile", "trust": 0.92},
            {"title": "Lagos State Announces New Infrastructure Bond", "impact": "Investment", "trust": 0.99},
            {"title": "Inflation Hits 3-Year High in Q1 Report", "impact": "Negative", "trust": 0.97}
        ]

    def start(self):
        print("🌍 [SENSORY] Starting BIZIT Pulse Collector (Nigeria Context)...")
        threading.Thread(target=self._generate_signals, daemon=True).start()

    def _generate_signals(self):
        while self.running:
            try:
                # 1. Generate FX Ticks
                fx_change = random.uniform(-15.0, 15.0)
                self.last_fx_rate += fx_change
                
                if self.callback:
                    # Emit FX Signal
                    self.callback({
                        "event_type": "ECON_TICK",
                        "source": "PULSE_SENSORS",
                        "payload": {
                            "variable": "NGN_USD",
                            "value": self.last_fx_rate,
                            "change": fx_change,
                            "market": "Parallel"
                        },
                        "timestamp": time.time(),
                        "tags": ["macro_economics", "nigeria"]
                    })
                    
                    # 2. Occasional News Injection (15% chance per tick)
                    if random.random() < 0.15:
                        news = random.choice(self.news_pool)
                        self.callback({
                            "event_type": "SOVEREIGN_NEWS",
                            "source": "VANGUARD_MOCK_FEED",
                            "payload": {
                                "title": news["title"],
                                "sentiment": news["impact"],
                                "source_hash": f"ipfs://QmSource{random.randint(1000, 9999)}"
                            },
                            "timestamp": time.time(),
                            "tags": ["policy", "nigeria"]
                        })
                
                time.sleep(12) # Tactical delay for observation
            except Exception as e:
                logger.error(f"Pulse Collector Error: {e}")
                time.sleep(10)

    def stop(self):
        self.running = False
