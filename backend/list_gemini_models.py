import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[ERROR] No API Key found in .env")
    exit()

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get("models", [])
        print("[SUCCESS] Available Models:")
        for m in models:
            if "gemini" in m["name"].lower():
                print(f" - {m['name']}")
    else:
        print(f"[ERROR] {response.status_code}: {response.text}")
except Exception as e:
    print(f"[FAILED] {e}")
