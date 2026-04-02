from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    location = Column(String)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    description = Column(String)
    hours = Column(String)
    phone = Column(String)
    website = Column(String)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    subscription_tier = Column(String, default="free")
    visibility_boost = Column(Float, default=0.0)
    services = Column(JSON) # Store list of strings


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
    
    business = relationship("Business")
