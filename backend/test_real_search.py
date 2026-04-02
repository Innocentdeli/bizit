import sys
sys.path.append(".")
from cognitive_kernel.tools.web_search_tool import WebSearchTool
import os
import json

def test_real_search():
    print("🧠 Testing Level 35c: Real Web Search (Serper.dev)...")
    print("=" * 50)
    
    # Check for API Key
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("⚠️  WARNING: SERPER_API_KEY not found in environment.")
        print("Please add it to your .env file or set it in your terminal.")
        print("Example: set SERPER_API_KEY=your_key")
        # We proceed anyway to show the error handling working
    else:
        print(f"🔑 API Key found: {api_key[:4]}...****")

    tool = WebSearchTool()
    query = "Tesla stock price today"
    
    print(f"\n🔍 Executing Search: '{query}'")
    result = tool.execute(query=query)
    
    print("\n📋 Result:")
    print("-" * 50)
    print(json.dumps(result, indent=2))
    print("-" * 50)
    
    if result.get("status") == "success":
        print("✅ PASS: Real Search Successful!")
        print(f"Provider: {result.get('provider')}")
    else:
        print("❌ FAIL: Search Failed (Expected if no API key is set)")
        print(f"Message: {result.get('message')}")

if __name__ == "__main__":
    test_real_search()
