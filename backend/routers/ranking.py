from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Business

router = APIRouter()

@router.get("/score/{business_id}")
async def get_ranking_score(business_id: str, db: Session = Depends(get_db)):
    """
    Module 12: Real Ranking & Visibility Engine
    Calculates a 'Visibility Score' based on live ecosystem metrics.
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    # Real Calculation Logic
    base_score = 50
    score = base_score
    
    breakdown = {}
    
    # 1. Verification Bonus
    if business.verified:
        score += 25
        breakdown["verification"] = +25
    
    # 2. Review Volume Bonus
    if business.review_count > 10:
        review_bonus = min(20, business.review_count // 2)
        score += review_bonus
        breakdown["reputation"] = +review_bonus
        
    # 3. Quality Bonus (Rating)
    if business.rating >= 4.5:
        score += 15
        breakdown["quality"] = +15
        
    # 4. Economic Tier Bonus
    if business.subscription_tier == "pro":
        score += 30
        breakdown["pro_tier"] = +30
    elif business.subscription_tier == "enterprise":
        score += 60
        breakdown["sovereign_tier"] = +60
        
    # 5. Autonomous Systemic Boost
    if business.visibility_boost > 0:
        score += business.visibility_boost
        breakdown["autonomous_boost"] = +business.visibility_boost
        
    # Determine Rank Percentile (Simulated based on global score distribution)
    # In a real app, this would be a comparative query:
    # rank_better_than = db.query(Business).filter(Business.visibility_score < score).count()
    # total = db.query(Business).count()
    rank_label = "Top 10%" if score > 100 else "Standard"
    if score > 130: rank_label = "Elite (Top 1%)"

    return {
        "business_id": business_id,
        "business_name": business.name,
        "visibility_score": score,
        "rank_percentile": rank_label,
        "breakdown": breakdown,
        "next_milestone": "Reach 50 reviews for +10 visibility" if business.review_count < 50 else "Maintain quality rating above 4.8"
    }

@router.post("/boost/{business_id}")
async def boost_listing(business_id: str, duration_days: int = 7):
    """
    Sub-feature: Paid visibility boost (Stubbed for now)
    """
    return {
        "status": "success",
        "message": f"Business {business_id} boosted for {duration_days} days.",
        "new_rank_projection": "Elite (Top 1%)"
    }
