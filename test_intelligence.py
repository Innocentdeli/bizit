import requests
import json

BASE_URL = "http://localhost:8002/search"

queries = [
    {"query": "Current dollar to naira rate and why it is rising this week", "strategy": "ARBITRAGE"},
    {"query": "Cheapest places to buy iPhone 13 in Nigeria with warranty", "strategy": "GROWTH"},
    {"query": "Why fuel prices increased in Nigeria and when it may drop", "strategy": "PRESERVE"},
    {"query": "Is POS business still profitable in Nigeria in 2026?", "strategy": "ARBITRAGE"},
    {"query": "Best business to start with 500k in Lagos right now", "strategy": "GROWTH"},
    {"query": "Should I buy land in Ibeju-Lekki or Epe for long-term investment?", "strategy": "GROWTH"},
    {"query": "Most reliable marketplaces to source wholesale phones in Nigeria", "strategy": "ARBITRAGE"},
    {"query": "Why are laptop prices increasing in Nigeria despite stable dollar rate?", "strategy": "PRESERVE"},
    {"query": "Impact of new CBN policies on small businesses in Nigeria", "strategy": "PRESERVE"},
    {"query": "Best time to import goods into Nigeria this year", "strategy": "GROWTH"}
]

def test_query(q_data):
    print(f"\n TESTING: {q_data['query']} | Strategy: {q_data['strategy']}")
    try:
        response = requests.post(BASE_URL, json=q_data, timeout=180) # Increased timeout
        if response.status_code == 200:
            data = response.json()
            brief = data.get('brief', {})
            print(f" HEADLINE: {brief.get('headline')}")
            print(f" SIGNAL: {brief.get('signal')[:100]}...")
            print(f" FORECAST: {brief.get('forecast')}")
            print(f" RECOMMENDATIONS: {brief.get('recommendations')}")
            print(f" CONFIDENCE: {brief.get('confidence')}")
            print(f" SOURCES: {len(brief.get('sources', []))}")
            print(" STATUS: SUCCESS")
        else:
            print(f" STATUS: FAILED ({response.status_code})")
            print(response.text)
    except Exception as e:
        print(f" STATUS: ERROR ({e})")

if __name__ == "__main__":
    for q in queries:
        test_query(q)
