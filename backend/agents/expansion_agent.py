from typing import Dict, Any
from agents.base_agent import BaseAgent

class ExpansionAgent(BaseAgent):
    """
    Agent specialized in Geographic Expansion (Phase 4).
    Handles autonomous market entry and regional risk management.
    """
    def __init__(self):
        super().__init__("ExpansionOfficer", "Expansion")
        self.regional_data = {
            "GLOBAL_ALPHA": {"currency": "USD", "port_latency": 0, "volatility": 0.01}
        }

    def reason(self, state: Dict[str, Any]):
        event_type = state.get("event_type", "")
        payload = state.get("payload", {})
        
        decision = "ANALYZING_MARKET"
        metadata = {}
        confidence = 0.85

        if "EXPANSION" in event_type or "MARKET_ENTRY" in event_type:
            target = payload.get("location", "GLOBAL_ALPHA")
            region = self.regional_data.get(target, self.regional_data["GLOBAL_ALPHA"])
            
            decision = f"ESTABLISH_REGIONAL_HUB_{target}"
            metadata = {
                "target_location": target,
                "hub_type": "LOGISTICS_CENTER",
                "estimated_setup_time": f"{region['port_latency'] + 30} days",
                "fx_risk_mitigation": "HEDGE_6_MONTHS",
                "local_currency": region["currency"]
            }
            confidence = 0.92
            
        elif "LOGISTICS" in event_type:
            decision = "OPTIMIZE_REGIONAL_ROUTING"
            metadata = {"port": "PRIMARY_HUB", "action": "SWITCH_TO_AIR_FREIGHT", "reason": "METABOLIC_LATENCY_THRESHOLD"}
            confidence = 0.88

        return {
            "agent": self.name,
            "decision": decision,
            "confidence": confidence,
            "metadata": metadata
        }
