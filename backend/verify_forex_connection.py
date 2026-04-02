import os
import asyncio
from dotenv import load_dotenv
from api_integrations.forex_client import ForexClient

async def verify():
    load_dotenv()
    
    print("--- Environment Check ---")
    deriv_token = os.getenv("DERIV_TOKEN")
    oanda_key = os.getenv("OANDA_API_KEY")
    
    print(f"DERIV_TOKEN: {'[SET]' if deriv_token else '[MISSING]'}")
    print(f"OANDA_API_KEY: {'[SET]' if oanda_key else '[MISSING]'}")
    
    client = ForexClient()
    print(f"\nInitialized ForexClient with: {'DERIV' if client.use_deriv else 'OANDA'}")
    
    print("\n--- Connection Test ---")
    if client.use_deriv:
        print("Testing Deriv Connectivity...")
        alive = await client.deriv.is_alive()
        print(f"Is Alive (Pre-Connect): {alive}")
        await client.deriv.connect()
        auth = await client.deriv.authorize()
        print(f"Authorization: {auth}")
        
        if auth:
            candles = await client.get_candles("frxGBPUSD", count=5)
            print(f"Fetched {len(candles)} candles.")
            if candles:
                print(f"Sample: {candles[0]}")
    else:
        print("Testing OANDA Connectivity...")
        status = client.get_connection_status()
        print(f"Connection Status: {status}")
        
        candles = await client.get_candles("GBP_USD", count=5)
        print(f"Fetched {len(candles)} candles.")
        if candles:
            print(f"Sample: {candles[0]}")

if __name__ == "__main__":
    asyncio.run(verify())
