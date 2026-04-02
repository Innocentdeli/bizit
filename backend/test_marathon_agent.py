import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from agents.pulse_agent import PulseAgent
from core.config import ConfigLoader

async def test_marathon_loop():
    print("🧠 [MARATHON_TEST] Initiating Autonomous Self-Correction Loop...")
    
    config = ConfigLoader(config_path="c:/bizit/config.yaml")
    api_key = config.get("gemini.api_key")
    
    if not api_key:
        print("⚠️ [SKIP] Running in MOCK Mode (No API Key).")

    agent = PulseAgent()
    
    mock_signal = {
        "event_type": "ECON_TICK",
        "payload": {
            "variable": "NGN/USD",
            "value": 1650,
            "change": 45.0,
            "title": "Naira Volatility Alert"
        }
    }
    
    print("\n--- Phase 1: Ingestion & Distillation ---")
    # This calls orchestrate_marathon_task (Level 60 Hackathon logic)
    result = await agent.orchestrate_marathon_task(mock_signal)
    
    print("\n[FINAL_DIRECTIVE] Sovereign Decision:")
    import json
    print(json.dumps(result, indent=2))
    
    if "thought_signature" in result:
        print(f"\n✅ [SUCCESS] Marathon Agent completed with Thinking Level: {result['thought_signature']['level']}")
    else:
        print("\n❌ [FAILURE] Thought Signature missing.")

if __name__ == "__main__":
    asyncio.run(test_marathon_loop())
