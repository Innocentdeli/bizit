from agents.base_agent import BaseAgent
from cognitive_kernel.tools.web_search_tool import WebSearchTool
from cognitive_kernel.tools.file_ops_tool import FileOpsTool
from cognitive_kernel.tools.defi_tool import DeFiTool

class FinanceAgent(BaseAgent):
    def __init__(self, name: str = "FinanceBot-1"):
        super().__init__(name, domain="Finance")
        # Level 35: Omni-Intelligence - Equip Tools
        self.register_tool(WebSearchTool())
        self.register_tool(FileOpsTool())
        # Level 36c: DeFi Wallet
        self.register_tool(DeFiTool())

    def reason(self, state: dict):
        event_type = state.get("event_type", "")
        payload = state.get("payload", {})
        value = payload.get("value", 0)
        
        decision = "ANALYZING"
        metadata = {}
        confidence = 0.85

        if "PAYMENT" in event_type or "INVOICE" in event_type:
            decision = "PAY_SUPPLIER"
            metadata = {"amount": value, "beneficiary": "SUPPLIER_ENTITY", "priority": "HIGH"}
            confidence = 0.95
        
        elif "PAYROLL" in event_type:
            decision = "SCHEDULE_PAYROLL"
            metadata = {"total_payroll": value, "cycle": "MONTHLY", "scheduled_date": "2026-01-31"}
            confidence = 0.98

        elif "DEFI_TICK" in event_type:
            instrument = payload.get("instrument", "BTC_USD")
            price = payload.get("price", 0)
            
            # Tier 7 Pivot: DeFi Strategist Logic
            # Retrieve DeFi vitals from grounding state
            vitals = getattr(self, 'state_vitals', {}) # Injected by main loop
            usdc = vitals.get("defi", {}).get("usdc_balance", 0)
            gas = vitals.get("defi", {}).get("gas_eth", 0)
            
            decision = "MONITORING_DEX_FEED"
            metadata = {"instrument": instrument, "price": price}
            confidence = 0.70
            
            if price > 0 and usdc > 500 and gas > 0.01:
                # Simple Momentum signal on BTC/ETH
                # (Demonstration logic: trade on even-price ticks)
                if int(price * 100) % 2 == 0:
                    trade_amount = min(500, usdc * 0.1) # 10% risk
                    
                    # Level 38: Swarm Consensus Check
                    if trade_amount > 100: # Virtual threshold for "High Stakes"
                        decision = "PROPOSE_CONSENSUS"
                        metadata = {
                            "action": "EXECUTE_DEFI_TRADE",
                            "pair": instrument,
                            "side": "BUY",
                            "amount_usdc": trade_amount,
                            "leverage": 10,
                            "reason": "High-value trade requires swarm validation."
                        }
                        confidence = 0.99
                    else:
                        decision = "EXECUTE_DEFI_TRADE"
                        metadata = {
                            "pair": instrument,
                            "side": "BUY",
                            "amount_usdc": trade_amount,
                            "leverage": 10,
                            "target_system": "DEFI",
                            "strategy": "DECENTRALIZED_MOMENTUM"
                        }
                        confidence = 0.88
        
        elif "FOREX_TICK" in event_type:
            instrument = payload.get("instrument", "EUR_USD")
            price = payload.get("price", 0)
            heuristic = payload.get("heuristic", "UNSET")
            
            decision = "FOREX_MARKET_MONITOR"
            metadata = {"instrument": instrument, "price": price, "heuristic": heuristic}
            confidence = 0.82
            
            # Level 45: Applied Forex Heuristic
            if "Bullish" in heuristic and price > 0:
                decision = "PROPOSE_FOREX_LONG"
                confidence = 0.94
                metadata["side"] = "BUY"
            elif "Bearish" in heuristic and price > 0:
                decision = "PROPOSE_FOREX_SHORT"
                confidence = 0.94
                metadata["side"] = "SELL"

        elif "BUDGET" in event_type:
            decision = "ALLOCATE_BUDGET"
            metadata = {"department": "R&D", "allocation": value}
            confidence = 0.90
        
        elif "PATERNAL_ALPHA_TICK" in event_type:
            # Level 46: The Father's Alpha Strategy
            return self.reason_paternal_alpha(state)
        
        else:
            decision = "CAPITAL_ALLOCATION_APPROVED"
            metadata = {"budget_impact": value * -1}
            confidence = 0.92

        return {
            "agent": self.name,
            "decision": decision,
            "confidence": confidence,
            "metadata": metadata
        }

    def reason_paternal_alpha(self, state: dict):
        """
        Level 46: Core implementation of the Father's 3-Point Confluence Rule.
        """
        payload = state.get("payload", {})
        symbol = payload.get("symbol", "GBPUSD")
        close = payload.get("close", 0)
        prev_close = payload.get("prev_close", 0)
        
        # Confluence Signals injected by Main Loop Meta-Analysis
        signal = payload.get("confluence_signal") # 'BUY', 'SELL', or None
        reason = payload.get("confluence_reason", "No Confluence")
        
        if signal == "BUY":
            return {
                "agent": self.name,
                "decision": "EXECUTE_PATERNAL_LONG",
                "confidence": 1.0, # Complete trust in the Father's Alpha
                "metadata": {
                    "symbol": symbol,
                    "side": "BUY",
                    "reason": reason,
                    "stop_loss_pips": 30,
                    "risk_pct": 0.005 # Default 0.5% risk
                }
            }
        elif signal == "SELL":
            return {
                "agent": self.name,
                "decision": "EXECUTE_PATERNAL_SHORT",
                "confidence": 1.0,
                "metadata": {
                    "symbol": symbol,
                    "side": "SELL",
                    "reason": reason,
                    "stop_loss_pips": 30,
                    "risk_pct": 0.005
                }
            }
            
        return {
            "agent": self.name,
            "decision": "MONITORING_ALPHA",
            "confidence": 0.90,
            "metadata": {"symbol": symbol, "status": "WAITING_FOR_CONFLUENCE"}
        }
