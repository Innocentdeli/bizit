import asyncio
import time
from agents.pulse_agent import PulseAgent
from core.state import OrganismState

async def verify_pulse_pipeline():
    print("--- STARTING PULSE PIPELINE VERIFICATION ---")
    
    agent = PulseAgent()
    state = OrganismState()
    
    # 1. Mock ECON_TICK (High Volatility)
    fx_event = {
        "event_type": "ECON_TICK",
        "source": "PULSE_SENSORS",
        "payload": {
            "variable": "NGN_USD",
            "value": 1600.0,
            "change": 150.0,
            "market": "Parallel"
        },
        "timestamp": time.time()
    }
    
    print("Processing FX Event (Urgent)...")
    result = agent.propose_action(fx_event)
    print(f"Result Decision: {result['decision']}")
    print(f"Brief Headline: {result['metadata']['brief']['headline']}")
    print(f"Urgency: {result['metadata']['brief']['urgency']}")
    
    # 2. Mock SOVEREIGN_NEWS (Hawkish)
    news_event = {
        "event_type": "SOVEREIGN_NEWS",
        "source": "NEWS_FEED",
        "payload": {
            "title": "CBN Hikes Rates to 25%",
            "sentiment": "Hawkish",
            "source_hash": "ipfs://QmTest123"
        },
        "timestamp": time.time()
    }
    
    print("\nProcessing News Event (Urgent)...")
    result = agent.propose_action(news_event)
    print(f"Result Decision: {result['decision']}")
    print(f"Brief Headline: {result['metadata']['brief']['headline']}")
    print(f"Urgency: {result['metadata']['brief']['urgency']}")

if __name__ == "__main__":
    asyncio.run(verify_pulse_pipeline())
