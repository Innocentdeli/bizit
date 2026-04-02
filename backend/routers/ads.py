from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from database.database import get_db
from database.models import AdCampaign
import uuid

router = APIRouter()

@router.post("/campaigns/create")
async def create_campaign(business_id: str, title: str, budget: float, db: Session = Depends(get_db)):
    """
    Module 14: Advertising & Promotion Engine
    Persists a new campaign into the database.
    """
    new_campaign = AdCampaign(
        id=f"cmp_{uuid.uuid4().hex[:8]}",
        business_id=business_id,
        title=title,
        budget=budget,
        status="ACTIVE",
        impressions=0,
        clicks=0
    )
    db.add(new_campaign)
    db.commit()
    return {
        "status": "success",
        "campaign": {
            "id": new_campaign.id,
            "title": new_campaign.title,
            "budget": f"₦{new_campaign.budget:,.2f}",
            "status": new_campaign.status
        }
    }

@router.get("/campaigns/{business_id}")
async def get_campaigns(business_id: str, db: Session = Depends(get_db)):
    """
    Module 14: List real campaigns from the DB
    """
    campaigns = db.query(AdCampaign).filter(AdCampaign.business_id == business_id).all()
    return {
        "status": "success",
        "count": len(campaigns),
        "campaigns": campaigns
    }
