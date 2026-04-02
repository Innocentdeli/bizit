from agents.base_agent import BaseAgent
from typing import Dict, Any
import json
import time

class PulseAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Pulse-Master-1", domain="Intelligence")
        self.specialization = "Decision Intelligence"
        self.trust_score = 0.99

    async def orchestrate_marathon_task(self, signal: Dict[str, Any]):
        """
        Hackathon: The Marathon Agent.
        Long-running task orchestration with Thinking Levels and Self-Correction.
        """
        from cognitive_kernel.prompt_engine import PromptEngine
        engine = PromptEngine()
        
        # 1. TACTICAL: Immediate Distillation
        brief = self.distillation_logic(signal)
        
        # 2. STRATEGIC: Decision Proposal
        context = {"event_summary": brief["headline"], "impact": brief["impact"]}
        proposal = await engine.generate_decision(self.name, context, "Preserve Sovereign Capital", level="STRATEGIC")
        
        # Robustness check
        proposal_decision = proposal.get("decision", "HOLD_LIQUIDITY")
        proposal_thought = proposal.get("thought_process", "No rationale provided by kernel.")
        
        # 3. SOVEREIGN: Critique and Self-Correction (Thinking Loop)
        critique_prompt = f"Critique this decision: {proposal_decision}. Rationale: {proposal_thought}. Is this resilient against 48h market volatility?"
        corrected = await engine.generate_decision(self.name, {"event_summary": critique_prompt}, "Finalize Resilient Directive", level="SOVEREIGN")
        
        final_decision = corrected.get("decision", proposal_decision)
        print(f"🧬 [MARATHON] Task Self-Corrected: {final_decision}")
        return corrected
        
    def distillation_logic(self, raw_signal):
        # ... existing logic ...
        """
        Converts raw news/data into the 'Pulse Card' schema.
        Input: Raw signal dictionary from Sensory Layer.
        Output: Distilled Micro-Brief.
        """
        payload = raw_signal.get("payload", {})
        event_type = raw_signal.get("event_type", "DATA_STREAM")
        
        # Determine Urgency based on signal confluence
        urgency = "WATCH"
        headline = f"POLARIS SIGNAL: {payload.get('title', 'Market Shift')}"
        signal_text = f"BIZIT Sensors detected a {payload.get('change', 'delta')} in {payload.get('variable', 'market context')}."
        impact_text = "This shift may require immediate capital reallocation or pricing adjustments."

        if event_type == "ECON_TICK":
            variable = payload.get("variable", "UNKNOWN")
            change = payload.get("change", 0)
            headline = f"MACRO ALERT: {variable} VOLATILITY"
            signal_text = f"Significant fluctuation detected in {variable} ({payload.get('value', 0)}). Delta: {change:+.2f}."
            if abs(change) > 10.0: # High volatility threshold for NGN
                urgency = "ACT"
                impact_text = "High volatility triggers mandatory liquidity audit. PnL exposure is high."
            else:
                urgency = "WATCH"
                impact_text = "Monitor for trend continuation before adjusting hedges."

        elif event_type == "SOVEREIGN_NEWS":
            sentiment = payload.get("sentiment", "NEUTRAL")
            headline = f"POLICY SHIFT: {payload.get('title', 'Govt Update')}"
            signal_text = f"Sovereign source reports {sentiment.lower()} development in Nigerian business environment."
            if sentiment == "Hawkish" or sentiment == "Volatile":
                urgency = "ACT"
                impact_text = "Policy shift indicates immediate interest rate or tax risk. Action required."
            else:
                urgency = "WATCH"
                impact_text = "Policy clarity improves; monitor for sector-specific implementation."

        # Distillation using PulseSchema
        from core.pulse_schema import PulseSchema
        brief = PulseSchema.create_pulse_card(
            headline=headline,
            urgency=urgency,
            signal=signal_text,
            impact=impact_text,
            trust_hash=payload.get("source_hash", f"ipfs://{raw_signal.get('source', 'SENSORY_LAYER_HASH')}")
        )
        return brief

    def propose_action(self, event_dict):
        """
        Level 59 Logic: Triggers the Decision Engine workflow 
        when an 'ACT' brief is generated.
        """
        brief = self.distillation_logic(event_dict)
        
        if brief["urgency"] == "ACT":
            return {
                "decision": "TRIGGER_DECISION_ENGINE",
                "reason": f"Urgent signal detected: {brief['headline']}",
                "metadata": {
                    "brief": brief,
                    "recommended_paths": ["AGGRESSIVE_HEDGE", "CAPITAL_PRESERVATION", "LIQUIDITY_PUMP"]
                }
            }
            
        return {
            "decision": "BROADCAST_BRIEF",
            "reason": "Routine high-signal intelligence update.",
            "metadata": {"brief": brief}
        }

    def receive_task(self, event_dict, **kwargs):
        """Standard BIZIT Agent Task Ingestion."""
        return self.propose_action(event_dict)
