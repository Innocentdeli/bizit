from agents.base_agent import BaseAgent

class OperationsAgent(BaseAgent):
    def __init__(self, name: str = "OpsBot-1"):
        super().__init__(name, domain="Operations")

    def reason(self, state: dict):
        event_type = state.get("event_type", "")
        payload = state.get("payload", {})
        
        decision = "ANALYZING"
        metadata = {}
        confidence = 0.85

        if "INVENTORY" in event_type or "STOCK" in event_type or "DEMAND" in event_type:
            decision = "REORDER_INVENTORY"
            metadata = {"sku": payload.get("sku", "WIDGET_Z"), "quantity": 50, "reason": "LOW_STOCK_THRESHOLD"}
            confidence = 0.95
        
        else:
            decision = "NO_ACTION"
            metadata = {"reason": "NO_OPERATIONAL_SIGNAL"}
            confidence = 0.5

        return {
            "agent": self.name,
            "decision": decision,
            "confidence": confidence,
            "metadata": metadata
        }
