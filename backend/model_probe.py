import httpx
import asyncio
import json

async def check_model(model_name):
    api_key = "AIzaSyDoJqB6CLyNWHhJNgBO3PEwGdf5aAaj_RI"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": "Say G3_ONLINE if you are Gemini 3."}]}],
        "generationConfig": {"maxOutputTokens": 10}
    }
    
    print(f"--- Probing: {model_name} ---")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                print(f"✅ SUCCESS: {model_name} is LIVE.")
                data = response.json()
                print(f"DEBUG_DATA: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ FAIL: {model_name} returned {response.status_code}")
                # print(response.text)
                return False
        except Exception as e:
            print(f"⚠️ ERROR probing {model_name}: {e}")
            return False

async def main():
    model = "gemini-3-pro-preview"
    success = await check_model(model)
    if success:
        print(f"\n🚀 GEMINI 3.0 PRO IS READY FOR BIZIT.")

if __name__ == "__main__":
    asyncio.run(main())
