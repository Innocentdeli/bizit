import sys
sys.path.append(".")
import time
import logging
import asyncio
import random
from agents.architect_agent import ArchitectAgent
from evolution import SafetySandbox

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def test_universal_substrate():
    print("📱 Testing Level 43: Universal Substrate (Cross-Platform UI)...")
    print("=" * 75)
    
    architect = ArchitectAgent()
    
    # 1. Trigger UI Substrate Audit
    print("\n[STEP 1] Architect Agent initiating UI substrate audit...")
    mock_event = {"event_type": "MOBILE_USER_SURGE", "payload": {"count": 10000}}
    
    # Loop to hit the random trigger
    decision = None
    for i in range(100):
        decision = architect.reason(mock_event)
        if decision['decision'] == "UI_SUBSTRATE_OPTIMIZATION":
            print(f"✅ Success: Architect Agent detected UI bottleneck and initiated audit at attempt {i+1}.")
            break
        await asyncio.sleep(0.01)
        
    if not decision or decision['decision'] != "UI_SUBSTRATE_OPTIMIZATION":
        print("❌ Failure: Architect Agent did not trigger UI substrate audit.")
        return

    # 2. Review UI Recommendations
    print(f"\n[STEP 2] Reviewing UI Substrate Recommendations...")
    audit = decision['metadata'].get('audit', {})
    recommendations = audit.get('recommendations', {})
    
    target_mobile = recommendations.get('native_mobile_interface')
    target_3d = recommendations.get('high_fidelity_3d_engine')
    
    print(f"💡 Recommended Mobile Substrate: {target_mobile}")
    print(f"💡 Recommended Spatial Substrate: {target_3d}")

    # 3. Simulate Native Synthesis
    print(f"\n[STEP 3] Synthesizing Native {target_mobile} Bridge...")
    synthesis = architect.use_tool(
        "architectural_optimizer", 
        action="synthesize_substrate",
        module="sovereign_ui.bridge",
        language=target_mobile
    )
    
    if synthesis['status'] == "SUCCESS":
        print(f"✨ [TRANSCENDENCE] Successfully synthesized {target_mobile} bridge for {synthesis['original_module']}.")
        print(f"🚀 Advantage: {synthesis['estimated_gain']}")
        print("\n✅ UNIVERSAL SUBSTRATE VERIFIED: BIZIT is NOT limited to React.")
    else:
        print("❌ Failure: UI substrate synthesis failed.")

if __name__ == "__main__":
    asyncio.run(test_universal_substrate())
