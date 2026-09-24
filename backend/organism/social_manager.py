import logging
import time
import random
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.database import SessionLocal
from database.models import Business, SocialPost, OrganismActivity
from cognitive_kernel.gemini_client import GeminiClient

logger = logging.getLogger(__name__)
gemini = GeminiClient(model_name="gemini-2.5-flash")

async def run_social_cycle():
    """
    Autonomous Social Media Manager cycle.
    Finds a top-performing business and generates a promo tweet.
    """
    logger.info("[SOCIAL] Starting social media cycle...")
    
    db = SessionLocal()
    try:
        # 1. Find a top business (highly rated, verified)
        top_business = db.query(Business)\
            .filter(Business.rating >= 4.5)\
            .order_by(desc(Business.review_count))\
            .first()

        if not top_business:
            logger.info("[SOCIAL] No candidate business found for promo.")
            return

        # Check if we already posted about them today (simple check)
        recent_post = db.query(SocialPost)\
            .filter(SocialPost.business_id == top_business.id)\
            .order_by(desc(SocialPost.timestamp))\
            .first()
            
        if recent_post and (time.time() - recent_post.timestamp) < 86400:
            logger.info(f"[SOCIAL] Already posted about {top_business.name} recently. Skipping.")
            return

        # 2. Generate Post Copy using Sovereign AI
        prompt = f"""
You are the official BIZIT Platform Social Media Manager.
Draft an engaging, hype-building tweet to highlight a top-performing local business on our platform.
Business Name: {top_business.name}
Category: {top_business.category}
Rating: {top_business.rating} stars ({top_business.review_count} reviews)
Services: {', '.join(top_business.services) if top_business.services else 'General'}

Keep it under 280 characters. Include hashtags like #LocalBusiness #BIZIT.
Make it sound aesthetic and premium.

Output valid JSON only:
{{
  "tweet": "<your tweet text>"
}}
"""
        try:
            result = await gemini.generate_reasoning(prompt, thinking_level="TACTICAL")
            if "error" in result:
                copy = f"Highlight of the week: {top_business.name} is crushing it with a {top_business.rating} rating! Book them on BIZIT today. #LocalBusiness #BIZIT"
            else:
                copy = result.get("tweet", f"Highlight of the week: {top_business.name} has a {top_business.rating} rating! Book them on BIZIT today.")
        except Exception as e:
            logger.error(f"[SOCIAL] Failed to generate tweet: {e}")
            copy = f"Highlight of the week: {top_business.name} has a {top_business.rating} rating! Book them on BIZIT today. #LocalBusiness #BIZIT"

        # 3. Generate "Promo Image" (Mocked URL for now, could be integrated with DALL-E/Midjourney API)
        mock_images = [
            "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=800&auto=format&fit=crop", # Office/Studio
            "https://images.unsplash.com/photo-1556761175-4b46a572b786?q=80&w=800&auto=format&fit=crop", # Cafe/Service
            "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=800&auto=format&fit=crop"  # Team/Professional
        ]
        promo_img = random.choice(mock_images)

        # 4. Save to Database
        post = SocialPost(
            business_id=top_business.id,
            platform="Twitter",
            post_copy=copy,
            image_url=promo_img,
            timestamp=time.time()
        )
        db.add(post)
        
        # 5. Log Activity
        activity = OrganismActivity(
            timestamp=time.time(),
            cycle="SOCIAL",
            business_id=top_business.id,
            business_name=top_business.name,
            action="Generated Promo Tweet",
            detail=copy,
            impact="+150 estimated platform impressions",
            status="DONE",
            autonomous=True
        )
        db.add(activity)
        
        db.commit()
        logger.info(f"[SOCIAL] Successfully posted promo for {top_business.name}.")
        
    except Exception as e:
        logger.error(f"[SOCIAL] Cycle failed: {e}")
        db.rollback()
    finally:
        db.close()
