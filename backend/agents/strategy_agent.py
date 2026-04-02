from typing import Dict, Any
from agents.base_agent import BaseAgent

class StrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__("StrategyBot-1", "strategy")

    def reflect_on_history(self, diary_path: str):
        """
        Level 13: Self-Reflective Evolution.
        Analyzes the narrative diary for strategic depth.
        """
        try:
            import os
            if not os.path.exists(diary_path): return None
            
            with open(diary_path, "r") as f:
                content = f.read()
            
            # Simple 'repetitive narrative' check
            words = content.split()
            unique_ratio = len(set(words)) / len(words) if words else 1.0
            
            print(f"🧐 [STRATEGY] Self-Reflection: Narrative Unique Ratio = {unique_ratio:.2f}")
            
            # If ratio < 0.5, narrative is stale. Trigger radical mutation.
            if unique_ratio < 0.5:
                print("⚠️ [STRATEGY] Strategic Stagnation Detected. Forcing radical weight mutation.")
                return {"stagnation": True, "ratio": unique_ratio}
                
        except Exception as e:
            print(f"🧐 [STRATEGY] Reflection failed: {e}")
        return None

    def reason(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Long-term planning, market positioning, and resource allocation meta-decisions.
        """
        event_type = state.get("event_type", "")
        
        decision = "MONITOR_TREND"
        confidence = 0.6
        
        if "MARKET" in event_type or "COMPETITOR" in event_type:
            decision = "ADJUST_MARKET_POSITION"
            confidence = 0.88
            
        elif "CASHFLOW" in event_type:
            decision = "REALLOCATE_CAPITAL"
            confidence = 0.9
            
        return {
            "agent": self.name,
            "decision": decision,
            "confidence": confidence,
            "metadata": {"horizon": "LONG_TERM"}
        }
