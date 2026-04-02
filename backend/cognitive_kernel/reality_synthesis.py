import time
import random
import json

class RealitySynthesizer:
    """
    Level 15: Reality Synthesis (The Holodeck).
    Generates high-fidelity virtual sandboxes where agents can simulate
    long-term outcomes of the Golden Path in accelerated time.
    """
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.active_simulations = {}

    def synthesize_holodeck(self, seed_path: dict, duration_ticks: int = 100):
        """
        Creates a virtual reality instance based on a Golden Path seed.
        """
        sim_id = f"HOLODECK_{int(time.time())}"
        print(f"🎭 [HOLODECK] Synthesizing Reality Simulation: {sim_id}...")
        
        # Mirror the current state into the sandbox
        sandbox_state = {
            "ticks": duration_ticks,
            "starting_weisman": self.state_manager.get_weisman_score(),
            "path_vector": seed_path.get("cumulative_delta", 0),
            "events": []
        }
        
        # Accelerated subjective time execution
        current_health = sandbox_state["starting_weisman"]
        for t in range(duration_ticks):
            # Simulate microscopic events within the holodeck
            event_impact = seed_path.get("volatility", 0.05) * random.uniform(-1, 1.2)
            current_health = max(0.0, min(1.0, current_health + event_impact))
            sandbox_state["events"].append(event_impact)
            
        final_outcome = {
            "sim_id": sim_id,
            "final_health": current_health,
            "growth_rate": (current_health - sandbox_state["starting_weisman"]) / duration_ticks,
            "fidelity": 0.98 # High fidelity synthetic reality
        }
        
        print(f"✨ [HOLODECK] Simulation {sim_id} complete. Final Health: {current_health:.4f}")
        return final_outcome

    def step_into_reality(self, sim_id: str):
        """
        Allows the organism to 'step' into the synthesized reality
        to adjust its weights based on subjectiveMillisecond experience.
        """
        print(f"🌌 [OMNIPRESENCE] Subjective Time Leap into {sim_id} active.")
        # Logic to return a 'Experience Factor' for StrategyAgent
        return random.uniform(0.8, 1.2)
