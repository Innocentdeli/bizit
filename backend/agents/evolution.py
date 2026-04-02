import random
import time
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from agents.finance_agent import FinanceAgent # Default class for clones

class AgentEvolutionModule:
    """
    Level 7: The Hive Mind (Genetics).
    Manages the lifecycle of the agent swarm: Birth, Death, and Evolution.
    """
    def __init__(self):
        self.generation = 0
        self.evolution_log = []

    def evolve_agents(self, agents: Dict[str, BaseAgent], performance_data: Dict[str, float]) -> List[str]:
        """
        Runs the Darwinian cycle. 
        Returns a list of significant events (strings).
        """
        self.generation += 1
        events = []
        
        # 1. Sort by Performance (Trust Score)
        sorted_agents = sorted(
            agents.items(), 
            key=lambda item: item[1].trust_score, 
            reverse=True
        )
        
        count = len(sorted_agents)
        if count < 3: return [] # Too small to evolve
        
        top_performer = sorted_agents[0][1]
        worst_performer = sorted_agents[-1][1]
        
        # 2. Culling (Death & Rebirth)
        if worst_performer.trust_score < 0.3:
            victim_name = sorted_agents[-1][0]
            print(f"[GENETICS] Culling Agent: {victim_name} (Trust: {worst_performer.trust_score:.2f})")
            
            # Reset to baseline instead of deleting to avoid dict mutation issues during iteration
            agents[victim_name].trust_score = 0.8
            if hasattr(agents[victim_name], 'history'): agents[victim_name].history = []
            events.append(f"Culled and rebooted weak agent: {victim_name}")
            
        # 3. Promotion / Resource Adjustment
        for name, agent in agents.items():
            score = performance_data.get(name, agent.trust_score)
            if score > 0.9:
                if hasattr(agent, 'resources'):
                    agent.resources["compute"] = agent.resources.get("compute", 100) + 10
                events.append(f"Agent {name} promoted due to excellence.")

        # 4. Reproduction (Cloning with mutation)
        if top_performer.trust_score > 0.98 and count < 12:
            child_name = f"Clone_{self.generation}_{random.randint(100,999)}"
            
            # Simple cloning mechanism
            child = FinanceAgent(name=child_name)
            child.trust_score = 0.7 
            
            agents[child_name] = child
            print(f"[GENETICS] New Agent Born: {child_name}")
            events.append(f"Spawned new agent: {child_name}")
            
        return events
