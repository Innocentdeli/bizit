import copy
import time
import random
import logging
from typing import Dict, List, Any, Optional
from core.state import OrganismState

logger = logging.getLogger(__name__)

class DigitalTwin:
    """
    Level 24: DigitalTwin Synthesis.
    A predictive mirror of the BIZIT organism.
    Allows for shadow simulations without affecting the primary state.
    """
    def __init__(self, primary_state: OrganismState):
        self.primary = primary_state
        self.twin_state: Dict[str, Any] = {}
        self.sync_with_primary()
        logger.info("DigitalTwin synthesized from primary state.")

    def sync_with_primary(self):
        """Clone the current primary state into the twin."""
        self.twin_state = copy.deepcopy(self.primary.get_snapshot())

    def project_future_state(self, ticks: int = 10) -> List[Dict[str, Any]]:
        """
        Simulate future state trajectories based on current momentum.
        Returns a timeline of projected vital signs.
        """
        projection = []
        temp_state = copy.deepcopy(self.twin_state)
        
        for i in range(ticks):
            # 1. Simulate DeFi volatility
            for pair in temp_state["defi_quotes"]:
                drift = random.uniform(-0.005, 0.005)
                temp_state["defi_quotes"][pair] *= (1 + drift)

            # 2. Simulate Passive Income/Burn
            temp_state["sov_balance"] *= 1.001 # 0.1% growth per tick (dummy growth)
            
            # 3. Simulate specific events (e.g. tax collection probability)
            if random.random() > 0.8:
                temp_state["sov_balance"] += 10.0
            
            projection.append({
                "tick": i,
                "sov_balance": temp_state["sov_balance"],
                "defi_quotes": copy.deepcopy(temp_state["defi_quotes"]),
                "timestamp": temp_state["timestamp"] + (i * 60) # 1 minute per tick
            })
            
        return projection

    def run_shadow_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run an action on the twin state to see its impact.
        """
        print(f"👻 [TWIN] Running Shadow Action: {action.get('decision')}")
        # Logic to simulate the action on temp_state...
        # For now, just return a success/impact report
        return {
            "status": "SUCCESS",
            "impact": {
                "sov_delta": random.uniform(-5, 15),
                "risk_increase": 0.02
            }
        }
