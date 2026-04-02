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
