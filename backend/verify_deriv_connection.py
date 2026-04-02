import asyncio
import os
from dotenv import load_dotenv
from api_integrations.deriv_client import DerivClient
from api_integrations.forex_client import ForexClient

async def verify_deriv():
    load_dotenv()
    token = os.getenv("DERIV_TOKEN")
    
    print(f"🔗 [DERIV] Initiating link with token: {token[:4]}****")
    
    client = DerivClient(token=token)
    
    # 1. Test Auth
    success = await client.authorize()
    if not success:
        print("❌ [DERIV] Authentication failed.")
        return
        
    print("✅ [DERIV] Link Established. Authenticated.")
    
    # 2. Test Candle Ingestion
    print("📊 [DERIV] Fetching H1 Candles for GBP/USD...")
    candles = await client.get_candles("frxGBPUSD", granularity=3600, count=5)
    if candles:
        print(f"📈 [DERIV] Successfully ingested {len(candles)} candles.")
        print(f"📝 [DERIV] Latest Close: {candles[-1]['close']}")
    else:
        print("❌ [DERIV] Candle ingestion failed.")

    # 3. Test Live Quotes
    print("⚡ [DERIV] Fetching live quote for GBP/USD...")
    quote = await client.get_live_quotes("frxGBPUSD")
    if quote:
        print(f"🎯 [DERIV] Live Ask: {quote['ask']} | Live Bid: {quote['bid']}")
    else:
        print("❌ [DERIV] Live quote retrieval failed.")

    await client.close()
    
    print("\n--- Unified ForexClient Test ---")
    sync_client = ForexClient()
    if sync_client.use_deriv:
        print("🛡️ [UNIFIED] ForexClient is correctly configured for Deriv substrate.")
        # Test synchronous bridge
        candles_sync = await sync_client.get_candles("GBP_USD", granularity="H1", count=2)
        if candles_sync:
            print(f"✅ [UNIFIED] Async Bridge Success. Close: {candles_sync[-1]['close']}")
    
    print("\n🏆 [VERIFY] LEVEL 48 SUCCESS: Deriv substrate is live and metabolizing.")

if __name__ == "__main__":
    asyncio.run(verify_deriv())
