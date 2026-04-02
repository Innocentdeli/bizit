from typing import Dict, Any
from enum import Enum
import time

class SubscriptionTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionManager:
    """
    Enforces the SaaS Business Model constraints.
    Checks if the user is allowed to spawn more agents or process more events.
    """
    LIMITS = {
        SubscriptionTier.FREE: {"max_agents": 2, "max_autonomy": "approval_only", "events_per_minute": 60},
        SubscriptionTier.PRO: {"max_agents": 10, "max_autonomy": "autonomous", "events_per_minute": 600},
        SubscriptionTier.ENTERPRISE: {"max_agents": 9999, "max_autonomy": "autonomous", "events_per_minute": 999999}
    }

    def __init__(self, tier: str = "pro"):
        self.tier = SubscriptionTier(tier.lower())
        self.current_event_count = 0
        self.last_reset = time.time()
        self.active_agents = set()

    def check_limits(self, active_agent_count: int, autonomy_requested: bool) -> bool:
        limits = self.LIMITS[self.tier]
        
        # Check Agent Count
        if active_agent_count > limits["max_agents"]:
            print(f"[BUSINESS] Blocked: Agent limit reached for {self.tier.name} tier.")
            return False
            
        # Check Autonomy
        if autonomy_requested and limits["max_autonomy"] == "approval_only":
            print(f"[BUSINESS] Blocked: Autonomy not allowed in {self.tier.name} tier.")
            return False
        
        # Check Rate Limit (Events)
        now = time.time()
        if now - self.last_reset > 60:
            self.current_event_count = 0
            self.last_reset = now
            
        if self.current_event_count >= limits["events_per_minute"]:
             print(f"[BUSINESS] Blocked: API Rate limit reached for {self.tier.name} tier.")
             return False
             
        self.current_event_count += 1
        return True

    def upgrade_tier(self, new_tier: str):
        self.tier = SubscriptionTier(new_tier.lower())
        print(f"[BUSINESS] Tier upgraded to {self.tier.name}")
