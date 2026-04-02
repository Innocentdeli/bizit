from typing import Dict, Any, List
import random
import statistics

class LearningModule:
    """
    Reinforcement Learning Module specifically designed for:
    1. Multi-Objective Utility Evaluation
    2. Counterfactual Simulation
    3. Dynamic Strategy Adjustment
    """
    def __init__(self, optimizer=None):
        self.optimizer = optimizer # Link to Cognitive Kernel
        self.agent_performance = {} # agent_id -> [utility_scores]
        self.historical_outcomes = []
        # Moving average of global system performance
        self.global_performance_trend = []

    def record_outcome(self, agent_id: str, action: Dict[str, Any], realized_metrics: Dict[str, float]):
        """
        Record the actual result of an action against 5 dimensions.
        realized_metrics should contain keys: cashflow, growth, efficiency, fairness, resilience
        """
        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = []
            
        # 1. Calculate Multi-Objective Reward
        # Uses the CURRENT kernel weights to evaluate the realized outcome
        # Reward = w1*r1 + w2*r2 ...
        reward = self.optimizer._compute_weighted_utility(realized_metrics) if self.optimizer else sum(realized_metrics.values())/5
        
        self.agent_performance[agent_id].append(reward)
        self.global_performance_trend.append(reward)
        
        # Keep history bounded
        if len(self.agent_performance[agent_id]) > 100:
            self.agent_performance[agent_id].pop(0)
            
        print(f"[LEARN] Action by {agent_id} yielded Utility {reward:.4f}")
        
        # 2. Continuous Improvement (Meta-Learning)
        # If trend is negative, adjust kernel weights to favor Resilience/Efficiency (Defensive Mode)
        # If trend is positive, adjust kernel weights to favor Growth/Cashflow (Aggressive Mode)
        self._adjust_kernel_weights()

    def run_counterfactuals(self, original_action: Dict[str, Any], realized_outcome: float):
        """
        Simulate "What if we did X instead?"
        Used to update policy if a better action existed.
        """
        # Conceptual implementation
        # 1. Generate alternative actions
        alternatives = ["WAIT", "AGGRESSIVE_BID", "PASSIVE_BID"]
        best_alt_utility = realized_outcome
        
        for alt in alternatives:
            if alt == original_action.get("decision"): continue
            
            # Simulate outcome (Mock)
            sim_utility = realized_outcome * random.uniform(0.8, 1.2)
            
            if sim_utility > best_alt_utility:
                print(f"[LEARN] COUNTERFACTUAL: '{alt}' would have been better ({sim_utility:.2f} vs {realized_outcome:.2f})")
                # Update strategy weights (Implementation specific)

    def _adjust_kernel_weights(self):
        """
        Feedback Loop: Connect learning outputs to cognitive kernel weights.
        """
        if not self.optimizer or len(self.global_performance_trend) < 10:
            return

        recent_avg = statistics.mean(self.global_performance_trend[-10:])
        if recent_avg < 0.4:
            # Crisis detected: Shift validation to Resilience
            print("[LEARN] Performance dropping. Shifting Kernel weights to RESILIENCE.")
            self.optimizer.weights["resilience"] += 0.05
            self.optimizer.weights["growth"] -= 0.05
        elif recent_avg > 0.8:
            # Boom detected: Shift to Growth
            print("[LEARN] Performance strong. Shifting Kernel weights to GROWTH.")
            self.optimizer.weights["growth"] += 0.05
            self.optimizer.weights["resilience"] -= 0.05
            
        # Normalize weights
        total = sum(self.optimizer.weights.values())
        for k in self.optimizer.weights:
            self.optimizer.weights[k] /= total

    def get_agent_policy_weight(self, agent_id: str) -> float:
        """Dynamically adjust probability of selecting this agent based on success."""
        history = self.agent_performance.get(agent_id, [])
        if not history:
            return 1.0 # Default weight
            
        avg_utility = statistics.mean(history)
        return max(0.1, min(2.0, avg_utility * 2)) # Scaled weight

    def specialize_agents(self, agents: Dict[str, Any]):
        """
        Updates agent internal expertise parameters based on domain success.
        """
        for agent_id, agent in agents.items():
            weight = self.get_agent_policy_weight(agent_id)
            if weight > 1.2:
                 print(f"[LEARN] {agent_id} is gaining EXPERTISE level.")
                 # agent.expertise_level += 1
