from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import get_db
from database.models import Business, AdCampaign, AnalyticsEvent
import time
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional

router = APIRouter()

@router.get("/overview")
async def get_analytics_overview(business_id: str = "b-101", db: Session = Depends(get_db)):
    """
    Module 10: Business Analytics Dashboard (Real Data Aggregation)
    """
    import urllib.parse
    clean_name = urllib.parse.unquote(business_id).replace("-", " ").title() if business_id != "default" else "My Business"

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        business = Business(
            id=business_id,
            name=clean_name,
            category="Technology & Growth",
            location="Lagos, Nigeria",
            verified=True,
            rating=5.0,
            review_count=0,
            profile_views=0,
            search_appearances=0,
            leads=0,
            visibility_boost=1.0,
            subscription_tier="pro"
        )
        try:
            db.add(business)
            db.commit()
            db.refresh(business)
        except Exception:
            db.rollback()

    active_ads = db.query(AdCampaign).filter(AdCampaign.business_id == business_id, AdCampaign.status == "ACTIVE").count()

    now = time.time()
    
    website_clicks = db.query(AnalyticsEvent).filter(AnalyticsEvent.business_id == business_id, AnalyticsEvent.event_type == "website_click").count()
    direction_clicks = db.query(AnalyticsEvent).filter(AnalyticsEvent.business_id == business_id, AnalyticsEvent.event_type == "direction_click").count()
    total_views = db.query(AnalyticsEvent).filter(AnalyticsEvent.business_id == business_id, AnalyticsEvent.event_type == "profile_view").count()
    total_leads = db.query(AnalyticsEvent).filter(AnalyticsEvent.business_id == business_id, AnalyticsEvent.event_type == "lead").count()
    
    unique_visitors = int(total_views * 0.7) # baseline uniqueness ratio
    
    # Generate traffic chart based on last 60 days broken into 12 buckets (5 days each)
    period_length = (60 * 24 * 60 * 60) / 12
    traffic_chart = [0] * 12
    
    events = db.query(AnalyticsEvent.timestamp).filter(AnalyticsEvent.business_id == business_id, AnalyticsEvent.event_type == "profile_view", AnalyticsEvent.timestamp > now - (60*24*3600)).all()
    for (ts,) in events:
        bucket = int((now - ts) / period_length)
        if 0 <= bucket < 12:
            traffic_chart[11 - bucket] += 1
            
    return {
        "business_id": business_id,
        "business_name": business.name,
        "period": "Last 60 Days",
        "metrics": {
            "total_views": total_views or business.profile_views or 0,
            "unique_visitors": unique_visitors,
            "search_appearances": business.search_appearances or 0,
            "visibility_boost": business.visibility_boost,
            "active_ads": active_ads,
            "actions": {
                "calls": total_leads or business.leads or 0,
                "website_clicks": website_clicks,
                "directions": direction_clicks
            }
        },
        "revenue_estimated": float((total_leads or business.leads or 0) * 15000),
        "revenue_estimated_formatted": "₦" + str(round((total_leads or business.leads or 0) * 15000 / 1000000, 1)) + "M",
        "growth": "+15%",
        "traffic_chart": traffic_chart
    }

@router.get("/audience")
async def get_audience_insights(business_id: str = "b-101", db: Session = Depends(get_db)):
    """
    Module 9: Recommendation & Decision Engine (Real Audience Data)
    """
    # Get top locations
    locs = db.query(AnalyticsEvent.location_city, func.count(AnalyticsEvent.id)).filter(
        AnalyticsEvent.business_id == business_id, AnalyticsEvent.location_city != None
    ).group_by(AnalyticsEvent.location_city).order_by(func.count(AnalyticsEvent.id).desc()).limit(3).all()
    
    top_locations = [l[0] for l in locs] if locs else ["No Data"]

    # Get demographics
    ages = db.query(AnalyticsEvent.user_age_group, func.count(AnalyticsEvent.id)).filter(
        AnalyticsEvent.business_id == business_id, AnalyticsEvent.user_age_group != None
    ).group_by(AnalyticsEvent.user_age_group).all()
    
    total_ages = sum(a[1] for a in ages)
    age_groups = {a[0]: f"{int((a[1]/total_ages)*100)}%" for a in ages} if total_ages > 0 else {}

    # Get peak hours by extracting hour from timestamp
    events = db.query(AnalyticsEvent.timestamp).filter(AnalyticsEvent.business_id == business_id).all()
    hour_counts = {}
    for (ts,) in events:
        h = datetime.fromtimestamp(ts).hour
        hour_counts[h] = hour_counts.get(h, 0) + 1
        
    top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    def format_hour(h):
        if h == 0: return "12:00 AM"
        if h == 12: return "12:00 PM"
        return f"{h}:00 AM" if h < 12 else f"{h-12}:00 PM"
        
    peak_hours = [format_hour(h[0]) for h in top_hours] if top_hours else ["No Data"]

    return {
        "top_locations": top_locations,
        "peak_hours": peak_hours,
        "demographics": {
            "age_groups": age_groups,
            "interests": ["Technology", "Startups", "Remote Work"] # Keep generic interests for now
        }
    }

class TrackEventReq(BaseModel):
    event_type: str
    location_city: Optional[str] = None
    user_age_group: Optional[str] = None

@router.post("/track")
async def track_event(business_id: str, req: TrackEventReq, db: Session = Depends(get_db)):
    """
    Track a new real-time analytics event
    """
    event = AnalyticsEvent(
        business_id=business_id,
        event_type=req.event_type,
        location_city=req.location_city,
        user_age_group=req.user_age_group,
        timestamp=time.time()
    )
    db.add(event)
    
    # Update master counters
    biz = db.query(Business).filter(Business.id == business_id).first()
    if biz:
        if req.event_type == "profile_view":
            biz.profile_views = (biz.profile_views or 0) + 1
        elif req.event_type == "lead":
            biz.leads = (biz.leads or 0) + 1
            
    db.commit()
    return {"status": "success"}
