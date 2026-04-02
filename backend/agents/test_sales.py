from agents.base_agent import BaseAgent

class SalesAgent(BaseAgent):
    def __init__(self, name: str = "SalesBot-1"):
        super().__init__(name, domain="Sales")

    def reason(self, state: dict):
        return {"agent": self.name, "decision": "TEST", "confidence": 1.0, "metadata": {}}
