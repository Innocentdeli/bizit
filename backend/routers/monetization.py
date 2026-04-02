from fastapi import APIRouter, HTTPException, Depends

from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Business
import uuid

router = APIRouter()

class Plan(BaseModel):
    id: str
    name: str
    price: str
    features: list

PLANS = [
    {
        "id": "free",
        "name": "Starter",
        "price": "Free",
        "features": ["Basic Profile", "Listing in Directory", "Receive Reviews"]
    },
    {
        "id": "pro",
        "name": "Professional",
        "price": "₦15,000/mo",
        "features": ["Verified Badge", "Analytics Dashboard", "Priority Support", "3 Gap Alerts/mo"]
    },
    {
        "id": "enterprise",
        "name": "Sovereign",
        "price": "₦50,000/mo",
        "features": ["All Pro Features", "Unlimited Market Intel", "API Access", "Dedicated Account Manager"]
    }
]

@router.get("/plans")
async def get_plans():
    """
    Module 13: Subscription Plans
    """
    return {"status": "success", "plans": PLANS}

@router.post("/subscribe/{plan_id}")
async def subscribe(plan_id: str, business_id: str, db: Session = Depends(get_db)):
    """
    Module 13: Real Subscription Logic
    Updates the business tier in the ecosystem.
    """
    plan = next((p for p in PLANS if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
         raise HTTPException(status_code=404, detail="Business not found")

    # Update the business tier
    business.subscription_tier = plan_id
    db.commit()
    
    return {
        "status": "success",
        "message": f"Successfully upgraded {business.name} to {plan['name']} tier.",
        "transaction_id": f"tx_{uuid.uuid4().hex[:10]}"
    }
