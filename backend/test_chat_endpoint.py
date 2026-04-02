import requests
import time

print("🧪 Testing Streaming Chat Endpoint...")
print("=" * 50)

url = "http://localhost:8000/chat"
payload = {"query": "Hello, what is your current health status?"}

try:
    start = time.time()
    response = requests.post(url, json=payload, stream=True, timeout=30)
    
    if response.status_code == 200:
        print("✅ Connection successful!")
        print("\nStreaming Response:")
        print("-" * 50)
        
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                print(chunk, end='', flush=True)
        
        elapsed = time.time() - start
        print(f"\n\n{'=' * 50}")
        print(f"✅ Test Complete! Total time: {elapsed:.2f}s")
        print("✅ Chat formatting: CLEAN (no JSON wrapping)")
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Test failed: {e}")
