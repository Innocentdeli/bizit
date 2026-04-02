import psutil
import asyncio
import time
from ..event_encoder import EventEncoder, UnifiedEvent

class MetabolicCollector:
    """
    Level 6: System Metabolic Pulse.
    Monitors the 'biological cost' of the organism (CPU/RAM).
    """
    def __init__(self, interval: float = 5.0):
        self.interval = interval

    async def collect_stream(self):
        """Simulates/Monitors system metabolism."""
        print("[SENSORY] Metabolic Collector Active (Monitoring CPU/RAM)")
        while True:
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                
                source = "BIOS"
                event_type = "METABOLIC_PULSE"
                if cpu > 80:
                    event_type = "METABOLIC_STRESS_HIGH"
                
                data = {
                    "cpu": cpu,
                    "ram": ram,
                    "energy_state": "HIGH" if cpu > 80 else "NORMAL"
                }
                
                priority = 2 if cpu < 80 else 5 # High metabolic stress is high priority
                
                event = EventEncoder.encode(source, event_type, data, priority)
                yield event
                
                await asyncio.sleep(self.interval)
            except Exception as e:
                print(f"[SENSORY] Metabolic Error: {e}")
                await asyncio.sleep(5)
