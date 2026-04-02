from cognitive_kernel.tool_registry import AgentTool
from typing import Dict, Any
import logging
import random
import time

logger = logging.getLogger(__name__)

class DeFiTool(AgentTool):
    """
    Enables agents to interact with Decentralized Finance protocols (Mock/Simulated).
    Level 36c: The Wallet of the Organism.
    """
    def __init__(self):
        super().__init__("defi_wallet", "Interact with DeFi: Check balances and execute swaps.")
        # Mock State
        self._wallet_address = "0x" + "".join([random.choice("0123456789abcdef") for _ in range(40)])
        self._balances = {
            "ETH": 15.5,
            "USDC": 50000.0,
            "BTC": 1.2
        }

    def execute(self, action: str = "", **kwargs) -> Dict[str, Any]:
        logger.info(f"💸 [DEFI] Executing action: '{action}'")
        
        if action == "get_balance":
            asset = kwargs.get("asset", "USDC").upper()
            balance = self._balances.get(asset, 0.0)
            return {
                "status": "success",
                "action": "get_balance",
                "asset": asset,
                "balance": balance,
                "wallet": self._wallet_address
            }
            
        elif action == "swap":
            from_asset = kwargs.get("from_asset", "").upper()
            to_asset = kwargs.get("to_asset", "").upper()
            amount = float(kwargs.get("amount", 0.0))
            
            if not from_asset or not to_asset or amount <= 0:
                 return {"status": "error", "message": "Invalid swap parameters."}
            
            current_bal = self._balances.get(from_asset, 0.0)
            if current_bal < amount:
                 return {"status": "error", "message": f"Insufficient {from_asset} balance."}
                 
            # Execute Simulated Swap
            # Mock Rate
            rate_map = {
                "ETH_USDC": 3200.0,
                "USDC_ETH": 1/3200.0,
                "BTC_USDC": 95000.0,
                "USDC_BTC": 1/95000.0
            }
            pair = f"{from_asset}_{to_asset}"
            rate = rate_map.get(pair, 1.0)
            
            received = amount * rate
            fee = received * 0.003 # 0.3% LP fee
            final_received = received - fee
            
            # Update balances
            self._balances[from_asset] -= amount
            self._balances[to_asset] = self._balances.get(to_asset, 0.0) + final_received
            
            return {
                "status": "success",
                "action": "swap",
                "tx_hash": "0x" + "".join([random.choice("0123456789abcdef") for _ in range(64)]),
                "swapped": f"{amount} {from_asset}",
                "received": f"{final_received:.4f} {to_asset}",
                "fee": f"{fee:.4f} {to_asset}",
                "new_balances": self._balances
            }
            
        return {"status": "error", "message": f"Unknown action: {action}"}

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "name": "defi_wallet",
            "description": "Interact with DeFi ecosystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["get_balance", "swap"]},
                    "asset": {"type": "string", "description": "Asset symbol for checks."},
                    "from_asset": {"type": "string", "description": "Swap input asset."},
                    "to_asset": {"type": "string", "description": "Swap output asset."},
                    "amount": {"type": "number", "description": "Amount to swap."}
                },
                "required": ["action"]
            }
        }
