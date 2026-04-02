import requests
r = requests.get('http://localhost:8002/status')
print(f"Status: {r.json()}")
# Since I added a get_status endpoint, let me check if I can add document count there.
