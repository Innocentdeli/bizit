import time
import random
import sys
import os

# Add the parent directory to sys.path so we can import from database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import models, database

# List of businesses to seed
BUSINESSES = ["b-101", "b-102"]

# Analytics metadata choices
LOCATIONS = ["Yaba", "Surulere", "Victoria Island", "Ikeja", "Lekki", "Gbagada"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]
EVENT_TYPES = ["profile_view", "website_click", "direction_click", "lead"]
EVENT_WEIGHTS = [0.70, 0.15, 0.10, 0.05] # mostly views

def seed():
    db = database.SessionLocal()
    
    # Check if table exists, create if not
    models.Base.metadata.create_all(bind=database.engine)
    
    # We will generate events for the last 60 days
    now = time.time()
    day_in_seconds = 24 * 60 * 60
    
    print("Generating analytics events...")
    
    events_created = 0
    
    for business_id in BUSINESSES:
        # Check if business exists
        biz = db.query(models.Business).filter(models.Business.id == business_id).first()
        if not biz:
            print(f"Skipping {business_id} (not found in DB)")
            continue
            
        print(f"Seeding events for {biz.name} ({business_id})...")
        
        # We will generate a random number of events per day for the last 60 days
        for day in range(60, -1, -1):
            base_timestamp = now - (day * day_in_seconds)
            
            # Generate between 5 and 25 events per day
            events_today = random.randint(5, 25)
            
            for _ in range(events_today):
                # Pick a random hour, weighted towards peak hours (e.g. 10am-5pm)
                hour_offset = random.choices(
                    range(24), 
                    weights=[1,1,1,1,1,1,3,6,10,12,15,14,15,16,15,14,12,10,8,6,4,3,2,1], 
                    k=1
                )[0]
                minute_offset = random.randint(0, 59)
                
                # Timestamp within that day
                # Since base_timestamp is exactly 'now' minus days, let's normalize to start of that day
                event_time = base_timestamp - (base_timestamp % day_in_seconds) + (hour_offset * 3600) + (minute_offset * 60)
                
                event_type = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS, k=1)[0]
                location = random.choices(LOCATIONS, weights=[5,3,4,2,2,1], k=1)[0]
                age_group = random.choices(AGE_GROUPS, weights=[2,5,3,1,1], k=1)[0]
                
                event = models.AnalyticsEvent(
                    business_id=business_id,
                    event_type=event_type,
                    location_city=location,
                    user_age_group=age_group,
                    timestamp=event_time
                )
                db.add(event)
                events_created += 1
                
                # Update business counters to match
                if event_type == "profile_view":
                    biz.profile_views = (biz.profile_views or 0) + 1
                elif event_type == "lead":
                    biz.leads = (biz.leads or 0) + 1
                    
        db.commit()
    
    print(f"Successfully seeded {events_created} analytics events.")
    db.close()

if __name__ == "__main__":
    seed()
