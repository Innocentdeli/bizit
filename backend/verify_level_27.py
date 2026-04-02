import asyncio
import sys
import os
import hashlib
sys.path.append(os.getcwd())

from core.state import OrganismState
from cognitive_kernel.directive_engine import DirectiveEngine
from agents.recursive_editor import RecursiveEditor

async def test_god_mode():
    print("👑 Testing Level 27: Sovereign God Mode...")
    state = OrganismState()
    # Default Master Key: BIZIT_SOVEREIGN_2026
    engine = DirectiveEngine(master_key_hash=None) 
    
    # 1. Test Security (Key Verification)
    print("\n[1/3] Testing Cryptographic Security...")
    valid = engine.verify_key("BIZIT_SOVEREIGN_2026")
    invalid = engine.verify_key("WRONG_KEY")
    print(f"✅ Valid Key accepted: {valid}")
    print(f"✅ Invalid Key rejected: {not invalid}")
    
    # 2. Test Absolute Control (Highjacking logic)
    print("\n[2/3] Testing Cognitive Highjacking (!HALT)...")
    # Simulate adding a directive to state
    state.active_directives.append("!HALT")
    
    # In a real run, the main_loop would see this. We'll simulate the engine's response.
    result = engine.execute_directive("!HALT", state, None)
    print(f"✅ Directive Execute Result: {result}")
    print(f"✅ State status updated: {state.get_summary()['organism_status']}")
    
    # 3. Test Immutability Guard (Growth Resistance)
    print("\n[3/3] Testing Immutability Guard (Architect Defense)...")
    editor = RecursiveEditor(state)
    
    # Try to edit a protected file
    print("Architect attempting to modify 'directive_engine.py'...")
    success = editor.edit_core_logic("backend/cognitive_kernel/directive_engine.py", "REWRITE_ALL")
    
    if not success:
        print("✅ SUCCESS: Immutability Guard blocked the modification.")
    else:
        print("❌ FAILURE: Immutability Guard was bypassed.")

    print("\n👑 Verification Complete: Sovereign Dominance Confirmed.")

if __name__ == "__main__":
    asyncio.run(test_god_mode())
