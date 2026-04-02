from typing import Dict
from enum import Enum

class StrategicGoal(Enum):
    MAXIMIZE_CASHFLOW = "maximize_cashflow"
    GROW_REVENUE = "grow_revenue"
    CUT_COSTS = "cut_costs"
    BALANCED_GROWTH = "balanced_growth"
    SURVIVAL_MODE = "survival_mode"
    REDUCE_INVENTORY_COST = "reduce_inventory_cost"
    CUT_LOGISTICS_COST = "cut_logistics_cost"
    OPTIMIZE_PROFIT = "optimize_profit"
    SCALE_MARKET = "scale_market"

class ObjectiveManager:
    """
    Implements LAYER 3: FULL AUTONOMY.
    Translates user-defined high-level goals into mathematical utility weights for the Cognitive Kernel.
    """
    
    # Maps strategic goals to (Cashflow, Growth, Efficiency, Fairness, Resilience) weights
    STRATEGY_MAP = {
        StrategicGoal.MAXIMIZE_CASHFLOW: {"cashflow": 0.9, "growth": 0.1, "efficiency": 0.5, "fairness": 0.1, "resilience": 0.4},
        StrategicGoal.GROW_REVENUE:      {"cashflow": 0.3, "growth": 0.9, "efficiency": 0.3, "fairness": 0.2, "resilience": 0.4},
        StrategicGoal.CUT_COSTS:         {"cashflow": 0.5, "growth": 0.1, "efficiency": 0.9, "fairness": 0.1, "resilience": 0.2},
        StrategicGoal.BALANCED_GROWTH:   {"cashflow": 0.5, "growth": 0.5, "efficiency": 0.5, "fairness": 0.5, "resilience": 0.5},
        StrategicGoal.SURVIVAL_MODE:     {"cashflow": 1.0, "growth": 0.0, "efficiency": 0.8, "fairness": 0.0, "resilience": 1.0},
        StrategicGoal.REDUCE_INVENTORY_COST: {"cashflow": 0.6, "growth": 0.2, "efficiency": 0.9, "fairness": 0.3, "resilience": 0.5},
        StrategicGoal.CUT_LOGISTICS_COST:    {"cashflow": 0.7, "growth": 0.2, "efficiency": 0.9, "fairness": 0.2, "resilience": 0.3},
        StrategicGoal.OPTIMIZE_PROFIT:       {"cashflow": 0.6, "growth": 0.6, "efficiency": 0.8, "fairness": 0.4, "resilience": 0.5},
        StrategicGoal.SCALE_MARKET:          {"cashflow": 0.2, "growth": 1.0, "efficiency": 0.4, "fairness": 0.2, "resilience": 0.6},
    }

    def __init__(self):
        self.current_goal = StrategicGoal.BALANCED_GROWTH
        self.custom_weights = None

    def set_goal(self, goal: str):
        try:
            self.current_goal = StrategicGoal(goal.lower())
            self.custom_weights = None
            print(f"[OBJECTIVE] Strategic Goal set to: {self.current_goal.name}")
            return True
        except ValueError:
            print(f"[OBJECTIVE] Invalid goal: {goal}")
            return False

    def set_custom_weights(self, weights: Dict[str, float]):
        """For advanced users who want to manually tune the organism."""
        self.custom_weights = weights
        print(f"[OBJECTIVE] Custom weights applied: {weights}")

    def get_current_weights(self) -> Dict[str, float]:
        if self.custom_weights:
            return self.custom_weights
        return self.STRATEGY_MAP[self.current_goal]

    def get_active_goal(self):
        return self.current_goal.name

    def mutate_weights_based_on_forecast(self, predicted_health: float):
        """
        Level 10: Goal Mutation (Teleological Evolution).
        The organism changes its own priorities based on future predictions.
        """
        current_weights = self.get_current_weights().copy()
        
        if predicted_health < 0.4:
            print(f"⚠️ [OBJECTIVE] Oracle predicts doom ({predicted_health:.2f}). MUTATING: Survival Mode.")
            # Drastically boost Resilience and Cashflow
            current_weights["resilience"] = 0.9
            current_weights["cashflow"] = 0.8
            current_weights["growth"] = 0.0
            self.set_custom_weights(current_weights)
            
        elif predicted_health > 0.8:
             print(f"🚀 [OBJECTIVE] Oracle predicts boom ({predicted_health:.2f}). MUTATING: Hyper-Growth.")
             # Boost Growth
             current_weights["growth"] = 1.0
             current_weights["resilience"] = 0.3
             self.set_custom_weights(current_weights)
             
        else:
            # Revert to standard if predictions are nominal
            if self.custom_weights:
                print(f"⚖️ [OBJECTIVE] Forecast nominal. Reverting to standard dogma.")
                self.custom_weights = None
    def evaluate_organism_needs(self, state):
        """
        Level 33: Autonomous Self-Priority Evaluation.
        Analyzes real-time state to decide if current goals should be overridden.
        """
        weisman = state.get_weisman_score()
        sov_balance = getattr(state, "sov_balance", 1000.0)
        
        # 1. Survival Check (Health < 0.3)
        if weisman < 0.3:
            if self.current_goal != StrategicGoal.SURVIVAL_MODE:
                print(f"⚠️ [OBJECTIVE] Critical Health Failure ({weisman:.2f}). Emergency Survival Mode.")
                self.set_goal("survival_mode")
            return
            
        # 2. Liquidity Check (SOV balance low)
        if sov_balance < 200:
            if self.current_goal != StrategicGoal.MAXIMIZE_CASHFLOW:
                print(f"💸 [OBJECTIVE] Liquidity Strain ({sov_balance:.2f} SOV). Prioritizing Cashflow.")
                self.set_goal("maximize_cashflow")
            return
            
        # 3. Growth Check (Health > 0.9 and Cash > 2000)
        if weisman > 0.9 and sov_balance > 2000:
            if self.current_goal != StrategicGoal.GROW_REVENUE:
                print(f"🚀 [OBJECTIVE] Organism is thriving. Transitioning to Growth.")
                self.set_goal("grow_revenue")
            return

        # 4. Revert to Homeostasis (Normal parameters)
        if 0.5 < weisman < 0.8 and 500 < sov_balance < 1500:
            if self.current_goal != StrategicGoal.BALANCED_GROWTH:
                 print(f"⚖️ [OBJECTIVE] Parameters normalized. Returning to Balanced Growth.")
                 self.set_goal("balanced_growth")
