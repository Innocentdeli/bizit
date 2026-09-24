"""
seed_surges.py
Inserts demo surge pricing events so the Surge Pricing Dashboard
has data to display before the Organism runs its first live cycle.
"""
import sys, os, time, random
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.database import SessionLocal
from database.models import SurgePricingEvent

BASE_PRICES = {
    "visibility_boost_24h": 2500,
    "visibility_boost_7d":  12000,
    "featured_listing":     8000,
    "priority_placement":   15000,
}

DEMO_SURGES = [
    {
        "category": "Wedding Catering",
        "search_term": "wedding catering",
        "demand_count": 512,
        "multiplier": 1.38,
        "product": "visibility_boost_7d",
        "reason": "Wedding Catering searches spiked 38% this week — peak wedding season demand detected.",
    },
    {
        "category": "Real Estate",
        "search_term": "real estate agent Lagos",
        "demand_count": 304,
        "multiplier": 1.20,
        "product": "featured_listing",
        "reason": "Property searches up 20% following interest rate announcements — buyer urgency is high.",
    },
    {
        "category": "Fashion & Boutique",
        "search_term": "ankara fashion boutique",
        "demand_count": 287,
        "multiplier": 1.15,
        "product": "visibility_boost_24h",
        "reason": "Fashion demand surging ahead of upcoming cultural festivals in Lagos and Abuja.",
    },
    {
        "category": "Tech Repair",
        "search_term": "phone repair near me",
        "demand_count": 198,
        "multiplier": 0.85,
        "product": "visibility_boost_24h",
        "reason": "Supply exceeds demand in this category — price dropped 15% to incentivise more boosts.",
    },
    {
        "category": "Event Photography",
        "search_term": "photographer for event Abuja",
        "demand_count": 445,
        "multiplier": 1.60,
        "product": "priority_placement",
        "reason": "Event Photography is the single most searched service this weekend — surge capped at 60%.",
    },
    {
        "category": "Cleaning Services",
        "search_term": "house cleaning service",
        "demand_count": 143,
        "multiplier": 1.10,
        "product": "visibility_boost_24h",
        "reason": "Moderate 10% surge detected as end-of-month cleaning bookings rise.",
    },
]

def seed():
    db = SessionLocal()
    now = time.time()
    added = 0

    for s in DEMO_SURGES:
        exists = db.query(SurgePricingEvent).filter(
            SurgePricingEvent.category == s["category"],
            SurgePricingEvent.active == True
        ).first()
        if exists:
            print(f"  SKIP  {s['category']} — already has active surge")
            continue

        base  = BASE_PRICES.get(s["product"], 2500)
        surge = round(base * s["multiplier"])
        age   = random.randint(0, 36) * 3600  # triggered 0–36 hours ago

        event = SurgePricingEvent(
            category     = s["category"],
            search_term  = s["search_term"],
            demand_count = s["demand_count"],
            multiplier   = s["multiplier"],
            base_price   = base,
            surge_price  = surge,
            currency     = "NGN",
            active       = True,
            triggered_at = now - age,
            expires_at   = now - age + 72 * 3600,
            reason       = s["reason"],
        )
        db.add(event)
        added += 1
        direction = "UP  " if s["multiplier"] > 1 else "DOWN"
        print(f"  {direction}  {s['category']}  x{s['multiplier']}  NGN {surge:,}")

    db.commit()
    db.close()
    print(f"\nDone. {added} surge events seeded.")

if __name__ == "__main__":
    seed()
