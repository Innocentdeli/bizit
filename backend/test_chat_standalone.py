import asyncio
import sys
sys.path.append(".")

from core.state import OrganismState
from human_interface.chat_engine import ChatEngine

class MockGraphManager:
    def __init__(self): pass

async def test_chat():
    print("🧠 Testing ChatEngine Streaming...")
    state = OrganismState()
    engine = ChatEngine(MockGraphManager(), state)
    
    query = "Hello, what is your purpose?"
    print(f"Query: {query}\n")
    print("Response: ", end="", flush=True)
    
    try:
        async for chunk in engine.process_query_stream(query):
            print(chunk, end="", flush=True)
        print("\n\n✅ Chat streaming works!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat())
