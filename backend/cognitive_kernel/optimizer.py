try:
    from ortools.sat.python import cp_model
    _ORTOOLS_AVAILABLE = True
except ImportError:
    _ORTOOLS_AVAILABLE = False

import logging
from typing import List, Dict, Any

class Optimizer:
    def __init__(self):
        # Weights for the multi-objective function
        self.weights = {
            "cashflow": 0.3,
            "growth": 0.2,
            "efficiency": 0.2,
            "fairness": 0.1,  # e.g., equitable workload distribution
            "resilience": 0.2 # low risk/variance
        }
        
        if _ORTOOLS_AVAILABLE:
            self.model = cp_model.CpModel()
            self.solver = cp_model.CpSolver()
        else:
            logging.warning("OR-Tools not available. Using heuristic-based optimization.")

    def optimize_resource_allocation(self, resources: dict, tasks: list, utility_weights: dict = None, state: Any = None):
        """
        Assign tasks to agents (resources) maximizing the weighted utility sum.
        """
        if utility_weights:
             self.weights = utility_weights
             
        print(f"[KERNEL] Optimizing allocation for {len(tasks)} tasks...")
        
        recommendations = []
        for task in tasks:
            # 1. Identify Candidate Agents
            # In a real system, we'd query available agents from 'resources'
            # Here we assume a standard set or use the task's pref.
            candidates = ["finance", "sales", "operations", "negotiation"]
            
            best_agent = None
            max_utility = -float('inf')
            
            # 2. Score each candidate
            for agent_type in candidates:
                # Calculate scores for each objective based on task + agent match
                scores = self._score_assignment(task, agent_type)
                
                # 3. Compute weighted utility
                utility = self._compute_weighted_utility(scores, state)
                
                if utility > max_utility:
                    max_utility = utility
                    best_agent = agent_type
            
            recommendations.append({
                "task_id": task.get("id"),
                "action": "EXECUTE",
                "assigned_agent": best_agent,
                "utility": round(max_utility, 4),
                "priority_score": task.get("priority", 1)
            })
            
        return recommendations

    def _score_assignment(self, task: Dict, agent: str) -> Dict[str, float]:
        """
        Heuristic scoring function for the 5 objectives.
        Returns normalized scores (0.0 - 1.0).
        """
        specialization = task.get("specialization", "general")
        is_expert = (agent == specialization)
        
        # Base efficiency
        efficiency = 0.95 if is_expert else 0.4
        
        # Cashflow impact (Sales/Finance are high impacters)
        cashflow = 0.8 if agent in ["finance", "sales"] else 0.5
        
        # Growth (Sales/Negotiation drive growth)
        growth = 0.9 if agent in ["sales", "negotiation"] else 0.3
        
        # Resilience (Ops/Finance are stable)
        resilience = 0.9 if agent in ["operations", "finance"] else 0.6
        
        # Fairness (Randomize slightly to simulate load balancing)
        import random
        fairness = random.uniform(0.7, 1.0) 
        
        return {
            "cashflow": cashflow,
            "growth": growth,
            "efficiency": efficiency,
            "fairness": fairness,
            "resilience": resilience
        }

    def _compute_weighted_utility(self, scores: Dict[str, float], state: Any = None) -> float:
        """
        Calculate dot product of weights and scores.
        Level 33: Apply global penalties for metabolic stress and resource scarcity.
        """
        utility = 0.0
        for dimension, weight in self.weights.items():
            utility += scores.get(dimension, 0) * weight
            
        if state:
            # 1. Metabolic Penalty (CPU/RAM stress)
            # High compute tasks are penalized when system is under load
            # metabolic_data = getattr(state, "metabolic", {}) # state is a dict or OrganismState
            # If state is OrganismState:
            try:
                # Mock metabolic pull from state if it doesn't exist yet as a property
                metabolic = getattr(state, "metabolic_stats", {"cpu": 10}) 
                cpu_usage = metabolic.get("cpu", 10)
                if cpu_usage > 70:
                     penalty = (cpu_usage - 70) / 100.0 # 0.0 to 0.3
                     utility -= penalty
                 
                # 2. Resource Scarcity Penalty (Budget)
                # High cost tasks penalized if SOV balance is low
                sov_balance = getattr(state, "sov_balance", 1000)
                if sov_balance < 200:
                    utility -= 0.15
            except:
                pass
                
        return max(0.01, utility)

    def evaluate_utility(self, state: dict, action: dict) -> float:
        """Public method to evaluate a standalone action outside of assignment."""
        # Map generic action keys to our 5 dimensions if present
        scores = {
            "cashflow": action.get("impact_cashflow", 0.5),
            "growth": action.get("impact_growth", 0.5),
            "efficiency": action.get("impact_efficiency", 0.5),
            "fairness": action.get("impact_fairness", 0.5),
            "resilience": action.get("impact_resilience", 0.5)
        }
        return self._compute_weighted_utility(scores)


