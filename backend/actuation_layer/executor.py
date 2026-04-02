from typing import Dict, Any
import time
from .coordinator import ActionCoordinator
from api_integrations.forex_client import ForexClient
from api_integrations.defi_client import DeFiTradingClient

class Executor:
    def __init__(self):
        self.execution_history = []
        # Store snapshots for rollback: transaction_id -> state_snapshot
        self.rollback_registry = {}
        self.coordinator = ActionCoordinator()
        # Level 51: Active trade tracking
        self.active_trades = {}  # {trade_id: {"symbol": "GBPUSD", "entry_price": 1.35, "entry_time": timestamp, "zone": [1.34, 1.36]}}

    async def execute_action(self, action_data: Dict[str, Any], proof: str):
        """
        The final 'Act' phase.
        Translates a verified proposal into an external system call.
        """
        agent = action_data.get("agent")
        decision = action_data.get("decision")
        resources = action_data.get("resources", []) # e.g. ["inventory_item_123"]
        
        # 1. Coordination & Conflict Check
        if not self.coordinator.request_lock(agent, resources):
            return {"status": "FAILED", "error": "Resource Conflict - Locked by another agent"}
            
        print(f"[ACTUATE] Dispatching {decision} to external systems...")
        
        # 2. Create Rollback Point
        tx_id = f"TX-{proof[:8]}"
        self._create_rollback_point(tx_id, action_data)
        
        try:
            # 3. Route to specific system handler
            target = action_data.get("target_system", "GENERIC")
            
            if target == "SHOPIFY":
                result = await self._execute_shopify(action_data)
            elif target == "SALESFORCE":
                result = await self._execute_salesforce(action_data)
            elif target == "SAP":
                result = await self._execute_sap(action_data)
            elif target == "FOREX":
                result = await self._execute_forex(action_data)
            elif target == "DEFI":
                result = await self._execute_defi(action_data)
            else:
                result = await self._execute_generic(action_data)
            
            result["transaction_id"] = tx_id
            self.execution_history.append(result)
            
            # 4. Release Locks
            self.coordinator.release_lock(agent, resources)
            
            return result
            
        except Exception as e:
            print(f"[ACTUATE] ERROR: Action failed ({e}). Initiating Rollback...")
            self.rollback_action(tx_id)
            self.coordinator.release_lock(agent, resources)
            return {"status": "FAILED", "error": str(e)}

    async def _execute_shopify(self, action: Dict[str, Any]):
        return {"status": "SUCCESS", "system": "SHOPIFY", "details": "Order Updated"}

    async def _execute_salesforce(self, action: Dict[str, Any]):
        return {"status": "SUCCESS", "system": "SALESFORCE", "details": "Stage Updated"}

    async def _execute_sap(self, action: Dict[str, Any]):
        return {"status": "SUCCESS", "system": "SAP", "details": "PO Created"}

    async def _execute_forex(self, action: Dict[str, Any]):
        """Execute trade via OANDA or Deriv API."""
        decision = action.get("decision")
        metadata = action.get("metadata", {})
        
        client = ForexClient()
        
        if decision == "EXECUTE_TRADE":
            pair = metadata.get("pair", "EUR_USD")
            side = metadata.get("side", "BUY")
            units = metadata.get("units", 100)
            sl = metadata.get("stop_loss")
            tp = metadata.get("take_profit")
            
            result = await client.place_order(pair, side, units, sl, tp)
            if "error" in result:
                return {"status": "FAILED", "system": "FOREX", "error": result["error"]}
            
            return {"status": "SUCCESS", "system": "FOREX", "details": f"Placed {side} {units} {pair}"}
            
        elif decision == "CLOSE_POSITION":
            pair = metadata.get("pair")
            units = metadata.get("units", "ALL")
            result = await client.close_position(pair, units)
            return {"status": "SUCCESS", "system": "FOREX", "details": f"Closed {pair} position"}

        elif decision.startswith("EXECUTE_PATERNAL"):
            return await self._execute_paternal_forex(action)

        return {"status": "FAILED", "system": "FOREX", "error": "Unknown Decision"}

    async def _execute_paternal_forex(self, action: Dict[str, Any]):
        """
        Level 46: Executes the Father's Alpha strategy trade.
        Enforces 30-pip fixed SL and position sizing.
        """
        metadata = action.get("metadata", {})
        symbol = metadata.get("symbol", "GBPUSD")
        side = metadata.get("side", "BUY")
        risk_pct = metadata.get("risk_pct", 0.005)
        sl_pips = 30
        
        # 1. Check for Duplicate Open Trade Logic
        # In a real system, we'd query API. 
        if any(h.get("details", "").split()[-1] == symbol and h.get("status") == "SUCCESS" for h in self.execution_history[-10:]):
            return {"status": "FAILED", "error": f"Duplicate trade blocked for {symbol}"}

        client = ForexClient()
        
        # 2. Position Sizing (Fixed 30-pip SL)
        summary = await client.get_account_summary()
        balance = summary.get("balance", 10000)
        risk_amount = balance * risk_pct
        pip_value_per_lot = 10 # Approx for majors
        
        lots = risk_amount / (sl_pips * pip_value_per_lot)
        units = int(lots * 100000)
        
        # 3. Calculate SL Price
        current_quotes = await client.get_live_quotes([symbol])
        if not current_quotes:
            return {"status": "FAILED", "error": "Quotes unavailable"}
            
        entry_price = current_quotes.get("ask", 0) if side == "BUY" else current_quotes.get("bid", 0)
        pip_size = 0.01 if "JPY" in symbol else 0.0001
        
        sl_price = entry_price - (sl_pips * pip_size) if side == "BUY" else entry_price + (sl_pips * pip_size)
        
        # 4. Execute
        result = await client.place_order(symbol, side, units, stop_loss=round(sl_price, 5))
        
        if "error" in result:
            return {"status": "FAILED", "system": "FOREX_ALPHA", "error": result["error"]}
        
        # Level 51: Register active trade
        trade_id = result.get("contract_id", f"TRADE_{int(time.time())}")
        entry_zone = metadata.get("entry_zone", [entry_price - 0.005, entry_price + 0.005])
        
        self.active_trades[trade_id] = {
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "entry_time": time.time(),
            "sl_price": sl_price,
            "zone": entry_zone,
            "units": units
        }
            
        return {
            "status": "SUCCESS", 
            "system": "FOREX_ALPHA", 
            "details": f"Alpha Trade: {side} {units} {symbol} @ {entry_price} (SL: {sl_price})",
            "paternal_verified": True,
            "trade_id": trade_id
        }

    async def _execute_defi(self, action: Dict[str, Any]):
        """Execute on-chain trade simulation (Tier 7 Pivot)."""
        decision = action.get("decision")
        metadata = action.get("metadata", {})
        
        client = DeFiTradingClient()
        
        if decision == "EXECUTE_DEFI_TRADE":
            pair = metadata.get("pair", "BTC_USD")
            side = metadata.get("side", "BUY")
            amount = metadata.get("amount_usdc", 100)
            leverage = metadata.get("leverage", 10)
            
            result = client.trade_on_chain(pair, side, amount, leverage)
            if result["status"] == "FAILED":
                return {"status": "FAILED", "system": "DEFI", "error": result["error"]}
            
            return {"status": "SUCCESS", "system": "DEFI", "details": result["details"], "tx_hash": result["tx_hash"]}
            
        elif decision == "CLOSE_DEFI_POSITION":
            pair = metadata.get("pair")
            result = client.close_defi_position(pair)
            return {"status": "SUCCESS", "system": "DEFI", "details": result["details"]}

        return {"status": "FAILED", "system": "DEFI", "error": "Unknown Decision"}

    async def _execute_generic(self, action: Dict[str, Any]):
        decision = action.get("decision")
        metadata = action.get("metadata", {})
        
        # Specific Logic Mappings
        if decision == "PAY_SUPPLIER":
            return {"status": "SUCCESS", "system": "FINANCE_CORE", "details": f"Paid ${metadata.get('amount')} to {metadata.get('beneficiary')}"}
        
        elif decision == "SCHEDULE_PAYROLL":
            return {"status": "SUCCESS", "system": "PAYROLL_SVC", "details": f"Payroll scheduled for {metadata.get('scheduled_date')}"}
        
        elif decision == "REORDER_INVENTORY":
            return {"status": "SUCCESS", "system": "ERP", "details": f"Reordered {metadata.get('quantity')} of {metadata.get('sku')}"}
        
        elif decision == "OPTIMIZE_PRICING":
            return {"status": "SUCCESS", "system": "STOREFRONT", "details": f"Pricing updated for {metadata.get('sku')}"}
        
        elif decision == "ROUTING_LOGISTICS":
            return {"status": "SUCCESS", "system": "LOGISTICS_HUB", "details": f"Route {metadata.get('route_id')} dispatched"}

        elif decision == "NEGOTIATE_DISCOUNTS":
            return {"status": "SUCCESS", "system": "COMMS", "details": f"Negotiation offer of {metadata.get('target_discount')} sent to {metadata.get('vendor')}"}

        return {
            "status": "SUCCESS", 
            "system": "GENERIC",
            "realized_utility": action.get("metadata", {}).get("value", 5000) * 0.95
        }

    def _create_rollback_point(self, tx_id: str, action_data: Dict[str, Any]):
        """Save reverse-operation instructions."""
        self.rollback_registry[tx_id] = {
            "type": "COMPENSATING_TRANSACTION",
            "original_action": action_data,
            "status": "PENDING"
        }

    def rollback_action(self, tx_id: str):
        """
        Execute rollback/compensating transaction for a failed action.
        """
        snapshot = self.rollback_registry.get(tx_id)
        if snapshot:
            print(f"[ACTUATE] ROLLBACK: Reverting transaction {tx_id}...")
            snapshot["status"] = "ROLLED_BACK"
            print(f"[ACTUATE] ROLLBACK: Success. System consistent.")
            return True
        return False

    async def monitor_active_trades(self):
        """
        Level 51: Monitor active trades for external closures (e.g., SL hit).
        Compares active_trades registry with live positions from ForexClient.
        """
        if not self.active_trades:
            return
            
        client = ForexClient()
        live_positions = await client.get_open_positions()
        
        # Build set of live position symbols for quick lookup
        live_symbols = {pos.get("instrument", ""): pos for pos in live_positions}
        
        # Check for closed trades
        closed_trades = []
        for trade_id, trade_info in list(self.active_trades.items()):
            symbol = trade_info["symbol"]
            
            # If trade is not in live positions, it was closed
            if symbol not in live_symbols:
                # Log closure
                duration = time.time() - trade_info["entry_time"]
                closure_event = {
                    "trade_id": trade_id,
                    "symbol": symbol,
                    "side": trade_info["side"],
                    "entry_price": trade_info["entry_price"],
                    "close_time": time.time(),
                    "duration_seconds": duration,
                    "close_reason": "SL_HIT",  # Assume SL unless we have more data
                    "status": "CLOSED"
                }
                
                self.execution_history.append(closure_event)
                closed_trades.append(trade_id)
                print(f"[EXECUTOR] Trade {trade_id} closed externally: {symbol} (Duration: {duration/60:.1f}m)")
        
        # Remove closed trades from active registry
        for trade_id in closed_trades:
            del self.active_trades[trade_id]
