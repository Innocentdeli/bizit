import os
import uuid
import random
from sqlalchemy.orm import Session
from database.database import engine, Base, SessionLocal
from database.models import Business

# Ensure tables are created
Base.metadata.create_all(bind=engine)

CATEGORIES = ["Technology & Innovation", "Food & Beverage", "Logistics & Freight", "Beauty & Wellness", "Electrical & Energy", "Auto & Garage", "Home Services", "Real Estate", "Healthcare"]
ADJECTIVES = ["Prime", "Global", "NextGen", "Smart", "Eco", "Pro", "Urban", "Crystal", "Golden", "Apex", "Nova", "Elite", "Swift", "Dynamic"]
NOUNS = ["Solutions", "Hub", "Enterprises", "Consulting", "Group", "Network", "Ventures", "Partners", "Systems", "Labs", "Studios", "Dynamics"]
STREETS = ["Awolowo Road", "Adetokunbo Ademola Street", "Allen Avenue", "Isaac John Street", "Admiralty Way", "Bode Thomas Street", "Montgomery Road", "Ahmadu Bello Way"]
AREAS = ["Ikoyi", "Victoria Island", "Lekki Phase 1", "Ikeja", "Yaba", "Surulere", "Apapa", "Gbagada"]

def generate_random_business():
    b_id = f"b-{uuid.uuid4().hex[:6]}"
    name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
    category = random.choice(CATEGORIES)
    
    area = random.choice(AREAS)
    street = random.choice(STREETS)
    location = f"{random.randint(1, 100)} {street}, {area}, Lagos"
    
    # Rough Lagos coordinates
    # lat ~ 6.4 to 6.6, lng ~ 3.3 to 3.5
    lat = random.uniform(6.4, 6.6)
    lng = random.uniform(3.3, 3.5)
    
    rating = round(random.uniform(3.0, 5.0), 1)
    review_count = random.randint(0, 500)
    verified = random.choice([True, False])
    tier = random.choice(["free", "free", "free", "pro", "premium"])
    
    description = f"A leading provider of {category.lower()} services in {area}. We pride ourselves on quality, speed, and customer satisfaction. Contact us today to learn more."
    
    hours = random.choice(["Open 24/7", "Open • Closes 8PM", "Open • Closes 5PM", "Open • Closes 10PM"])
    phone = f"+234 {random.randint(8000000000, 8199999999)}"
    
    profile_views = random.randint(50, 5000)
    search_appearances = profile_views + random.randint(100, 2000)
    leads = int(profile_views * random.uniform(0.01, 0.1))
    
    services = [f"{category.split(' ')[0]} Service", "Consultation", "Support"]
    
    return {
        "id": b_id,
        "name": name,
        "category": category,
        "location": location,
        "latitude": lat,
        "longitude": lng,
        "rating": rating,
        "review_count": review_count,
        "verified": verified,
        "subscription_tier": tier,
        "description": description,
        "hours": hours,
        "phone": phone,
        "services": services,
        "profile_views": profile_views,
        "search_appearances": search_appearances,
        "leads": leads,
        "claimed": random.choice([True, False])
    }

def seed_50():
    db = SessionLocal()
    
    businesses = []
    for _ in range(50):
        b_data = generate_random_business()
        businesses.append(b_data)
        b = Business(**b_data)
        db.add(b)
    
    db.commit()
    print(f"Successfully seeded 50 additional businesses into the database. Total businesses: {db.query(Business).count()}")
    db.close()

if __name__ == "__main__":
    seed_50()
