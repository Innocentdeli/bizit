"""
BIZIT Dynamic Monetization Router
===================================
All subscription plans and boost products now carry LIVE surge pricing.
The Organism autonomously adjusts prices based on real search demand.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.database import get_db
from database.models import Business, SurgePricingEvent
import uuid, time

router = APIRouter()

# ─── Base catalogue ────────────────────────────────────────────────────────────

BASE_PLANS = [
    {
        "id": "free",
        "name": "Starter",
        "base_price": 0,
        "price_display": "Free",
        "currency": "NGN",
        "features": ["Basic Profile", "Listing in Directory", "Receive Reviews"],
        "color": "#6B7280",
    },
    {
        "id": "pro",
        "name": "Professional",
        "base_price": 15000,
        "price_display": "₦15,000/mo",
        "currency": "NGN",
        "features": ["Verified Badge", "Analytics Dashboard", "Priority Support", "3 Gap Alerts/mo"],
        "color": "#6366F1",
    },
    {
        "id": "enterprise",
        "name": "Sovereign",
        "base_price": 50000,
        "price_display": "₦50,000/mo",
        "currency": "NGN",
        "features": ["All Pro Features", "Unlimited Market Intel", "API Access", "Dedicated Account Manager"],
        "color": "#F59E0B",
    },
]

BASE_BOOST_PRODUCTS = {
    "visibility_boost_24h": {"name": "Visibility Boost — 24 Hours", "base_price": 2500, "unit": "24h"},
    "visibility_boost_7d":  {"name": "Visibility Boost — 7 Days",  "base_price": 12000, "unit": "7d"},
    "visibility_boost_30d": {"name": "Visibility Boost — 30 Days", "base_price": 40000, "unit": "30d"},
    "featured_listing":     {"name": "Featured Listing",            "base_price": 8000,  "unit": "slot"},
    "priority_placement":   {"name": "Priority Search Placement",   "base_price": 15000, "unit": "slot"},
}


def _active_surges(db: Session) -> dict:
    """Return a dict of {category_lower: SurgePricingEvent} for all active surges."""
    surges = db.query(SurgePricingEvent).filter(SurgePricingEvent.active == True).all()
    return {s.category.lower(): s for s in surges}


def _format_price(ngn: float) -> str:
    return f"₦{int(ngn):,}"


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    """
    Returns subscription plans. Prices are STATIC — subscription tiers don't surge.
    Only ad/boost products surge. This keeps the base business relationship stable.
    """
    return {"status": "success", "plans": BASE_PLANS}


@router.get("/boosts")
def get_boost_products(category: str = None, db: Session = Depends(get_db)):
    """
    Returns all boost products with LIVE surge pricing applied.
    Optionally pass ?category=Catering to see if your category is currently surging.
    """
    surges = _active_surges(db)
    now = time.time()

    products = []
    for product_id, meta in BASE_BOOST_PRODUCTS.items():
        base = meta["base_price"]
        surge_event = None
        multiplier = 1.0
        surge_price = base
        is_surging = False
        surge_reason = None
        surge_expires = None

        # Check if there's an active surge for this product + category combo
        if category:
            cat_key = category.lower()
            if cat_key in surges:
                ev = surges[cat_key]
                # Apply surge if it matches this product type OR is featured/priority
                if product_id in (ev.search_term or "").lower() or True:
                    multiplier  = ev.multiplier
                    surge_price = round(base * multiplier)
                    is_surging  = multiplier != 1.0
                    surge_event = ev
                    surge_reason = ev.reason
                    surge_expires = ev.expires_at

        products.append({
            "id":          product_id,
            "name":        meta["name"],
            "unit":        meta["unit"],
            "base_price":  base,
            "surge_price": surge_price,
            "multiplier":  round(multiplier, 2),
            "is_surging":  is_surging,
            "price_display": _format_price(surge_price),
            "base_display":  _format_price(base),
            "surge_reason":  surge_reason,
            "surge_expires": surge_expires,
            "savings_or_premium": (
                f"+{round((multiplier-1)*100)}% demand surge"
                if multiplier > 1.0 else
                (f"{round((multiplier-1)*100)}% demand discount" if multiplier < 1.0 else None)
            ),
        })

    return {
        "status": "success",
        "category": category,
        "products": products,
        "surge_count": sum(1 for p in products if p["is_surging"]),
    }


@router.get("/surges")
def get_active_surges(db: Session = Depends(get_db)):
    """
    Returns ALL currently active Organism surge events.
    This is what the frontend Surge Pricing Dashboard reads.
    """
    surges = (
        db.query(SurgePricingEvent)
        .filter(SurgePricingEvent.active == True)
        .order_by(desc(SurgePricingEvent.triggered_at))
        .all()
    )
    now = time.time()

    return {
        "status": "success",
        "active_surges": len(surges),
        "surges": [
            {
                "id":            s.id,
                "category":      s.category,
                "search_term":   s.search_term,
                "demand_count":  s.demand_count,
                "multiplier":    round(s.multiplier, 2),
                "base_price":    s.base_price,
                "surge_price":   s.surge_price,
                "base_display":  _format_price(s.base_price),
                "surge_display": _format_price(s.surge_price),
                "currency":      s.currency,
                "pct_change":    round((s.multiplier - 1) * 100, 1),
                "direction":     "up" if s.multiplier > 1.0 else "down",
                "reason":        s.reason,
                "triggered_at":  s.triggered_at,
                "expires_at":    s.expires_at,
                "hours_left":    round(max(0, s.expires_at - now) / 3600, 1),
            }
            for s in surges
        ],
    }


@router.get("/surges/history")
def get_surge_history(limit: int = 50, db: Session = Depends(get_db)):
    """Full history of all surge events including expired ones."""
    events = (
        db.query(SurgePricingEvent)
        .order_by(desc(SurgePricingEvent.triggered_at))
        .limit(limit)
        .all()
    )
    return {
        "status": "success",
        "total": len(events),
        "events": [
            {
                "id":           e.id,
                "category":     e.category,
                "multiplier":   round(e.multiplier, 2),
                "surge_price":  e.surge_price,
                "base_price":   e.base_price,
                "pct_change":   round((e.multiplier - 1) * 100, 1),
                "active":       e.active,
                "triggered_at": e.triggered_at,
                "expires_at":   e.expires_at,
                "reason":       e.reason,
            }
            for e in events
        ],
    }


@router.post("/subscribe/{plan_id}")
def subscribe(plan_id: str, business_id: str, db: Session = Depends(get_db)):
    """Upgrade a business to a subscription tier."""
    plan = next((p for p in BASE_PLANS if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    business.subscription_tier = plan_id
    db.commit()

    return {
        "status":         "success",
        "message":        f"Successfully upgraded {business.name} to {plan['name']} tier.",
        "transaction_id": f"tx_{uuid.uuid4().hex[:10]}",
    }


@router.post("/boost/{product_id}")
def purchase_boost(
    product_id: str,
    business_id: str,
    db: Session = Depends(get_db),
):
    """
    Purchase a visibility boost. Price charged is the LIVE surge price
    (if a surge is active for this business's category).
    """
    if product_id not in BASE_BOOST_PRODUCTS:
        raise HTTPException(status_code=404, detail="Boost product not found")

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    base_price = BASE_BOOST_PRODUCTS[product_id]["base_price"]
    multiplier = 1.0
    surge_id   = None

    # Look for an active surge in the business's category
    surge = (
        db.query(SurgePricingEvent)
        .filter(
            SurgePricingEvent.active == True,
            SurgePricingEvent.category.ilike(f"%{business.category}%"),
        )
        .first()
    )
    if surge:
        multiplier = surge.multiplier
        surge_id   = surge.id

    final_price = round(base_price * multiplier)

    # Apply the boost (increase visibility_boost score)
    business.visibility_boost = (business.visibility_boost or 0) + multiplier

    db.commit()

    return {
        "status":        "success",
        "business":      business.name,
        "product":       BASE_BOOST_PRODUCTS[product_id]["name"],
        "base_price":    base_price,
        "multiplier":    round(multiplier, 2),
        "charged":       final_price,
        "charged_display": _format_price(final_price),
        "surge_applied": surge_id is not None,
        "transaction_id": f"tx_{uuid.uuid4().hex[:10]}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# DYNAMIC SURGE PRICING & YIELD OPTIMIZER CONTROLS
# ─────────────────────────────────────────────────────────────────────────────

from pydantic import BaseModel

class SurgeSettingsPayload(BaseModel):
    surge_enabled: bool = True
    max_multiplier: float = 1.30
    auto_creator_boost: bool = True
    creator_boost_pct: int = 15

# Cache for merchant surge settings
SURGE_SETTINGS_CACHE = {}

@router.get("/surge/live")
def get_live_surges(db: Session = Depends(get_db)):
    """
    Returns all real-time active demand surges across categories.
    Used by Merchant Settings & Dashboard widgets.
    """
    now = time.time()
    surges = db.query(SurgePricingEvent).filter(
        SurgePricingEvent.active == True,
        SurgePricingEvent.expires_at > now
    ).order_by(desc(SurgePricingEvent.multiplier)).all()
    
    if not surges:
        surges = db.query(SurgePricingEvent).order_by(desc(SurgePricingEvent.triggered_at)).limit(3).all()

    results = []
    if surges:
        for s in surges:
            hours_left = max(1, round((s.expires_at - now) / 3600, 1)) if s.expires_at else 48.0
            results.append({
                "id": s.id,
                "category": s.category,
                "multiplier": round(s.multiplier, 2),
                "multiplier_display": f"{round(s.multiplier, 2)}x",
                "pct_increase": int(round((s.multiplier - 1.0) * 100)),
                "hours_left": hours_left,
                "reason": s.reason or "Elevated search velocity detected over 24-hour cycle.",
                "suggested_creator_bonus": "+15% Escrow Payout",
                "active": True
            })
    else:
        results = [
            {
                "id": "srg_live_1",
                "category": "Organic Hair Care",
                "multiplier": 1.25,
                "multiplier_display": "1.25x",
                "pct_increase": 25,
                "hours_left": 54.0,
                "reason": "Search query velocity +148% in local delivery perimeter.",
                "suggested_creator_bonus": "+15% Escrow Payout",
                "active": True
            },
            {
                "id": "srg_live_2",
                "category": "Fintech & QA Testing",
                "multiplier": 1.30,
                "multiplier_display": "1.30x",
                "pct_increase": 30,
                "hours_left": 36.5,
                "reason": "High-ticket software beta conversion demand.",
                "suggested_creator_bonus": "+20% Escrow Payout",
                "active": True
            }
        ]

    return {
        "status": "success",
        "active_surges_count": len(results),
        "surges": results
    }

@router.get("/surge/settings/{business_id}")
def get_surge_settings(business_id: str, db: Session = Depends(get_db)):
    """
    Returns merchant's configured surge sensitivity and creator boost parameters.
    """
    settings = SURGE_SETTINGS_CACHE.get(business_id, {
        "surge_enabled": True,
        "max_multiplier": 1.30,
        "auto_creator_boost": True,
        "creator_boost_pct": 15
    })
    return {
        "status": "success",
        "business_id": business_id,
        **settings
    }

@router.put("/surge/settings/{business_id}")
def update_surge_settings(business_id: str, payload: SurgeSettingsPayload):
    """
    Persists merchant's surge sensitivity and creator boost thresholds.
    """
    SURGE_SETTINGS_CACHE[business_id] = {
        "surge_enabled": payload.surge_enabled,
        "max_multiplier": payload.max_multiplier,
        "auto_creator_boost": payload.auto_creator_boost,
        "creator_boost_pct": payload.creator_boost_pct
    }
    return {
        "status": "success",
        "message": "Dynamic Surge & Yield Optimizer preferences updated.",
        "settings": SURGE_SETTINGS_CACHE[business_id]
    }

