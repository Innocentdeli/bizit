from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.events import BizEvent
from typing import List

app = FastAPI(title="BIZIT Cognitive Kernel API")

# Mock storage for events
events_db = []

@app.post("/events", status_code=201)
async def receive_event(event: BizEvent):
    # In a real scenario, this would publish to RabbitMQ/Kafka
    # For now, we store in memory and log
    event.id = f"evt_{len(events_db) + 1}"
    events_db.append(event)
    print(f"Received Event: {event.event_type} from {event.source}")
    return {"status": "received", "event_id": event.id}

@app.get("/events", response_model=List[BizEvent])
async def get_events():
    return events_db

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "BIZIT API",
        "status": "operational",
        "version": "0.1.0",
        "layers": ["Sensory", "Cognitive", "Trust", "Agent", "Learning"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
