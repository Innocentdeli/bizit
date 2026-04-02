"""
Level 51: Test Autonomous Alpha Execution

This script simulates a Tri-Confluence signal and verifies that BIZIT
autonomously executes the trade via the Executor.
"""

import asyncio
from core.state import OrganismState
from actuation_layer.executor import Executor

async def test_alpha_execution():
    print("🧪 [TEST] Level 51: Autonomous Alpha Execution")
    print("=" * 60)
    
    # 1. Initialize State and Executor
    state_manager = OrganismState()
    executor = Executor()
    
    # 2. Verify Auto-Execution is Enabled
    is_auto = state_manager.is_automated("EXECUTE_PATERNAL_ALPHA")
    print(f"\n✓ Auto-Execution Enabled: {is_auto}")
    
    if not is_auto:
        print("❌ [TEST] FAILED: Auto-execution not enabled for EXECUTE_PATERNAL_ALPHA")
        return
    
    # 3. Simulate Alpha Signal
    print("\n📡 [TEST] Simulating Tri-Confluence Alpha Signal...")
    
    alpha_action = {
        "agent": "FinanceBot-1",
        "decision": "EXECUTE_PATERNAL_ALPHA",
        "target_system": "FOREX",
        "metadata": {
            "symbol": "GBPUSD",
            "side": "BUY",
            "risk_pct": 0.005,
            "entry_zone": [1.3500, 1.3520]
        }
    }
    
    # 4. Execute (Should auto-execute without approval)
    print("\n⚡ [TEST] Executing Alpha Trade...")
    result = await executor.execute_action(alpha_action, proof="TEST_ALPHA_001")
    
    # 5. Verify Result
    print(f"\n📊 [TEST] Execution Result:")
    print(f"   Status: {result.get('status')}")
    print(f"   System: {result.get('system')}")
    print(f"   Details: {result.get('details')}")
    print(f"   Trade ID: {result.get('trade_id')}")
    
    if result.get("status") == "SUCCESS":
        print("\n✅ [TEST] SUCCESS: Alpha trade executed autonomously!")
        
        # 6. Verify Active Trades Registry
        if result.get("trade_id") in executor.active_trades:
            trade_info = executor.active_trades[result.get("trade_id")]
            print(f"\n📝 [TEST] Active Trade Registered:")
            print(f"   Symbol: {trade_info['symbol']}")
            print(f"   Entry Price: {trade_info['entry_price']}")
            print(f"   SL Price: {trade_info['sl_price']}")
            print(f"   Zone: {trade_info['zone']}")
        else:
            print("\n⚠ [TEST] WARNING: Trade not found in active_trades registry")
    else:
        print(f"\n❌ [TEST] FAILED: {result.get('error')}")
    
    # 7. Test Position Monitor
    print("\n🔍 [TEST] Testing Position Monitor...")
    await executor.monitor_active_trades()
    print("✓ Position monitor executed successfully")
    
    print("\n" + "=" * 60)
    print("🏆 [TEST] Level 51 Verification Complete")

if __name__ == "__main__":
    asyncio.run(test_alpha_execution())
