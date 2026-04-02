import random
import statistics
from typing import List, Dict, Any

class ScenarioSimulator:
    def __init__(self):
        # Forecast Models: Normal distributions driven by 'volatility'
        self.scenarios = {
            "Optimistic": {"mu_shift": 0.20, "sigma_scale": 1.2},
            "Pessimistic": {"mu_shift": -0.20, "sigma_scale": 1.5}, # Higher risk/variance
            "Baseline": {"mu_shift": 0.0, "sigma_scale": 1.0}
        }
    def simulate_action(self, params: Dict[str, Any], event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates probabilistic outcome scenarios for an event.
        Returns a list of scenarios (dict).
        """
        base_value = params.get("expected_value", 1000)
        volatility = params.get("volatility", 0.1)
        
        results = []
        for name, model in self.scenarios.items():
            # Monte Carlo-lite: Sample from distribution
            noise = random.normalvariate(model["mu_shift"], volatility * model["sigma_scale"])
            outcome_value = base_value * (1 + noise)
            
            results.append({
                "name": name,
                "projected_utility": outcome_value,
                "probability": 1.0 / len(self.scenarios), # Equal weight for now
                "risk_factor": volatility * model["sigma_scale"]
            })
            
        return results

    def run_what_if(self, variables: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculates a projected Weisman Score shift based on input variables.
        """
        w_price = 0.4
        w_marketing = 0.3
        w_logistics = -0.5 
        
        price_delta = variables.get("price_adj", 1.0) - 1.0
        mkt_delta = variables.get("marketing_adj", 1.0) - 1.0
        log_delta = variables.get("logistics_adj", 1.0) - 1.0

        impact = (price_delta * w_price) + (mkt_delta * w_marketing) + (log_delta * w_logistics)
        impact += random.uniform(-0.02, 0.02)
        
        return {
            "projected_impact": round(impact, 4),
            "new_score_estimate": round(0.85 + impact, 2),
            "confidence": 0.88,
            "details": f"Price shift of {price_delta*100:.1f}% combined with marketing adjustments."
        }

    def spawn_ghost_realities(self, current_health: float, ticks=10, parallels=3):
        """
        Level 13: Parallel Realities.
        Simulates multiple future timelines.
        """
        print(f"👻 [SIMULATOR] Spawning {parallels} Parallel Ghost Realities...")
        realities = []
        for i in range(parallels):
            score = current_health
            path_log = []
            for t in range(ticks):
                # Random events in ghost state
                event_impact = random.uniform(-0.05, 0.05)
                score = max(0.0, min(1.0, score + event_impact))
                path_log.append(event_impact)
            
            realities.append({
                "id": f"GHOST_{i}",
                "final_health": score,
                "volatility": statistics.stdev(path_log) if len(path_log) > 1 else 0,
                "cumulative_delta": sum(path_log)
            })
        
        # Select the 'Golden Path' (highest health)
        golden_path = max(realities, key=lambda x: x["final_health"])
        print(f"🌟 [SIMULATOR] Golden Path Identified: {golden_path['id']} (Final Health: {golden_path['final_health']:.4f})")
        return golden_path
