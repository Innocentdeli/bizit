import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from cognitive_kernel.gemini_client import GeminiClient
from core.config import ConfigLoader

async def test_reasoning():
    print("🧬 [TEST] Initiating Gemini 3 Sovereign Reasoning Test...")
    
    config = ConfigLoader(config_path="c:/bizit/config.yaml")
    api_key = config.get("gemini.api_key") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️ [SKIP] No GEMINI_API_KEY found. Skipping live test.")
        return

    client = GeminiClient(api_key=api_key)
    
    prompt = """
    Market Context: NIGERIA FX POLICY SHIFT. 
    Variable: NGN/USD Exchange Rate. 
    Current Value: 1650. 
    Recent Delta: +400bps hike announced by CBN.
    
    Goal: CAPITAL_PRESERVATION.
    
    Analyze and propose an optimal BIZIT action.
    """
    
    system_instr = "You are the BIZIT Sovereign Intelligence Lobe. Return JSON with 'thought_process', 'decision', and 'confidence'."
    
    print("\n--- Sending to Gemini 1.5 Pro ---")
    result = await client.generate_reasoning(prompt, system_instruction=system_instr)
    
    print("\n[RESULT] Gemini Response:")
    import json
    print(json.dumps(result, indent=2))
    
    if "decision" in result:
        print("\n✅ [SUCCESS] BIZIT successfully reasoned via Gemini!")
    else:
        print("\n❌ [FAILURE] Invalid response format.")

if __name__ == "__main__":
    asyncio.run(test_reasoning())
