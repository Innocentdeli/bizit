import os
import sys
import json
import random
from sqlalchemy.orm import Session
from database.database import engine, Base, SessionLocal
from database.models import Business, SearchHistory

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    
    # Check if we already have businesses
    if db.query(Business).count() > 0:
        print("Database already seeded. Dropping and re-seeding...")
        db.query(Business).delete()
        db.query(SearchHistory).delete()
        db.commit()

    businesses = [
        {
            "id": "b-101",
            "name": "Lagos Tech Hub",
            "category": "Technology & Innovation",
            "location": "15 Montgomery Road, Yaba, Lagos",
            "latitude": 6.505,
            "longitude": 3.375,
            "rating": 4.8,
            "review_count": 124,
            "verified": True,
            "subscription_tier": "premium",
            "description": "The premier destination for startups and tech innovators in West Africa. High-speed internet, dedicated desks, and incubation support.",
            "hours": "Open • Closes 10PM",
            "phone": "+234 800 BIZIT",
            "services": ["High-Speed WiFi", "Meeting Rooms", "24/7 Power", "Coffee Bar", "Event Space"],
            "profile_views": random.randint(500, 2000),
            "search_appearances": random.randint(2000, 5000),
            "leads": random.randint(20, 150)
        },
        {
            "id": "b-102",
            "name": "Mama Cassie's Catering",
            "category": "Food & Beverage",
            "location": "Ikeja, Lagos",
            "latitude": 6.601,
            "longitude": 3.351,
            "rating": 4.5,
            "review_count": 89,
            "verified": True,
            "subscription_tier": "pro",
            "description": "Authentic local dishes for corporate events and private celebrations. We deliver the taste of home to your office.",
            "hours": "Open • Closes 8PM",
            "phone": "+234 800 FOOD",
            "services": ["Catering", "Delivery", "Event Hosting", "Wedding Catering"],
            "profile_views": random.randint(500, 2000),
            "search_appearances": random.randint(2000, 5000),
            "leads": random.randint(20, 150)
        },
        {
            "id": "b-103",
            "name": "Blue Chip Logistics",
            "category": "Logistics & Freight",
            "location": "Apapa Port Complex, Lagos",
            "latitude": 6.444,
            "longitude": 3.361,
            "rating": 3.9,
            "review_count": 42,
            "verified": False,
            "subscription_tier": "free",
            "description": "Global shipping and freight forwarding. Clearing agents with 15+ years of port experience.",
            "hours": "Closes 5PM",
            "phone": "+234 800 MAIL",
            "services": ["Freight", "Shipping", "Warehousing", "Customs Clearing"],
            "profile_views": random.randint(100, 500),
            "search_appearances": random.randint(500, 1000),
            "leads": random.randint(5, 30)
        },
        {
            "id": "b-104",
            "name": "GlowUp Beauty Studio",
            "category": "Beauty & Wellness",
            "location": "Lekki Phase 1, Lagos",
            "latitude": 6.447,
            "longitude": 3.472,
            "rating": 4.9,
            "review_count": 203,
            "verified": True,
            "subscription_tier": "premium",
            "description": "Award-winning salon offering natural hair care, makeup artistry, and spa treatments in a luxury setting.",
            "hours": "Open • Closes 9PM",
            "phone": "+234 809 GLOW",
            "services": ["Hair Braiding", "Makeup", "Skincare", "Massage", "Nails"],
            "profile_views": random.randint(1000, 3000),
            "search_appearances": random.randint(3000, 8000),
            "leads": random.randint(50, 200)
        },
        {
            "id": "b-105",
            "name": "Abuja Solar Solutions",
            "category": "Electrical & Energy",
            "location": "Wuse 2, Abuja FCT",
            "latitude": 9.076,
            "longitude": 7.481,
            "rating": 4.6,
            "review_count": 67,
            "verified": True,
            "subscription_tier": "pro",
            "description": "Leading solar panel installation and inverter systems. Guaranteed 10-year warranty on all residential installs.",
            "hours": "Open • Closes 6PM",
            "phone": "+234 812 SOLAR",
            "services": ["Solar Installation", "Inverters", "Maintenance", "Power Audit"],
            "profile_views": random.randint(200, 800),
            "search_appearances": random.randint(800, 2000),
            "leads": random.randint(10, 80)
        },
        {
            "id": "b-106",
            "name": "Naija Motors Garage",
            "category": "Auto & Garage",
            "location": "Oregun Industrial Area, Lagos",
            "latitude": 6.605,
            "longitude": 3.365,
            "rating": 4.2,
            "review_count": 158,
            "verified": True,
            "subscription_tier": "free",
            "description": "Certified mechanics for all vehicle makes and models. Honest diagnostics with transparent pricing.",
            "hours": "Open • Closes 7PM",
            "phone": "+234 806 AUTO",
            "services": ["Servicing", "Repairs", "Diagnostics", "AC Repairs", "Tyre Change"],
            "profile_views": random.randint(500, 1500),
            "search_appearances": random.randint(1500, 4000),
            "leads": random.randint(30, 120)
        },
        {
            "id": "b-107",
            "name": "Eden Life Services",
            "category": "Home Services",
            "location": "Victoria Island, Lagos",
            "latitude": 6.428,
            "longitude": 3.421,
            "rating": 4.7,
            "review_count": 312,
            "verified": True,
            "subscription_tier": "premium",
            "description": "Premium managed home services. We handle your cleaning, laundry, and meals so you can focus on work.",
            "hours": "Open 24/7",
            "phone": "+234 800 EDEN",
            "services": ["Cleaning", "Laundry", "Meal Plans", "Pest Control"],
            "profile_views": random.randint(2000, 5000),
            "search_appearances": random.randint(5000, 12000),
            "leads": random.randint(100, 400)
        }
    ]

    for b_data in businesses:
        b = Business(**b_data)
        db.add(b)
    
    # Add some mock search history
    import time
    now = time.time()
    searches = [
        {"query": "Wedding Catering", "timestamp": now - 3600, "user_id": "anon-1"},
        {"query": "Wedding Catering", "timestamp": now - 7200, "user_id": "anon-2"},
        {"query": "Plumber", "timestamp": now - 86400, "user_id": "anon-3"},
        {"query": "Tech Hub", "timestamp": now - 172800, "user_id": "anon-4"},
    ]
    for s_data in searches:
        s = SearchHistory(**s_data)
        db.add(s)

    db.commit()
    print(f"Successfully seeded {len(businesses)} businesses into the database.")
    db.close()

if __name__ == "__main__":
    seed_db()
