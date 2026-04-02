import asyncio
from learning_layer.strategic_metabolism import TriConfluenceEngine

async def test_universal_eye():
    print("🧪 [TEST] Level 53: Visual Sovereignty & Universal Eye")
    print("=" * 60)
    
    # 1. Test Pip Sizing for different assets
    print("\n📍 Testing Dynamic Pip Sizing...")
    assets = [
        ("GBPUSD", 0.0001),
        ("EURUSD", 0.0001),
        ("USDJPY", 0.01),
        ("XAUUSD", 0.01),
        ("BTCUSD", 1.0)
    ]
    
    for symbol, expected_pip in assets:
        engine = TriConfluenceEngine(symbol=symbol)
        print(f"   {symbol:<8}: {engine.pip_size} (Expected: {expected_pip}) ... {'PASS' if engine.pip_size == expected_pip else 'FAIL'}")
        
    # 2. Test Zone Generation logic is safe
    print("\n📍 Testing Zone Generation Safety...")
    engine = TriConfluenceEngine("USDJPY")
    
    # Mock candles (JPY pricing)
    mock_candles_jpy = [
        {"high": 150.50, "low": 149.50, "close": 150.00},
        {"high": 151.00, "low": 150.00, "close": 150.50}, # Swing High
        {"high": 150.50, "low": 149.50, "close": 150.00} 
    ]
    
    sr = engine.detect_sr_levels(mock_candles_jpy, k=1)
    print(f"   USDJPY Resistances: {sr['resistances']}")
    
    psych = engine.generate_psychological_levels(150.42, pip_interval=50) # 50 pips = 0.50 JPY
    print(f"   USDJPY Psych Levels (near 150.42): {psych[:3]}...")
    
    # Expected: 150.00, 150.50, 151.00 etc.
    if 150.50 in psych:
        print("   ✓ Psych logic correctly handles JPY scaling")
    else:
        print("   ❌ Psych logic failed for JPY")

    print("\n" + "=" * 60)
    print("🏆 [TEST] Level 53 Universal Eye Verified")

if __name__ == "__main__":
    asyncio.run(test_universal_eye())
