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

async def test_transcendence():
    print("✨ Testing Level 40: Transcendence (Recursive Self-Improvement)...")
    print("=" * 70)
    
    architect = ArchitectAgent()
    sandbox = SafetySandbox()
    
    # Simulate an event that triggers architectural focus
    print("\n[STEP 1] Architect Agent initiating recursive audit...")
    mock_event = {"event_type": "METABOLIC_STABILITY_HIGH", "payload": {"weisman_score": 0.98}}
    
    # We loop a few times to ensure the random trigger (0.1 probability) hits
    decision = None
    for i in range(20):
        decision = architect.reason(mock_event)
        if decision['decision'] == "ARCHITECTURAL_OPTIMIZATION":
            print(f"✅ Success: Architect Agent triggered self-optimization at attempt {i+1}.")
            break
        await asyncio.sleep(0.1)
        
    if not decision or decision['decision'] != "ARCHITECTURAL_OPTIMIZATION":
        print("❌ Failure: Architect Agent failed to trigger optimization.")
        return

    # 2. Extract proposed optimization
    print(f"\n[STEP 2] Extracting Proposal...")
    analysis = decision['metadata'].get('analysis', {})
    target = analysis.get('root', 'CODEBASE')
    print(f"📦 Optimization Target: {target}")
    
    # 3. Sandbox Validation
    print(f"\n[STEP 3] Routing to Safety Sandbox...")
    # In the main loop, this is where code is tested
    proposal_id = "REF-RECURSIVE-SINGULARITY-01"
    is_safe = sandbox.validate_optimization(target, proposal_id)
    
    if is_safe:
        print(f"✨ [TRANSCENDENCE] Sandbox VALIDATED optimization for {target}.")
        print("🚀 Status: PROMOTED to Core Shadow Kernel.")
    else:
        print(f"⚠️ [TRANSCENDENCE] Sandbox REJECTED optimization. Integrity compromised.")

    # 4. History Check
    print("\n[STEP 4] Sandbox Validation History Audit")
    for entry in sandbox.validation_history:
        print(f" - {entry['module']}: {'PASSED' if entry['passed'] else 'FAILED'} (Coverage: {entry['coverage']:.2f})")

if __name__ == "__main__":
    asyncio.run(test_transcendence())
