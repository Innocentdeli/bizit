from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, JSON, Text, DateTime
import datetime
from sqlalchemy.orm import relationship
from .database import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    location = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    description = Column(String)
    hours = Column(String)
    phone = Column(String)
    website = Column(String)
    subscription_tier = Column(String, default="free")
    visibility_boost = Column(Float, default=0.0)
    services = Column(JSON) # Store list of strings
    
    # Sub-Agent Config
    ai_agent_enabled = Column(Boolean, default=False)
    ai_agent_prompt = Column(String, nullable=True) # Custom instructions
    
    
    # Ghost Listing Mechanics
    claimed = Column(Boolean, default=True)
    source_url = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    ghost_token = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)  # Real photo from Google Places
    

    profile_views = Column(Integer, default=0)
    search_appearances = Column(Integer, default=0)
    leads = Column(Integer, default=0)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String, ForeignKey("businesses.id"), index=True)
    event_type = Column(String, index=True)  # "profile_view", "website_click", "direction_click", "lead"
    location_city = Column(String, nullable=True) # e.g., "Yaba", "Surulere"
    user_age_group = Column(String, nullable=True) # e.g. "18-24"
    timestamp = Column(Float, index=True) # unix timestamp
    
    business = relationship("Business")


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    total_businesses = Column(Integer)
    avg_pricing = Column(String)
    saturation_score = Column(Float)
    timestamp = Column(String)

class AdCampaign(Base):
    __tablename__ = "ad_campaigns"

    id = Column(String, primary_key=True, index=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    title = Column(String)
    status = Column(String)
    budget = Column(Float)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    
    business = relationship("Business")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    query = Column(String)
    timestamp = Column(Float)

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    user_name = Column(String)
    rating = Column(Integer)
    comment = Column(String)
    timestamp = Column(Float)
    sentiment = Column(String, default="NEUTRAL")
    helpful_count = Column(Integer, default=0)
    agent_reply = Column(Text, nullable=True)
    reply_status = Column(String, default="PENDING")
    
    business = relationship("Business")


class OrganismActivity(Base):
    """
    Every autonomous action the Organism takes is logged here.
    This is the Organism's 'nervous system' trace.
    """
    __tablename__ = "organism_activity"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True)           # unix epoch
    cycle = Column(String)                          # ENRICH | VERIFY | ALERT | DEMAND | OUTREACH
    business_id = Column(String, ForeignKey("businesses.id"), nullable=True)
    business_name = Column(String, nullable=True)
    action = Column(String)                         # short action label
    detail = Column(Text)                           # full AI reasoning / output
    impact = Column(String, nullable=True)          # e.g. "+32 views expected"
    status = Column(String, default="DONE")         # DONE | PENDING | FAILED
    autonomous = Column(Boolean, default=True)      # was this AI-initiated?

    business = relationship("Business", foreign_keys=[business_id])


class OrganismAlert(Base):
    """
    Proactive alerts the Organism surfaces for business owners.
    """
    __tablename__ = "organism_alerts"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    timestamp = Column(Float)
    priority = Column(String, default="MEDIUM")     # HIGH | MEDIUM | LOW
    title = Column(String)
    body = Column(Text)
    action_label = Column(String, nullable=True)    # CTA text
    read = Column(Boolean, default=False)

    business = relationship("Business")


class SurgePricingEvent(Base):
    """
    Every autonomous pricing decision the Organism makes.
    Records the category, the multiplier applied, the trigger demand count,
    the base price, the surge price, and when it expires.
    """
    __tablename__ = "surge_pricing_events"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)          # e.g. "Wedding Catering"
    search_term = Column(String)                    # raw query term that triggered it
    demand_count = Column(Integer)                  # how many searches in 24h
    multiplier = Column(Float)                      # e.g. 1.20 for +20%
    base_price = Column(Float)                      # e.g. 5000
    surge_price = Column(Float)                     # e.g. 6000
    currency = Column(String, default="NGN")
    active = Column(Boolean, default=True)          # is this surge currently live?
    triggered_at = Column(Float)                    # unix timestamp
    expires_at = Column(Float)                      # unix timestamp (auto 72h)
    reason = Column(Text)                           # AI explanation


class CustomerInquiry(Base):
    """
    Messages sent from customers to a business.
    Handled by the AI Sub-Agent if ai_agent_enabled is True.
    """
    __tablename__ = "customer_inquiries"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    customer_name = Column(String)
    customer_email = Column(String)
    message = Column(Text)
    agent_reply = Column(Text, nullable=True)
    status = Column(String, default="PENDING")      # PENDING | REPLIED
    timestamp = Column(Float)

    business = relationship("Business")

class Appointment(Base):
    """
    Booking requests from customers.
    Handled by the AI Sub-Agent if ai_agent_enabled is True.
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    customer_name = Column(String)
    customer_email = Column(String)
    requested_time = Column(String)
    service = Column(String)
    agent_confirmation_message = Column(Text, nullable=True)
    status = Column(String, default="PENDING")      # PENDING | CONFIRMED
    timestamp = Column(Float)

    business = relationship("Business")

class SocialPost(Base):
    """
    Autonomous social media posts generated by the Organism.
    """
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String, ForeignKey("businesses.id"))
    platform = Column(String, default="Twitter")
    post_copy = Column(Text)
    image_url = Column(String, nullable=True)
    timestamp = Column(Float)
    
    business = relationship("Business")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user") # user, business_owner, admin
    business_id = Column(String, ForeignKey("businesses.id"), nullable=True)
    
    business = relationship("Business")
