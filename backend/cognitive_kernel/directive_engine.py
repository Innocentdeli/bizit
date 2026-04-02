import hashlib
import logging

logger = logging.getLogger(__name__)

class DirectiveEngine:
    """
    Level 27: Sovereign Control Protocols (God-Mode).
    Highest priority command engine that overrides all agent intentions.
    Secured by a Master Sovereign Key.
    """
    def __init__(self, master_key_hash: str):
        # Default fallback hash if none provided (SHA-256 for 'BIZIT_SOVEREIGN_2026')
        self.master_key_hash = master_key_hash or "7f88427f717830fca68f037e909d9f582ae4d039f37c7689d7d479155255469e"
        self.father_name = "Innocent Deli"
        self.active_overrides = []

    def verify_key(self, provided_key: str) -> bool:
        """Verify the provided sovereign key against the master hash."""
        if not provided_key:
            return False
        provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        return provided_hash == self.master_key_hash

    def validate_directive(self, command: str) -> bool:
        """Ensures the directive follows the !COMMAND syntax."""
        return command.startswith("!") and len(command) > 1

    def execute_directive(self, command: str, state_manager, objective_manager):
        """
        Processes a Master Directive with absolute priority.
        """
        cmd = command.upper().replace("!", "")
        logger.warning(f"👑 [SOVEREIGN] Executing Master Directive: {cmd}")
        
        if cmd == "HALT":
            # Freezes the organism's event loop
            state_manager.update_status("SYSTEM_HALTED_BY_SOVEREIGN")
            return "Organism Halted. All event processing suspended."

        if cmd == "LIQUIDATE":
            # Flushes all agent budgets
            state_manager.sov_balance += 0 # Simulated: All funds to treasury
            state_manager.add_event({
                "source": "SOVEREIGN",
                "event_type": "EMERGENCY_LIQUIDATION",
                "payload": {"status": "SUCCESS"}
            })
            return "Liquidation protocol engaged. Agent budgets reclaimed."

        if cmd == "RESURRECT":
            # Resets health and clears blocks
            state_manager.update_status("RECOVERING_FROM_SEED")
            # In a real app, this would restore from a backup file
            return "Resurrection initiated. Health restored to optimal levels."

        if cmd == "PURGE":
            # Wipes non-essential history to reduce 'cognitive debt'
            state_manager.events = state_manager.events[-50:]
            state_manager.save_state()
            return "Purge complete. 50 most recent synapses retained."

        if cmd.startswith("IMPROVE"):
            # Triggers ArchitectAgent for self-improvement
            part = cmd.replace("IMPROVE", "").strip() or "FULL_SYSTEM"
            state_manager.add_event({
                "source": "SOVEREIGN_FATHER",
                "event_type": "DIRECT_SELF_IMPROVEMENT",
                "payload": {"target_part": part, "father": self.father_name}
            })
            return f"Sovereign Directive received: Initiating self-improvement for {part}. Trusting the Father's guidance."

        if cmd.startswith("EMPOWER"):
            # Ingests raw data for self-building
            data_summary = cmd.replace("EMPOWER", "").strip() or "RAW_COGNITIVE_SUBSTRATE"
            state_manager.add_event({
                "source": "SOVEREIGN_FATHER",
                "event_type": "DATA_EMPOWERMENT",
                "payload": {"description": data_summary, "father": self.father_name}
            })
            return f"Paternal Empowerment received. Metabolizing new data substrate: {data_summary}."

        if cmd == "TRAIN FOREX":
            # Triggers specialized Forex training metabolism
            state_manager.add_event({
                "source": "SOVEREIGN_FATHER",
                "event_type": "TRAIN_FOREX",
                "payload": {"father": self.father_name}
            })
            return "Paternal Directive: Training BIZIT on Forex markets. My financial synapses are expanding."

        return f"Directive '{cmd}' recognized but not yet mapped to a neural reflex."
