import asyncio
import sys
sys.path.append(".")
from human_interface.chat_engine import ChatEngine
from core.state import OrganismState

# Mock dependencies
class MockGraphManager:
    def __init__(self): pass

async def test_sovereign_actuation():
    print("🧠 Testing Level 35b: Sovereign Actuation (Chat -> Action)...")
    
    # Setup
    state = OrganismState()
    engine = ChatEngine(MockGraphManager(), state)
    
    # Test Cases
    test_queries = [
        "Research quantum computing market trends",
        "Create report status_log.txt with content 'System Nominal'",
        "Hello, how are you?" # Should NOT trigger tools
    ]
    
    for query in test_queries:
        print(f"\n💬 Query: '{query}'")
        print("Response Stream:")
        print("-" * 40)
        
        tool_triggered = False
        async for chunk in engine.handle_message_async({"query": query}):
            print(chunk, end="", flush=True)
            if "Sovereign Actuation Initiated" in chunk:
                tool_triggered = True
                
        print("\n" + "-" * 40)
        
        if "Research" in query or "Create report" in query:
            if tool_triggered:
                print("✅ PASS: Tool Execution Triggered")
            else:
                print("❌ FAIL: Tool Execution NOT Triggered")
        else:
            if not tool_triggered:
                print("✅ PASS: Standard Chat Response (Correct)")
            else:
                print("❌ FAIL: False Positive Trigger")

if __name__ == "__main__":
    asyncio.run(test_sovereign_actuation())
