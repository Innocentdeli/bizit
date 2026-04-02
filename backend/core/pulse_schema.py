import json
import time

class PulseSchema:
    """
    Standard Data Schemas for BIZIT Pulse Intelligence.
    Ensures consistency between Backend (PulseAgent) and Frontend (Next.js).
    """
    
    @staticmethod
    def create_pulse_card(headline, urgency, signal, impact, trust_hash):
        return {
            "headline": headline[:60],
            "urgency": urgency.upper(), # IGNORE, WATCH, ACT
            "signal": signal,
            "impact": impact,
            "cta": "DECISION_MATRIX" if urgency.upper() == "ACT" else "ACKNOWLEDGE",
            "trust_hash": trust_hash,
            "timestamp": time.time()
        }

    @staticmethod
    def create_decision_matrix(goal, constraints, options):
        return {
            "goal": goal,
            "constraints": constraints,
            "options": options, # List of {label, risk, reward, logic}
            "timestamp": time.time()
        }
