import os
import logging
import random
import time
from typing import Dict, List, Optional, Any
from core.state import OrganismState

logger = logging.getLogger(__name__)

class DeFiTradingClient:
    """
    Tier 7: Sovereign DeFi Bridge (Sandbox).
    Simulates permissionless trading via Smart Contracts (e.g. gTrade, Synthetix).
    Bypasses geographic OANDA restrictions by using decentralized protocol logic.
    """
    def __init__(self, sandbox: bool = True):
        self.sandbox = sandbox
        self.state = OrganismState()
        logger.info(f"DeFiTradingClient initialized in {'SANDBOX' if sandbox else 'LIVE'} mode")

    def get_onchain_balance(self) -> Dict[str, float]:
        """Fetch current collateral and gas from state."""
        return self.state.defi_vitals

    def trade_on_chain(self, pair: str, side: str, amount_usdc: float, leverage: int = 10) -> Dict[str, Any]:
        """
        Simulates an on-chain trade transaction.
        In a real scenario, this would use web3.py to call a Smart Contract.
        """
        try:
            print(f"🌉 [DEFI] Initiating On-Chain Tx: {side} {leverage}x on {pair} with ${amount_usdc} USDC")
            
            # Simulate Gas usage
            gas_cost = random.uniform(0.001, 0.005) # ETH
            current_gas = self.state.defi_vitals.get("gas_eth", 0.5)
            
            if current_gas < gas_cost:
                return {"status": "FAILED", "error": "Insufficient ETH for Gas"}

            # Simulate Tx delay (Blockchain latency)
            time.sleep(1) 
            
            tx_hash = f"0x{os.urandom(32).hex()}"
            
            # Update State
            new_gas = current_gas - gas_cost
            new_balance = self.state.defi_vitals.get("usdc_balance", 10000.0) - amount_usdc
            
            self.state.update_defi_vitals({
                "usdc_balance": new_balance,
                "gas_eth": new_gas,
                "active_positions": self.state.defi_vitals.get("active_positions", []) + [{
                    "pair": pair,
                    "side": side,
                    "amount": amount_usdc,
                    "leverage": leverage,
                    "entry_price": self.state.defi_quotes.get(pair, 0),
                    "tx_hash": tx_hash
                }]
            })

            return {
                "status": "SUCCESS",
                "tx_hash": tx_hash,
                "gas_used": gas_cost,
                "details": f"On-chain {side} position opened for {pair}"
            }

        except Exception as e:
            logger.error(f"DeFi Trade Failed: {e}")
            return {"status": "FAILED", "error": str(e)}

    def close_defi_position(self, pair: str) -> Dict[str, Any]:
        """Simulates closing an on-chain position."""
        positions = self.state.defi_vitals.get("active_positions", [])
        active = [p for p in positions if p["pair"] == pair]
        
        if not active:
            return {"status": "FAILED", "error": f"No active position for {pair}"}
            
        print(f"🌉 [DEFI] Closing On-Chain Position: {pair}")
        
        # Simulate PnL (Mock)
        exit_price = self.state.defi_quotes.get(pair, 0)
        pnl = random.uniform(-50, 150) # Mock gain/loss
        
        new_balance = self.state.defi_vitals.get("usdc_balance", 10000.0) + active[0]["amount"] + pnl
        remaining = [p for p in positions if p["pair"] != pair]
        
        self.state.update_defi_vitals({
            "usdc_balance": new_balance,
            "net_pnl": self.state.defi_vitals.get("net_pnl", 0) + pnl,
            "active_positions": remaining
        })
        
        return {"status": "SUCCESS", "pnl": pnl, "details": f"Closed {pair} with ${pnl:.2f} PnL"}
