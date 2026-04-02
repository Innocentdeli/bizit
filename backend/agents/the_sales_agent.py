from agents.base_agent import BaseAgent

class SalesAgent(BaseAgent):
    def __init__(self, name: str = "SalesBot-1"):
        super().__init__(name, domain="Sales")

    def reason(self, state: dict):
        event_type = state.get("event_type", "")
        payload = state.get("payload", {})
        value = payload.get("value", 0)
        
        decision = "GENERATING_LEAD"
        metadata = {}
        confidence = 0.85

        if "ORDER" in event_type or "SALE" in event_type:
            decision = "PROCESS_ORDER"
            metadata = {"order_id": payload.get("id"), "revenue": value}
            confidence = 0.95
        
        elif "LEAD" in event_type or "CUSTOMER" in event_type:
            decision = "RE-ENGAGE_CUSTOMER"
            metadata = {"customer_segment": "high_value", "last_contact": "30d"}
            confidence = 0.90

        elif "MARKET" in event_type:
            decision = "MONITOR_TREND"
            metadata = {"symbol": payload.get("symbol"), "price": value}
            confidence = 0.80
        
        else:
            decision = "RE-ENGAGE_CUSTOMER"
            metadata = {"fallback": True}
            confidence = 0.80

        return {
            "agent": self.name,
            "decision": decision,
            "confidence": confidence,
            "metadata": metadata
        }
