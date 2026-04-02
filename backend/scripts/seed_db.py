import sys
import os
import json

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import SessionLocal, engine
from database import models
from routers.business import MOCK_BUSINESSES

def seed_data():
    db = SessionLocal()
    
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    # Check if data exists
    if db.query(models.Business).first():
        print("Database already seeded.")
        return

    print("Seeding Businesses...")
    for b_data in MOCK_BUSINESSES:
        # Business Model has specific fields, we need to map MOCK_BUSINESSES to it
        # Note: MOCK_BUSINESSES in routers/business.py might need to be imported or copied if not accessible easily.
        # For now, let's use the raw data structure we know exists.
        
        # Adjusting for list -> JSON string or just using JSON type in SQLite
        # verify services is list
        
        business = models.Business(
            id=b_data["id"],
            name=b_data["name"],
            category=b_data["category"],
            location=b_data["location"],
            rating=b_data["rating"],
            review_count=b_data.get("review_count", 0),
            verified=b_data["verified"],
            description=b_data.get("description", ""),
            hours=b_data.get("hours", ""),
            phone=b_data.get("phone", ""),
            website=b_data.get("website", ""),
            services=b_data.get("services", [])
        )
        db.add(business)
    
    db.commit()
    print("Seeding Complete!")
    db.close()

if __name__ == "__main__":
    seed_data()
