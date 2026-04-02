import sys
sys.path.append(".")
import time
import logging
from evolution.mitosis_engine import MitosisEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_mitosis_cycle():
    print("🧬 Testing Level 37: Mitosis (Self-Replication)...")
    print("=" * 50)
    
    engine = MitosisEngine()
    
    # 1. Trigger Mitosis
    print("\n[STEP 1] Spawning Daughter Cell (Researcher role)")
    task = {
        "target": "NVIDIA Stock Analysis",
        "description": "Provide a 1-sentence bull case for NVIDIA in 2026."
    }
    cell_id = engine.spawn_cell(role="Researcher", task_context=task)
    print(f"🐣 Cell Created: {cell_id}")
    
    # 2. Monitor Gestation/Activity
    print("\n[STEP 2] Monitoring Colony Status...")
    for _ in range(15):
        stats = engine.monitor_colony()
        print(f"   Colony Size: {stats['colony_size']} | Active: {[c['id'] for c in stats['active_cells']]}")
        if stats['colony_size'] == 0 and len(stats['recent_results']) > 0:
            break
        time.sleep(1)
        
    # 3. Verify Results
    print("\n[STEP 3] Verifying Result Transmission")
    stats = engine.monitor_colony()
    if len(stats['recent_results']) > 0:
        res = stats['recent_results'][0]
        print(f"🔍 Debug: Raw Result Object: {res}")
        if res.get("status") == "SUCCESS":
            print(f"✅ SUCCESS: Result received from {res['cell_id']}")
            print(f"📊 Content: {res['result'][:100]}...")
        else:
            print(f"❌ Daughter Cell reported FAILURE: {res.get('error')}")
    else:
        print("❌ FAIL: No results received within timeframe (Check Ollama connection?)")

if __name__ == "__main__":
    test_mitosis_cycle()
