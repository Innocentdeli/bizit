from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import time
from database.database import get_db, SessionLocal
from database.models import Review, Business
from organism.sub_agent import process_review_with_subagent

router = APIRouter()

def _run_review_subagent_bg(review_id: int, business_id: str):
    import asyncio
    db = SessionLocal()
    try:
        review = db.query(Review).filter(Review.id == review_id).first()
        business = db.query(Business).filter(Business.id == business_id).first()
        if review and business:
            asyncio.run(process_review_with_subagent(db, review, business))
    except Exception as e:
        db.rollback()
    finally:
        db.close()

@router.get("/{business_id}")
async def get_reviews(business_id: str, db: Session = Depends(get_db)):
    """
    Module 5: Get real reviews from the database for a business
    """
    reviews = db.query(Review).filter(Review.business_id == business_id).all()
    return {"status": "success", "count": len(reviews), "reviews": reviews}

@router.post("/")
async def add_review(review_data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Module 5: Submit a new review to the database
    Sub-Feature: Basic Sentiment Analysis
    """
    comment = review_data.get("comment", "")
    
    # Simple keyword-based sentiment for dynamism
    positive_words = ["excellent", "great", "good", "perfect", "highly", "best"]
    sentiment = "POSITIVE" if any(word in comment.lower() for word in positive_words) else "NEUTRAL"
    if "bad" in comment.lower() or "broken" in comment.lower() or "slow" in comment.lower():
        sentiment = "NEGATIVE"

    new_review = Review(
        business_id=review_data.get("business_id"),
        user_name=review_data.get("user_name", "Anonymous User"),
        rating=review_data.get("rating", 5),
        comment=comment,
        timestamp=time.time(),
        sentiment=sentiment,
        helpful_count=0
    )
    
    db.add(new_review)
    
    # Update business rating average
    business = db.query(Business).filter(Business.id == review_data.get("business_id")).first()
    if business:
        business.review_count += 1
        # Simple cumulative moving average
        business.rating = ((business.rating * (business.review_count - 1)) + new_review.rating) / business.review_count

    db.commit()
    db.refresh(new_review)

    if business and business.ai_agent_enabled:
        background_tasks.add_task(_run_review_subagent_bg, new_review.id, business.id)

    return {"status": "success", "review_id": new_review.id, "sentiment": sentiment}

@router.post("/{review_id}/vote")
async def vote_review(review_id: int, vote_type: str = "helpful", db: Session = Depends(get_db)):
    """
    Sub-Feature: Real review helpfulness voting
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    review.helpful_count += 1
    db.commit()
    return {"status": "success", "message": "Vote recorded", "new_count": review.helpful_count}
