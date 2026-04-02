from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import uuid
from sqlalchemy.orm import Session
from database import models, database

router = APIRouter()

# --- Data Models ---
class BusinessProfile(BaseModel):
    id: str
    name: str
    category: str
    location: str
    rating: float
    verified: bool
    subscription_tier: str = "free"
    # Add other fields as optional for list view, or separate model for details

# --- Mock Database ---
# KEEPING MOCK_BUSINESSES FOR SEEDING REFERENCE ONLY.
# REFACTOR: The seed script imports this. 
MOCK_BUSINESSES = [
    {
        "id": "b-101",
        "name": "Lagos Tech Hub",
        "category": "Technology & Innovation",
        "location": "15 Montgomery Road, Yaba, Lagos",
        "rating": 4.8,
        "review_count": 124,
        "verified": True,
        "description": "The premier destination for startups and tech innovators in West Africa. High-speed internet, dedicated desks, and incubation support.",
        "hours": "Open • Closes 10PM",
        "phone": "+234 800 BIZIT",
        "website": "www.lagostechhub.com",
        "services": ["High-Speed WiFi", "Meeting Rooms", "24/7 Power", "Coffee Bar", "Event Space"]
    },
    {
        "id": "b-102",
        "name": "Mama Cassie's Catering",
        "category": "Food & Beverage",
        "location": "Ikeja, Lagos",
        "rating": 4.5,
        "review_count": 89,
        "verified": True,
        "description": "Authentic local dishes for corporate events.",
        "hours": "Open • Closes 8PM",
        "phone": "+234 800 FOOD",
        "website": "www.mamacassie.com",
        "services": ["Catering", "Delivery", "Event Hosting"]
    },
    {
        "id": "b-103",
        "name": "Blue Chip Logistics",
        "category": "Logistics",
        "location": "Apapa, Lagos",
        "rating": 3.9,
        "review_count": 42,
        "verified": False,
        "description": "Global shipping and freight forwarding.",
        "hours": "Closes 5PM",
        "phone": "+234 800 MAIL",
        "website": "www.bluechip.com",
        "services": ["Freight", "Shipping", "Warehousing"]
    }
]

@router.get("/{business_id}")
async def get_business(business_id: str, db: Session = Depends(database.get_db)):
    """
    Module 3: Business Profile Retrieval (DB Connected)
    """
    business = db.query(models.Business).filter(models.Business.id == business_id).first()
    if not business:
         raise HTTPException(status_code=404, detail="Business not found")
    return {"status": "success", "data": business}

@router.get("/")
async def list_businesses(category: Optional[str] = None, db: Session = Depends(database.get_db)):
    """
    Module 3: Directory Listing (DB Connected)
    """
    query = db.query(models.Business)
    if category:
        # Simple case-insensitive exact match for now
        # In real app, use ILIKE
        all_businesses = query.all()
        filtered = [b for b in all_businesses if b.category.lower() == category.lower()]
        return {"status": "success", "count": len(filtered), "data": filtered}
    
    businesses = query.all()
    return {"status": "success", "count": len(businesses), "data": businesses}

@router.post("/")
async def create_business_claim(data: dict):
    """
    Module 4: Business Claiming & Registration
    """
    new_id = f"b-{uuid.uuid4().hex[:6]}"
    # In real app, save to DB
    return {"status": "success", "message": "Business claim submitted", "id": new_id}
