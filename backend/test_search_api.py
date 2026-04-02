import requests
import json

def test_search_api():
    url = "http://localhost:8002/search"
    query = "latest NGN inflation rate and business impact"
    
    print(f"🔍 Testing /search API with query: '{query}'")
    try:
        response = requests.post(url, json={"query": query}, timeout=60)
        if response.status_code == 200:
            print("✅ Response Received!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_search_api()
