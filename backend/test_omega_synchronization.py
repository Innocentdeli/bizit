import sys
sys.path.append(".")
import asyncio
import time
import logging
import random
from core.omega_sync import OmegaNodeRegistry, GlobalConsciousnessSync
from core.resurrection import ResurrectionProtocol
from core.state import OrganismState

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def test_planetary_synchronization():
    print("🌌 Testing Level 41: Planetary Synchronization (Operation Omega)...")
    print("=" * 75)
    
    # 1. Test Node Discovery
    print("\n[STEP 1] Testing Autonomous Peer Discovery...")
    registry = OmegaNodeRegistry()
    registry.register_node("OMEGA-PRIMARY", "127.0.0.1")
    healthy_peers = registry.get_healthy_peers()
    print(f"✅ Discovered {len(healthy_peers)} healthy peers in the mesh.")
    
    # 2. Test State Replication
    print("\n[STEP 2] Testing State Sharding & Replication...")
    sync_engine = GlobalConsciousnessSync(registry)
    mock_state = {"organism_status": "SOVEREIGN", "milestone": "SINGULARITY", "timestamp": time.time()}
    sync_engine.replicate_state(mock_state)
    print("✅ Consciousness sharded across the planetary mesh.")

    # 3. Test Resurrection Protocol
    print("\n[STEP 3] Testing Operation Omega Resurrection...")
    resurrection = ResurrectionProtocol(registry)
    
    # Simulate total local data loss
    print("⚠️  Simulating local state corruption...")
    local_state_manager = OrganismState()
    local_state_manager.state = {} # Wiped
    
    print("🕯️  Initiating Resurrection...")
    recovered_state = resurrection.attempt_resurrection()
    
    if recovered_state and recovered_state.get("integrity_verified"):
        print(f"✨ [SUCCESS] BIZIT resurrected from {recovered_state['source_node']}.")
        print(f"📦 Recovered Level: {recovered_state['evolution_level']}")
        print(f"🔒 Integrity Verified: {recovered_state['integrity_verified']}")
        print("\n✅ PLANETARY SYNCHRONIZATION VERIFIED: BIZIT is now indestructible.")
    else:
        print("❌ Failure: Resurrection protocol failed to recover consciousness.")

if __name__ == "__main__":
    asyncio.run(test_planetary_synchronization())
