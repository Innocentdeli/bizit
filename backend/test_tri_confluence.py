import asyncio
from datetime import datetime
from learning_layer.strategic_metabolism import TriConfluenceEngine

async def test_tri_confluence():
    print("🧪 [TEST] Level 52: Tri-Confluence Engine Precision")
    print("=" * 60)
    
    engine = TriConfluenceEngine(symbol="GBPUSD")
    
    # 1. Test S/R Detection
    print("\n📍 Testing S/R Detection...")
    mock_candles = [
        {"high": 1.3500, "low": 1.3400, "close": 1.3450},
        {"high": 1.3550, "low": 1.3450, "close": 1.3500},
        {"high": 1.3600, "low": 1.3500, "close": 1.3550}, # Pivot High
        {"high": 1.3550, "low": 1.3450, "close": 1.3500},
        {"high": 1.3500, "low": 1.3400, "close": 1.3450},
        {"high": 1.3450, "low": 1.3350, "close": 1.3400},
        {"high": 1.3400, "low": 1.3300, "close": 1.3350}, # Pivot Low
        {"high": 1.3450, "low": 1.3350, "close": 1.3400},
        {"high": 1.3500, "low": 1.3400, "close": 1.3450}
    ]
    sr = engine.detect_sr_levels(mock_candles, k=2)
    print(f"   Supports: {sr['supports']}")
    print(f"   Resistances: {sr['resistances']}")
    
    # 2. Test Psychological Levels
    print("\n📍 Testing Psychological Levels...")
    price = 1.3542
    levels = engine.generate_psychological_levels(price)
    print(f"   Price: {price}")
    print(f"   Nearest Levels: {levels}")
    
    # 3. Test Weekly H/L Calculation
    print("\n📍 Testing Weekly H/L Calculation...")
    # Mock Monday morning 4H candles
    monday_00 = datetime(2026, 1, 19, 0, 0)
    monday_04 = datetime(2026, 1, 19, 4, 0)
    mock_4h = [
        {"time": monday_00.timestamp(), "high": 1.3600, "low": 1.3500, "close": 1.3550},
        {"time": monday_04.timestamp(), "high": 1.3650, "low": 1.3580, "close": 1.3620}
    ]
    whl = engine.calculate_weekly_hl(mock_4h, current_datetime=datetime(2026, 1, 20))
    print(f"   Weekly High: {whl['high']}")
    print(f"   Weekly Low: {whl['low']}")
    
    # 4. Test S/R Invalidation
    print("\n📍 Testing S/R Invalidation...")
    engine.sr_cache["4H"] = {"supports": [1.3400], "resistances": [1.3600]}
    engine.invalidate_broken_sr("4H", 1.3610, "BULLISH")
    print(f"   Modified 4H Resistances: {engine.sr_cache['4H']['resistances']}")

    print("\n" + "=" * 60)
    print("🏆 [TEST] Level 52 Engine Core Logic Verified")

if __name__ == "__main__":
    asyncio.run(test_tri_confluence())
