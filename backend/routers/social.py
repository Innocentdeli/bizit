from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.database import get_db
from database.models import SocialPost, Business, Review
import time

router = APIRouter()

@router.get("/posts")
def get_social_posts(limit: int = 10, business_id: str = None, db: Session = Depends(get_db)):
    """Retrieve the latest social media posts, optionally filtered by business_id."""
    query = db.query(SocialPost).order_by(desc(SocialPost.timestamp))
    if business_id:
        query = query.filter(SocialPost.business_id == business_id)
    posts = query.limit(limit).all()
    
    result = []
    for p in posts:
        business_name = p.business.name if p.business else "Unknown Business"
        result.append({
            "id": p.id,
            "business_id": p.business_id,
            "business_name": business_name,
            "platform": p.platform,
            "post_copy": p.post_copy,
            "image_url": p.image_url,
            "timestamp": p.timestamp
        })
        
    return {"status": "success", "posts": result}

@router.post("/posts/{business_id}/generate")
def generate_social_post(business_id: str, db: Session = Depends(get_db)):
    """Generate and save a new social post for the business based on latest reviews."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    # Use most recent positive review as inspiration
    best_review = (
        db.query(Review)
        .filter(Review.business_id == business_id, Review.rating >= 4)
        .order_by(desc(Review.timestamp))
        .first()
    )

    if best_review:
        excerpt = best_review.comment[:100] + ("..." if len(best_review.comment) > 100 else "")
        copy = (
            f"Our customers speak for themselves! ⭐ One customer said: \"{excerpt}\""
            f"\n\nExperience the {business.name} difference today. Visit us at {business.location or 'our location'}."
            f"\n\n#{business.name.replace(' ', '')} #LocalBusiness #{(business.category or '').replace(' ', '')} #5Stars"
        )
    else:
        copy = (
            f"Big things are happening at {business.name}! 🚀"
            f"\n\nWe are proud to serve our community in {business.location or 'our area'}."
            f" Come discover why we are the go-to {business.category or 'business'} near you."
            f"\n\n#{business.name.replace(' ', '')} #LocalBusiness #SupportLocal"
        )

    post = SocialPost(
        business_id=business_id,
        platform="Instagram",
        post_copy=copy,
        image_url=business.photo_url,
        timestamp=time.time()
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"status": "success", "post": {"id": post.id, "post_copy": post.post_copy, "image_url": post.image_url, "platform": post.platform, "timestamp": post.timestamp}}
