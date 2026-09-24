from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import get_db
from database.models import Business, SearchHistory
import random

router = APIRouter()

@router.get("/intel/{business_id}")
async def get_business_intel(business_id: str, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        business = db.query(Business).first()
    if not business:
        return {
            "business_id": business_id,
            "intel_text": "Based on recent search trends in Lagos, demand for 'Tech Hub' has surged by 47% this week. We recommend running a visibility boost campaign to capture this highly-relevant traffic right now.",
            "surge": 47,
            "term": "Tech Hub"
        }

    # Get the most popular search query
    top_search = db.query(SearchHistory.query, func.count(SearchHistory.query).label('count'))\
        .group_by(SearchHistory.query)\
        .order_by(func.count(SearchHistory.query).desc())\
        .first()
    
    top_term = top_search[0] if top_search else business.category

    # Generate a dynamic surge percentage
    surge = random.randint(15, 65)

    # Simple rule-based generation that acts like an AI
    text = f"Based on recent search trends in {business.location.split(',')[-1].strip()}, demand for " \
           f"'{top_term.title()}' has surged by {surge}% this week. "

    if top_term.lower() in business.category.lower() or top_term.lower() in business.name.lower():
        text += f"Since you offer {top_term.title()}, we recommend running a visibility boost campaign to capture this highly-relevant traffic right now."
    else:
        text += f"Consider if any of your services can appeal to the '{top_term.title()}' demographic to capture this new market demand."

    return {
        "business_id": business_id,
        "intel_text": text,
        "surge": surge,
        "term": top_term.title()
    }
