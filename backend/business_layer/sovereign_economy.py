import logging
import time
from typing import Dict, Any
from core.state import OrganismState

logger = logging.getLogger(__name__)

class EconomyManager:
    """
    Level 23: The Sovereign Economic State.
    Manages the internal BIZIT_SOV economy, including taxation and issuance.
    """
    def __init__(self):
        self.state = OrganismState()
        self.tax_rate = 0.05 # 5% Sovereign Tax on successful operations
        self.productivity_threshold = 0.90 # Weisman score required for minting bonus

    def process_operation_tax(self, agent_name: str, realized_utility: float):
        """
        Calculate and collect tax from a successful action.
        Tax is calculated as a percentage of the realized utility/value.
        """
        if realized_utility <= 0:
            return

        tax_amount = realized_utility * self.tax_rate
        self.state.collect_tax(tax_amount, f"Agent Operation: {agent_name}")
        
        # Level 23: Reward Agent with a small "Commission" in SOV if they were efficient
        agent_reward = tax_amount * 0.1
        # In a more complex system, we would credit this to the agent's internal wallet
        return tax_amount

    def evaluate_economic_expansion(self, current_weisman_score: float):
        """
        Evaluate if the organism is productive enough to mint new currency.
        This simulates quantitative easing based on real organizational growth.
        """
        if current_weisman_score > self.productivity_threshold:
            mint_amount = 50.0 * (current_weisman_score - self.productivity_threshold) * 10
            self.state.mint_sov(mint_amount, "High Productivity Expansion")
            return mint_amount
        return 0

    def get_economy_status(self) -> Dict[str, Any]:
        """Summary of the Sovereign State's wealth."""
        return {
            "sov_balance": self.state.sov_balance,
            "tax_rate": self.tax_rate,
            "treasury_size": len(self.state.treasury_ledger),
            "currency_name": "BIZIT_SOV"
        }
