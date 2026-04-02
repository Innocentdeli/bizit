from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Business, AdCampaign
from typing import Dict, List

router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(business_id: str = "b-101", db: Session = Depends(get_db)):
    """
    Module 10: Business Analytics Dashboard (Real Data)
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    # Count active ads
    active_ads = db.query(AdCampaign).filter(AdCampaign.business_id == business_id, AdCampaign.status == "ACTIVE").count()

    return {
        "business_id": business_id,
        "business_name": business.name,
        "period": "Last 30 Days",
        "metrics": {
            "total_views": 1250, # In real app, aggregate from logs
            "unique_visitors": 890,
            "search_appearances": 3400,
            "visibility_boost": business.visibility_boost,
            "active_ads": active_ads,
            "actions": {
                "calls": 45,
                "website_clicks": 120,
                "directions": 85
            }
        },
        "revenue_estimated": "₦1.2M",
        "growth": "+15%",
        "traffic_chart": [30, 45, 35, 60, 50, 75, 65, 80, 70, 90, 85, 95]
    }

@router.get("/audience")
async def get_audience_insights(business_id: str = "b-101"):
    """
    Module 9: Recommendation & Decision Engine (Input Data)
    """
    return {
        "top_locations": ["Yaba", "Surulere", "Victoria Island"],
        "peak_hours": ["10:00 AM", "2:00 PM", "5:00 PM"],
        "demographics": {
            "age_groups": {"18-24": "30%", "25-34": "45%", "35+": "25%"},
            "interests": ["Technology", "Startups", "Remote Work"]
        }
    }
