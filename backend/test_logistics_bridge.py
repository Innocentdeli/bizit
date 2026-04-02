import sys
sys.path.append(".")
import logging
from backend.agents.logistics_agent import LogisticsAgent
from backend.actuation_layer.logistics_bridge import LogisticsBridge

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_logistics_integration():
    print("🚚 Testing Level 36: Logistics Bridge (Physical Body)...")
    
    # 1. Test Bridge Directly
    print("\n[TEST 1] Logistics Bridge Quote Generation")
    bridge = LogisticsBridge(mode="SANDBOX")
    quote = bridge.get_shipping_quote("New York, NY", "London, UK", 15.0)
    
    if quote.get("best_option"):
        best = quote["best_option"]
        print(f"✅ Bridge Success: Best option is {best['carrier']} (${best['price']}) ETA: {best['eta_days']} days")
    else:
        print(f"❌ Bridge Failed: {quote}")

    # 2. Test Agent Reasoning
    print("\n[TEST 2] Logistics Agent Autonomous Routing")
    agent = LogisticsAgent()
    
    # Simulate a shipment request event
    simulated_state = {
        "event_type": "SHIPMENT_REQUEST",
        "payload": {
            "origin": "Warehouse A (Seattle)",
            "destination": "Customer (Miami)",
            "weight": 5.0
        }
    }
    
    decision = agent.reason(simulated_state)
    
    if decision["decision"] == "ROUTING_LOGISTICS":
        meta = decision["metadata"]
        print(f"✅ Agent Success: Decided to Route via {meta['best_carrier']}")
        print(f"   > Estimated Cost: ${meta['price_estimate']}")
        print(f"   > Bridge Mode: {meta['bridge_mode']}")
    else:
        print(f"❌ Agent Failed: Decision was {decision['decision']}")

if __name__ == "__main__":
    test_logistics_integration()
