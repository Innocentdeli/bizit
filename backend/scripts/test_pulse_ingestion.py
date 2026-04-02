import asyncio
import time
from sensory_layer.collectors.pulse_collector import PulseCollector
from sensory_layer.event_encoder import UnifiedEvent

async def test_pulse_ingestion():
    print("--- STARTING PULSE INGESTION TEST ---")
    
    events_received = []
    
    def callback(event_dict):
        print(f"[CALLBACK] Received: {event_dict['event_type']} - {event_dict['payload'].get('title', event_dict['payload'].get('variable'))}")
        events_received.append(event_dict)

    collector = PulseCollector(callback=callback)
    collector.start()
    
    print("Waiting for signals (30s)...")
    await asyncio.sleep(30)
    
    collector.stop()
    
    if len(events_received) > 0:
        print(f"SUCCESS: Received {len(events_received)} pulse events.")
    else:
        print("FAILURE: No events received.")

if __name__ == "__main__":
    asyncio.run(test_pulse_ingestion())
