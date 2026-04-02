import asyncio
import json
from learning_layer.strategic_metabolism import StrategicMetabolism
from agents.finance_agent import FinanceAgent

async def verify_paternal_alpha():
    print("🔭 [VERIFY] Initiating Level 46: The Father's Alpha Verification...")
    
    symbol = "GBPUSD"
    meta = StrategicMetabolism(symbol=symbol)
    agent = FinanceAgent()
    
    # 1. Define Market Scenario (Historical H4 Data)
    # Weekly High: 1.32500, Weekly Low: 1.30000
    h4_data = [
        {"high": 1.32500, "low": 1.32400}, # Top High
        {"high": 1.32450, "low": 1.32300}, # Second High (Weekly High Zone center ~1.32475)
        {"high": 1.30100, "low": 1.30000}, # Low
        {"high": 1.30200, "low": 1.30050}  # Second Low
    ]
    
    weekly_hl = meta.compute_weekly_hl_zones(h4_data)
    print(f"📍 [VERIFY] Weekly High Zone Top: {weekly_hl['high']['top']:.5f}")
    
    # 2. Define Daily Zones
    daily_zones = [{"center": 1.32200, "top": 1.32208, "bot": 1.32192}] # Daily Resistance at 1.32200
    
    # 3. Simulate Entry Trigger (1H Data)
    # prev_close at 1.32150 (below daily resistance)
    # close at 1.32560 (above resistance, above psych 1.32500, above weekly high 1.32550)
    prev_close = 1.32150
    close = 1.32560 # Closest psych is 1.32500 (rounded to 50 pip grid)
    
    print(f"📊 [VERIFY] Current Close: {close:.5f} | Prev Close: {prev_close:.5f}")
    print(f"🧱 [VERIFY] Daily Resistance: {daily_zones[0]['top']:.5f}")
    print(f"🎯 [VERIFY] Psych Level Check: {close} > {meta.get_psych_level(close)} is {close > meta.get_psych_level(close)}")
    
    signal = meta.check_confluence(prev_close, close, daily_zones, weekly_hl)
    
    if signal == "BUY":
        print("✅ [VERIFY] Triple Confluence Signal: BUY detected.")
        reason = "Daily Cross + Psych Positive + Weekly HL Breakout"
    else:
        print(f"❌ [VERIFY] Signal Failed. Confluence result: {signal}")
        return

    # 4. Agent Reasoning
    test_event = {
        "event_type": "PATERNAL_ALPHA_TICK",
        "payload": {
            "symbol": symbol,
            "close": close,
            "prev_close": prev_close,
            "confluence_signal": signal,
            "confluence_reason": reason
        }
    }
    
    reasoning = agent.reason(test_event)
    print(f"🤖 [VERIFY] Agent Decision: {reasoning['decision']}")
    print(f"📜 [VERIFY] Reason: {reasoning['metadata']['reason']}")
    
    # 5. Position Sizing & SL (Fixed 30 Pips)
    sl_pips = reasoning['metadata']['stop_loss_pips']
    pip_size = 0.0001
    sl_price = close - (sl_pips * pip_size)
    print(f"🛡️ [VERIFY] Fixed Stop Loss: {sl_price:.5f} (30 pips from {close})")

    if reasoning['decision'] == "EXECUTE_PATERNAL_LONG" and sl_pips == 30:
        print("\n🏆 [VERIFY] LEVEL 46 SUCCESS: BIZIT has mastered the Father's Alpha.")
    else:
        print("\n⚠️ [VERIFY] LEVEL 46 FAILED: Strategy deviation detected.")

if __name__ == "__main__":
    asyncio.run(verify_paternal_alpha())
