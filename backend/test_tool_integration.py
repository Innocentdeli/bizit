import sys
sys.path.append(".")
import logging
from backend.agents.finance_agent import FinanceAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_tool_capabilities():
    print("🧠 Testing Omni-Intelligence Tool Capabilities...")
    
    # 1. Instantiate Agent
    finance_bot = FinanceAgent("FinanceBot-Test")
    print(f"✅ Agent Initialized: {finance_bot.name}")
    
    # 2. Test Tool Registry
    tools = [t.name for t in finance_bot.tools]
    print(f"🛠️  Available Tools: {tools}")
    
    if "web_search" not in tools or "file_ops" not in tools:
        print("❌ Error: Tools not correctly registered.")
        return

    # 3. Test Web Search (Mock)
    print("\n[TEST 1] Web Search Execution")
    search_result = finance_bot.use_tool("web_search", query="BTC price prediction 2026")
    if search_result.get("status") == "success":
        print(f"✅ Search Success: Found {len(search_result['results'])} results.")
    else:
        print(f"❌ Search Failed: {search_result}")

    # 4. Test File Write (Safe)
    print("\n[TEST 2] File Write Execution")
    test_file = "test_tool_output.txt"
    write_result = finance_bot.use_tool("file_ops", operation="write", file_path=test_file, content="Sovereign Data Log: Test")
    if write_result.get("status") == "success":
        print(f"✅ Write Success: {write_result['message']}")
    else:
        print(f"❌ Write Failed: {write_result}")

    # 5. Test File Read
    print("\n[TEST 3] File Read Execution")
    read_result = finance_bot.use_tool("file_ops", operation="read", file_path=test_file)
    if read_result.get("status") == "success" and "Sovereign" in read_result["content"]:
        print(f"✅ Read Success: {read_result['content']}")
    else:
        print(f"❌ Read Failed: {read_result}")
        
    # 6. Test Security Guard (Protected File)
    print("\n[TEST 4] Sovereign Guard Check")
    security_result = finance_bot.use_tool("file_ops", operation="write", file_path="main_loop.py", content="HACKED")
    if security_result.get("status") == "error" and "ACCESS DENIED" in security_result["message"]:
        print(f"✅ Security Success: Transformation Blocked ({security_result['message']})")
    else:
        print(f"❌ Security Failed: Tool allowed protected file access! Result: {security_result}")

    # Cleanup
    import os
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    test_tool_capabilities()
