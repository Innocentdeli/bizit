import random

class SuperpositionEngine:
    """
    Level 16: Quantum Decision Superposition.
    Allows agents to maintain multiple contradictory intent states until 'observed'.
    """
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.probability_clouds = {} # {agent_name: [list of actions]}

    def project_wavefunction(self, agent_name, available_actions):
        """
        Projects a cloud of potential actions into superposition.
        """
        self.probability_clouds[agent_name] = available_actions
        print(f"⚛️ [SUPERPOSITION] Agent {agent_name} in state of potential for: {[a.get('type', 'UNKNOWN') for a in available_actions]}")

    def collapse_wavefunction(self, agent_name, market_reality):
        """
        Collapses the cloud based on 'Observation' (Market Reality).
        Returns the single optimal action that survived decoherence.
        """
        cloud = self.probability_clouds.get(agent_name, [])
        if not cloud: 
            return None
        
        # Market Reality Observation
        # If market delta is positive, we collapse towards growth/risk
        # If negative, we collapse towards resilience
        market_delta = market_reality.get("delta", 0)
        
        if market_delta > 0:
            # Sort by a hypothetical 'growth_potential' (or just random for now)
            observed = sorted(cloud, key=lambda x: random.uniform(0.5, 1.0) if "GROWTH" in x.get("type", "") else random.uniform(0, 0.5), reverse=True)[0]
        else:
            observed = sorted(cloud, key=lambda x: random.uniform(0.5, 1.0) if "RESILIENCE" in x.get("type", "") or "WAIT" in x.get("type", "") else random.uniform(0, 0.5), reverse=True)[0]
            
        print(f"💫 [COLLAPSE] Wavefunction collapsed for {agent_name} -> {observed.get('type')}")
        del self.probability_clouds[agent_name]
        return observed
