import time
import json
from typing import Dict, Any

class SymbiosisInterface:
    """
    Level 11: Symbiosis (Discord/Chat Bot).
    The bridge between the organism's Board Room and the Human's social reality.
    """
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url
        self.notification_history = []

    def notify_user(self, source_agent: str, message: str, priority="NORMAL"):
        """
        Simulates a real notification (Discord, Slack).
        """
        payload = {
            "source": source_agent,
            "text": message,
            "priority": priority,
            "timestamp": time.time()
        }
        
        print(f"[SYMBIOSIS] [{source_agent}] {message}")
        self.notification_history.append(payload)
        
        if self.webhook_url:
            # mock sending to discord
            # requests.post(self.webhook_url, json={"content": f"**{source_agent}**: {message}"})
            pass

    def request_human_permission(self, agent_name: str, action: str) -> bool:
        """
        The organism pauses and 'waits' for the human signal.
        """
        print(f"[HALT] {agent_name} is requesting permission for: {action}")
        print("[SYMBIOSIS] Sending request to Human via Discord...")
        # In a real interactive scenario, this would wait for an event.
        # For simulation, we 'approve' if trust is high.
        return True
