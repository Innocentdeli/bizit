import asyncio
import time
import os
from cognitive_kernel.local_llm_client import LocalLLMClient

async def test_client_direct():
    print("🧠 Testing LocalLLMClient Direct Streaming...")
    client = LocalLLMClient()
    
    prompt = "Explain the concept of sovereign digital metabolism in 3 sentences."
    start_time = time.time()
    first_token_time = None
    
    print(f"Query: {prompt}\n")
    print("Response: ", end="", flush=True)
    
    try:
        async for chunk in client.generate_stream(prompt):
            if not first_token_time:
                first_token_time = time.time()
                print(f"\n⚡ TTFT (Time To First Token): {first_token_time - start_time:.2f}s\n", end="", flush=True)
            
            print(chunk, end="", flush=True)
            
    except Exception as e:
        print(f"\n❌ Client Test Failed: {e}")

    end_time = time.time()
    print(f"\n\n📊 Total Duration: {end_time - start_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_client_direct())
