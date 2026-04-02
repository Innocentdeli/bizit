import sys
import os
sys.path.append(os.getcwd())

from core.state import OrganismState
from business_layer.objective_manager import ObjectiveManager, StrategicGoal
from cognitive_kernel.optimizer import Optimizer

def test_objective_mutation():
    print("🧪 Testing ObjectiveManager Mutation...")
    obj_manager = ObjectiveManager()
    state = OrganismState()
    
    # Test Survival Mode trigger
    state.agent_trust_history = {"test": [0.1]} # Lowers weisman
    # state.get_weisman_score() should be low
    obj_manager.evaluate_organism_needs(state)
    print(f"Goal after health failure: {obj_manager.get_active_goal()}")
    
    # Test Liquidity trigger
    state.agent_trust_history = {"test": [0.9]} # Reset health
    state.sov_balance = 50.0
    obj_manager.evaluate_organism_needs(state)
    print(f"Goal after liquidity failure: {obj_manager.get_active_goal()}")
    
    # Test Homeostasis
    state.sov_balance = 1000.0
    obj_manager.evaluate_organism_needs(state)
    print(f"Goal after recovery: {obj_manager.get_active_goal()}")

def test_optimizer_penalties():
    print("\n🧪 Testing Optimizer Penalties...")
    optimizer = Optimizer()
    state = OrganismState()
    
    task = {"id": "t1", "specialization": "operations"}
    scores = optimizer._score_assignment(task, "operations")
    
    # Baseline utility
    u_base = optimizer._compute_weighted_utility(scores, state)
    print(f"Baseline Utility: {u_base:.4f}")
    
    # Metabolic Penalty
    state.update_metabolic_stats({"cpu": 95, "ram": 20})
    u_stressed = optimizer._compute_weighted_utility(scores, state)
    print(f"Metabolic Stressed Utility (CPU 95%): {u_stressed:.4f}")
    
    # Scarcity Penalty
    state.sov_balance = 100.0
    u_broke = optimizer._compute_weighted_utility(scores, state)
    print(f"Scarcity Utility (SOV 100): {u_broke:.4f}")

if __name__ == "__main__":
    try:
        test_objective_mutation()
        test_optimizer_penalties()
        print("\n✅ Verification Complete.")
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback
        traceback.print_exc()
