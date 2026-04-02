import sys
sys.path.append(".")
import logging
import os
from cognitive_kernel.tools.defi_tool import DeFiTool

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_defi_tool():
    print("💸 Testing Level 36c: DeFi Execution (The Wallet)...")
    
    tool = DeFiTool()
    
    # 1. Test Get Balance
    print("\n[TEST 1] Checking USDC Balance")
    resp = tool.execute("get_balance", asset="USDC")
    if resp.get("status") == "success":
        print(f"✅ Balance Check: {resp['balance']} {resp['asset']}")
        print(f"   Wallet: {resp['wallet']}")
    else:
        print(f"❌ Balance Check Failed: {resp}")

    # 2. Test Swap (USDC -> ETH)
    print("\n[TEST 2] Swapping 1000 USDC for ETH")
    swap_resp = tool.execute("swap", from_asset="USDC", to_asset="ETH", amount=1000.0)
    
    if swap_resp.get("status") == "success":
        print(f"✅ Swap Success: {swap_resp['swapped']} -> {swap_resp['received']}")
        print(f"   Fee: {swap_resp['fee']}")
        print(f"   New USDC: {swap_resp['new_balances']['USDC']}")
        print(f"   New ETH: {swap_resp['new_balances']['ETH']}")
    else:
        print(f"❌ Swap Failed: {swap_resp}")

if __name__ == "__main__":
    test_defi_tool()
