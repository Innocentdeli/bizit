from typing import Dict, Any
from agents.base_agent import BaseAgent
from actuation_layer.logistics_bridge import LogisticsBridge

class LogisticsAgent(BaseAgent):
    def __init__(self):
        super().__init__("LogisticsBot-1", "logistics")
        self.bridge = LogisticsBridge(mode="SANDBOX")

    def reason(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize fleet routing, warehouse allocation, and last-mile delivery.
        Level 36: Integrated with LogisticsBridge for physical world actuation.
        """
        event_type = state.get("event_type", "")
        payload = state.get("payload", {})
        
        decision = "NO_ACTION"
        confidence = 0.5
        metadata = {}
        
        if "SHIPMENT" in event_type or "LOCATION" in event_type or "LOGISTICS" in event_type:
            # Autonomous Routing with LogisticsBridge
            if payload.get("origin") and payload.get("destination"):
                quote = self.bridge.get_shipping_quote(
                    origin=payload["origin"], 
                    destination=payload["destination"], 
                    weight_kg=payload.get("weight", 10.0)
                )
                
                decision = "ROUTING_LOGISTICS"
                metadata = {
                    "origin": payload["origin"],
                    "destination": payload["destination"],
                    "best_carrier": quote["best_option"]["carrier"],
                    "price_estimate": quote["best_option"]["price"],
                    "eta_days": quote["best_option"]["eta_days"],
                    "bridge_mode": self.bridge.mode
                }
                confidence = 0.95
            else:
                decision = "AWAITING_COORDINATES"
                confidence = 0.1
            
        elif "INVENTORY" in event_type:
            decision = "REBALANCE_STOCK"
            metadata = {"from": "WH_EAST", "to": "WH_WEST", "units": 100}
            confidence = 0.85
            
        return {
            "agent": self.name,
            "decision": decision,
            "confidence": confidence,
            "metadata": metadata
        }
