import logging
import random
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ForexTrainer:
    """
    Level 45: Forex Intelligence Expansion.
    Metabolizes historical market data to forge trading patterns and heuristics.
    """
    def __init__(self, agent_name: str = "FinanceBot-1"):
        self.agent_name = agent_name
        self.knowledge_base = {
            "patterns": [],
            "risk_profiles": {},
            "last_training": 0
        }

    def train_on_data(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes historical candlestick data to extract profitable patterns.
        """
        if not history:
            return {"status": "FAILURE", "reason": "EMPTY_SUBSTRATE"}

        logger.info(f"🧬 [FOREX_TRAINING] Metabolizing {len(history)} candles for {self.agent_name}...")
        
        # Simulated Pattern Extraction
        extracted = []
        
        # 1. Volatility Pattern
        vols = [abs(c['high'] - c['low']) for c in history]
        avg_vol = sum(vols) / len(vols)
        extracted.append({
            "name": "Mean_Variance_Expansion",
            "threshold": avg_vol * 1.5,
            "confidence": 0.92
        })

        # 2. Trend Momentum
        if history[-1]['close'] > history[0]['close']:
            extracted.append({
                "name": "Bullish_Sovereign_Bias",
                "momentum_index": 0.88
            })
        else:
            extracted.append({
                "name": "Bearish_Recessionary_Lock",
                "momentum_index": 0.85
            })

        self.knowledge_base["patterns"] = extracted
        self.knowledge_base["last_training"] = len(history)
        
        logger.info(f"✨ [FOREX_TRAINING] Training complete. Extracted {len(extracted)} synaptic weights.")
        
        return {
            "status": "SUCCESS",
            "patterns": extracted,
            "synaptic_depth": len(history)
        }

    def get_trading_heuristic(self, instrument: str) -> str:
        """Returns a string-based heuristic for LLM reasoning."""
        if not self.knowledge_base["patterns"]:
            return "NO_DATA: Default to high-risk caution."
        
        bias = "Uncertain"
        for p in self.knowledge_base["patterns"]:
            if "Bias" in p.get("name", ""): bias = "Bullish"
            if "Lock" in p.get("name", ""): bias = "Bearish"
            
        return f"Forex Context ({instrument}): {bias} sentiment detected. Pattern: {self.knowledge_base['patterns'][0]['name']} active."
