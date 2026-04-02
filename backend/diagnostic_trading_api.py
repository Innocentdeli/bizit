import requests
import json
import time

def test_trading_api():
    url = "http://localhost:8000/trading/market"
    print(f"📡 [DIAGNOSTIC] Testing {url}...")
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            candles = data.get("candles", [])
            print(f"✅ [DIAGNOSTIC] API Reachable. Latency: {duration:.2f}s")
            print(f"📊 [DIAGNOSTIC] Symbol: {data.get('symbol')}")
            print(f"🕯️ [DIAGNOSTIC] Candle Count: {len(candles)}")
            
            if len(candles) > 0:
                print(f"📝 [DIAGNOSTIC] Latest Close: {candles[-1]['close']}")
                print(f"🧱 [DIAGNOSTIC] Zones Found: {len(data.get('zones', []))}")
            else:
                print("⚠ [DIAGNOSTIC] WARNING: Candle list is EMPTY. Check Deriv connectivity.")
        else:
            print(f"❌ [DIAGNOSTIC] API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ [DIAGNOSTIC] Failed to connect to API: {e}")
        print("💡 [DIAGNOSTIC] TIP: Ensure 'python run_dashboard.py' is running in a terminal.")

if __name__ == "__main__":
    test_trading_api()
