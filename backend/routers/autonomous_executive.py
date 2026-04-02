from fastapi import APIRouter, Depends, BackgroundTasks

from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import get_db
from database.models import SearchHistory, Business, AdCampaign
from cognitive_kernel.gemini_client import GeminiClient
import time
import uuid

router = APIRouter()
gemini = GeminiClient(model_name="gemini-1.5-flash")

@router.post("/process-market-signals")
async def process_market_signals(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Module 20: Autonomous Executive Signal Processing
    Analyzes demand vs supply and executes autonomous 'Systemic Boosts'.
    """
    # 1. SCAN: Find top 3 high-demand areas with low supply (Gaps)
    seven_days_ago = time.time() - (7 * 86400)
    
    top_demands = db.query(
        SearchHistory.query, 
        func.count(SearchHistory.id).label('total')
    ).filter(SearchHistory.timestamp > seven_days_ago)\
     .group_by(SearchHistory.query)\
     .order_by(func.count(SearchHistory.id).desc())\
     .limit(5).all()

    actions_taken = []

    for demand in top_demands:
        query_text = demand.query.lower()
        demand_count = demand.total
        
        supply_count = db.query(Business).filter(
            (Business.category.ilike(f"%{query_text}%")) | 
            (Business.name.ilike(f"%{query_text}%"))
        ).count()
        
        if demand_count > supply_count:
            candidates = db.query(Business).filter(
                (Business.category.ilike(f"%{query_text}%")) | 
                (Business.name.ilike(f"%{query_text}%"))
            ).order_by(Business.rating.desc()).limit(1).all()
            
            for biz in candidates:
                biz.visibility_boost += 50.0
                new_campaign = AdCampaign(
                    id=f"cmp_auto_{uuid.uuid4().hex[:6]}",
                    business_id=biz.id,
                    title=f"AUTO: {query_text.title()} Gap Capture",
                    status="ACTIVE",
                    budget=500.0,
                    impressions=0,
                    clicks=0
                )
                db.add(new_campaign)
                actions_taken.append({
                    "target": biz.name,
                    "reason": f"High Demand ({demand_count}) vs Low Supply ({supply_count}) for '{query_text}'",
                    "action": "SYSTEMIC_VISIBILITY_BOOST + SUBSIDIZED_ADS"
                })

    db.commit()
    return {
        "status": "success",
        "timestamp": time.time(),
        "actions": actions_taken
    }
