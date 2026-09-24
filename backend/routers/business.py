from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import uuid
import math
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
async def get_business(business_id: str, track: bool = True, db: Session = Depends(database.get_db)):
    """
    Module 3: Business Profile Retrieval (DB Connected)
    Use track=false for internal dashboard calls to avoid inflating view counts.
    """
    business = db.query(models.Business).filter(models.Business.id == business_id).first()
    if not business:
         raise HTTPException(status_code=404, detail="Business not found")
         
    # Only log a view event for genuine external/public profile fetches
    if track:
        import time
        from database.models import AnalyticsEvent
        
        event = AnalyticsEvent(
            business_id=business_id,
            event_type="profile_view",
            location_city="Lagos",
            timestamp=time.time()
        )
        db.add(event)
        
        business.profile_views = (business.profile_views or 0) + 1
        db.commit()
    
    db.refresh(business)
    return {"status": "success", "data": business}

@router.get("/")
async def list_businesses(
    category: Optional[str] = None, 
    q: Optional[str] = None, 
    sort: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    email: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """
    Module 3: Directory Listing (DB Connected) with Dynamic Search & Sorting
    """
    query = db.query(models.Business)
    
    if email:
        query = query.filter(models.Business.contact_email == email)
    
    if q:
        # Log the search
        import time
        from database.models import SearchHistory
        new_history = SearchHistory(
            user_id="anonymous",
            query=q.lower().strip(),
            timestamp=time.time()
        )
        db.add(new_history)
        db.commit()

        # Update search_appearances for matched businesses
        matched = query.filter((models.Business.name.ilike(f"%{q}%")) | (models.Business.category.ilike(f"%{q}%"))).all()
        for b in matched:
            b.search_appearances = (b.search_appearances or 0) + 1
        db.commit()
        
        query = query.filter((models.Business.name.ilike(f"%{q}%")) | (models.Business.category.ilike(f"%{q}%")))

    if category and category != "all":
        query = query.filter(models.Business.category.ilike(f"%{category}%"))
        
    # Sort by rating if requested
    if sort == "rating":
        query = query.order_by(models.Business.rating.desc())
        
    businesses = query.all()
    
    # Sort by distance if requested and user coordinates provided
    if sort == "distance" and lat is not None and lng is not None:
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0 # Earth radius in kilometers
            dLat = math.radians(lat2 - lat1)
            dLon = math.radians(lon2 - lon1)
            lat1 = math.radians(lat1)
            lat2 = math.radians(lat2)
            a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c
            
        def sort_key(b):
            # If business has no coordinates, put it at the end (large distance)
            if b.latitude is None or b.longitude is None:
                return float('inf')
            return haversine(lat, lng, b.latitude, b.longitude)
            
        businesses.sort(key=sort_key)
        
        # Optionally attach distance to the objects for frontend display
        for b in businesses:
            if b.latitude is not None and b.longitude is not None:
                b.distance_km = round(haversine(lat, lng, b.latitude, b.longitude), 1)
            else:
                b.distance_km = None

    return {"status": "success", "count": len(businesses), "data": businesses}

@router.post("/")
async def create_business(data: dict, db: Session = Depends(database.get_db)):
    """
    Create a new business from the onboarding wizard.
    Saves the business to the database and returns the new business ID.
    """
    new_id = f"b-{uuid.uuid4().hex[:6]}"
    new_biz = models.Business(
        id=new_id,
        name=data.get("name", ""),
        category=data.get("category", ""),
        location=data.get("location", ""),
        phone=data.get("phone", ""),
        description=data.get("description", ""),
        website=data.get("website", ""),
        hours=data.get("hours", ""),
        subscription_tier=data.get("subscription_tier", "free"),
        claimed=True,
        verified=False,
        rating=0.0,
        review_count=0,
        profile_views=0,
        search_appearances=0,
        leads=0,
        contact_email=data.get("contact_email"),
    )
    db.add(new_biz)
    db.commit()
    db.refresh(new_biz)
    return {"status": "success", "message": f"Welcome to BIZIT, {new_biz.name}!", "id": new_biz.id}

@router.put("/{business_id}")
async def update_business(business_id: str, data: dict, db: Session = Depends(database.get_db)):
    """
    Update an existing business.
    """
    biz = db.query(models.Business).filter(models.Business.id == business_id).first()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
        
    # Update fields if provided
    if "name" in data: biz.name = data["name"]
    if "category" in data: biz.category = data["category"]
    if "location" in data: biz.location = data["location"]
    if "phone" in data: biz.phone = data["phone"]
    if "website" in data: biz.website = data["website"]
    if "hours" in data: biz.hours = data["hours"]
    if "description" in data: biz.description = data["description"]
    
    db.commit()
    db.refresh(biz)
    
    return {"status": "success", "message": "Business updated", "data": biz}

@router.patch("/{business_id}/ai-toggle")
async def toggle_ai_agent(business_id: str, db: Session = Depends(database.get_db)):
    """Toggle the AI sub-agent on or off for a business."""
    biz = db.query(models.Business).filter(models.Business.id == business_id).first()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    biz.ai_agent_enabled = not biz.ai_agent_enabled
    db.commit()
    db.refresh(biz)
    return {"status": "success", "ai_agent_enabled": biz.ai_agent_enabled}

@router.get("/{business_id}/competitors")
async def get_competitors(business_id: str, db: Session = Depends(database.get_db)):
    """Get rival businesses in the same category and approximate location as this business."""
    biz = db.query(models.Business).filter(models.Business.id == business_id).first()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    # Find businesses with same category, exclude the requesting business
    rivals = (
        db.query(models.Business)
        .filter(
            models.Business.category == biz.category,
            models.Business.id != business_id,
            models.Business.claimed == True
        )
        .order_by(models.Business.rating.desc())
        .limit(10)
        .all()
    )

    result = []
    for i, r in enumerate(rivals):
        result.append({
            "rank": i + 1,
            "id": r.id,
            "name": r.name,
            "rating": r.rating,
            "review_count": r.review_count,
            "location": r.location,
            "verified": r.verified,
        })

    # Determine own rank among the full sorted list
    all_same_cat = (
        db.query(models.Business)
        .filter(models.Business.category == biz.category, models.Business.claimed == True)
        .order_by(models.Business.rating.desc())
        .all()
    )
    own_rank = next((i + 1 for i, b in enumerate(all_same_cat) if b.id == business_id), None)

    return {
        "status": "success",
        "business_id": business_id,
        "own_rank": own_rank,
        "total_in_category": len(all_same_cat),
        "competitors": result
    }
