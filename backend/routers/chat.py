from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from event_graph.graph_manager import GraphManager
from core.state import OrganismState
from human_interface.chat_engine import ChatEngine 

router = APIRouter()

state_manager = OrganismState()

chat_engine = None
try:
    # Initialize real production GraphManager
    graph_manager = GraphManager()
    chat_engine = ChatEngine(graph_manager, state_manager)
except Exception as e:
    print(f"⚠️ [CHAT_ROUTER] Degraded Mode: {e}")


@router.post("/")
async def chat_endpoint(data: dict):
    state_manager.load_state()
    async def event_generator():
        async for chunk in chat_engine.process_query_stream(data.get("query", "")):
            yield chunk
    return StreamingResponse(event_generator(), media_type="text/event-stream")
