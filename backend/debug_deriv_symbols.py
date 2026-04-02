import asyncio
import os
from dotenv import load_dotenv
from api_integrations.deriv_client import DerivClient

async def debug_deriv_symbols():
    load_dotenv()
    token = os.getenv("DERIV_TOKEN")
    client = DerivClient(token=token)
    
    print("🔍 [DEBUG] Testing Deriv Symbols...")
    
    # Test 1: GBPUSD (Standard)
    print("\n📍 Testing 'GBPUSD'...")
    candles_1 = await client.get_candles("GBPUSD", count=2)
    print(f"Result: {'SUCCESS' if candles_1 else 'FAILED'}")
    
    # Test 2: frxGBPUSD (Deriv Format)
    print("\n📍 Testing 'frxGBPUSD'...")
    candles_2 = await client.get_candles("frxGBPUSD", count=2)
    print(f"Result: {'SUCCESS' if candles_2 else 'FAILED'}")
    
    # Test 3: GBP_USD (OANDA Format)
    print("\n📍 Testing 'GBP_USD'...")
    candles_3 = await client.get_candles("GBP_USD", count=2)
    print(f"Result: {'SUCCESS' if candles_3 else 'FAILED'}")

    await client.close()
    print("\n--- Diagnostic Complete ---")

if __name__ == "__main__":
    asyncio.run(debug_deriv_symbols())
