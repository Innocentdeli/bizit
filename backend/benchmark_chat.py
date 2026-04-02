import asyncio
import httpx
import time
import sys
import os

async def benchmark_chat_stream():
    print("⚡ Benchmarking Optimized Symbiotic Chat Streaming...")
    url = "http://localhost:8000/chat"
    payload = {"query": "Explain your metabolic purpose and future projection."}
    
    start_time = time.time()
    first_token_time = None
    total_chunks = 0
    full_response = ""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    print(f"❌ Error: {response.status_code}")
                    return

                async for chunk in response.aiter_text():
                    if not first_token_time:
                        first_token_time = time.time()
                        print(f"✅ First Token Received in: {first_token_time - start_time:.2f}s")
                    
                    full_response += chunk
                    total_chunks += 1
                    # print(chunk, end="", flush=True)

    except Exception as e:
        print(f"❌ Benchmark Failed: {e}")
        return

    end_time = time.time()
    print(f"\n\n📊 STATS:")
    print(f"- Total Duration: {end_time - start_time:.2f}s")
    print(f"- TTFT (Time to First Token): {first_token_time - start_time:.2f}s")
    print(f"- Total Chunks Received: {total_chunks}")
    print(f"- Response Length: {len(full_response)} characters")
    
    if first_token_time - start_time < 2.5:
        print("🚀 PERFORMANCE: OPTIMAL")
    else:
        print("⚠️ PERFORMANCE: SUB-OPTIMAL (Check Ollama load)")

if __name__ == "__main__":
    asyncio.run(benchmark_chat_stream())
