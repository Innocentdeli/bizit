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
from routers import search, chat, business, map_intel, admin, market_intel, reviews, analytics, recommendations, monetization, ranking, integrations, data_pipeline, ads, ai_kernel, ecosystem, autonomous_executive



from database import models, database

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Bizit Pulse Platform API",
    description="Modular Business Intelligence Platform API (Refactored)",
    version="2.1.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(admin.router, prefix="/admin", tags=["Platform Admin"])


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
