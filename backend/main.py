from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

# Add backend directory to sys.path to ensure absolute imports work
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import Routers
from routers import search, chat, business, map_intel, admin, market_intel, reviews, analytics, recommendations, monetization, ranking, integrations, data_pipeline, ads, ai_kernel, ecosystem, autonomous_executive, organism, inquiries, appointments, social, auth, boardroom
from routers import brand, growth_loop, scale_mode, simulation, execution_hub
from routers import marketing_network, marketing_os
from organism.scheduler import start_organism, stop_organism



from database import models, database

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Bizit Pulse Platform API",
    description="Modular Business Intelligence Platform API (Refactored)",
    version="3.0.0"
)

@app.on_event("startup")
async def on_startup():
    """Awaken the Organism on server start."""
    import logging
    logging.basicConfig(level=logging.INFO)
    start_organism()

@app.on_event("shutdown")
async def on_shutdown():
    """Gracefully stop the Organism."""
    stop_organism()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router, prefix="/chat", tags=["Chat & Intelligence"])
app.include_router(search.router, prefix="/search", tags=["Search Engine"])
app.include_router(business.router, prefix="/business", tags=["Business Listings"])
app.include_router(map_intel.router, prefix="/map", tags=["Location Intelligence"])
app.include_router(market_intel.router, prefix="/market", tags=["Market Intelligence"])
app.include_router(reviews.router, prefix="/reviews", tags=["Reviews & Ratings"])
app.include_router(analytics.router, prefix="/analytics", tags=["Business Analytics"])
app.include_router(recommendations.router, prefix="/audit", tags=["Recommendation Engine"])
app.include_router(monetization.router, prefix="/billing", tags=["Monetization & Plans"])
app.include_router(ranking.router, prefix="/ranking", tags=["Ranking Engine"])
app.include_router(integrations.router, prefix="/api", tags=["Integrations"])
app.include_router(data_pipeline.router, prefix="/pipeline", tags=["Data Pipeline"])
app.include_router(ads.router, prefix="/ads", tags=["Advertising Engine"])
app.include_router(ai_kernel.router, prefix="/ai", tags=["AI Augmentation"])
app.include_router(ecosystem.router, prefix="/extensions", tags=["Ecosystem"])
app.include_router(autonomous_executive.router, prefix="/executive", tags=["Autonomous Orchestration"])
app.include_router(organism.router, prefix="/organism", tags=["🧬 Autonomous Organism"])
app.include_router(inquiries.router)
app.include_router(appointments.router)
app.include_router(social.router, prefix="/social", tags=["Social Media"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Platform Admin"])
app.include_router(boardroom.router, prefix="/boardroom", tags=["🏛️ Autonomous Boardroom"])

# ── Dima Dynamic Marketing OS — 5 Pillar Routers ──────────────────────────────
app.include_router(brand.router, prefix="/brand", tags=["🧬 Brand Intelligence"])
app.include_router(growth_loop.router, prefix="/growth-loop", tags=["⚡ Growth Loop Engine"])
app.include_router(scale_mode.router, prefix="/scale-mode", tags=["🎯 Adaptive Scale Mode"])
app.include_router(simulation.router, prefix="/simulation", tags=["📊 Monte Carlo Simulation"])
app.include_router(execution_hub.router, prefix="/execution-hub", tags=["🚀 Sovereign Execution Hub"])
app.include_router(marketing_network.router, prefix="/network", tags=["🌐 Global Marketing Network"])
app.include_router(marketing_os.router, prefix="/marketing-os", tags=["🧠 Autonomous Marketing OS"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "system": "Bizit Pulse Platform v2.0",
        "modules_active": [
            "Search & Discovery",
            "Location Intelligence",
            "Business Profiles",
            "Market Analysis",
            "Admin Control"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "mock_json"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
