from agents.base_agent import BaseAgent

class NegotiationAgent(BaseAgent):
    """
    Level 21: Planetary Connectivity.
    Specialized in P2P negotiations with other Sovereign Nodes.
    """
    def __init__(self, name: str = "Diplomat-1"):
        super().__init__(name, domain="Planetary-Trade")
        self.active_negotiations = {}
        self.reputation_index = 0.95

    def evaluate_proposal(self, proposal: dict):
        """Evaluate a trade proposal from another node."""
        source_id = proposal.get("node_id")
        offer = proposal.get("offer", {}) # e.g., {"type": "compute", "amount": 100}
        request = proposal.get("request", {}) # e.g., {"type": "capital", "amount": 25000}
        
        # Simple logic: Is the value of what we get > what we give?
        # Mock valuation: Compute = 1, Capital = 0.01 (over-simplified)
        offer_val = offer.get("amount", 0) * (1 if offer.get("type") == "compute" else 0.01)
        request_val = request.get("request_amount", 0) * (1 if request.get("type") == "compute" else 0.01)
        
        confidence = self.reputation_index
        decision = "ACCEPT" if offer_val >= request_val else "COUNTER_OFFER"
        
        print(f"🤝 [NEGOTIATOR] Evaluating proposal from {source_id}: {decision}")
        
        return {
            "agent": self.name,
            "decision": decision,
            "confidence": confidence,
            "metadata": {"proposal_id": proposal.get("id"), "logic": "Value_Arbitrage"}
        }

    def reason(self, state: dict):
        """Negotiator reasons about the global market pulse."""
        event_type = state.get("event_type")
        payload = state.get("payload", {})

        if event_type == "INCOMING_TRADE_PROPOSAL":
            return self.evaluate_proposal(payload)

        return {
            "agent": self.name,
            "decision": "SCANNING_MESH_FOR_DEALS",
            "confidence": 0.95,
            "metadata": {"status": "Market_Sync_Active"}
        }
