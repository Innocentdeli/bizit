from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

@router.get("/snapshot")
async def get_market_snapshot(location: str = "Lagos", category: str = "Technology"):
    """
    Module 6: Market Snapshot Engine
    Purpose: Show instant market-level insight per category/location.
    """
    return {
        "location": location,
        "category": category,
        "metrics": {
            "total_businesses": 142,
            "competition_level": "HIGH",
            "avg_pricing": "₦350,000/mo",
            "avg_rating": 4.2,
            "growth_trend": "+12% YoY",
            "saturation_score": 0.78  # 0 to 1
        }
    }

@router.get("/supply-demand")
async def get_supply_demand(location: str = "Lagos"):
    """
    Module 7: Supply vs Demand Analytics
    Purpose: Reveal opportunities and saturation clearly.
    """
    return {
        "demand_signal": {
            "searches": 4500,
            "clicks": 1200,
            "trend": "UP"
        },
        "supply_signal": {
            "active_businesses": 142,
            "new_entrants_last_month": 5
        },
        "market_pressure": 0.85, # High demand, low supply? or High competition?
        "status": "OPPORTUNITY", # OPPORTUNITY, BALANCED, SATURATED
        "chart_data": [40, 65, 30, 80, 55, 90, 70]
    }

@router.get("/gaps")
async def get_market_gaps(location: str = "Lagos"):
    """
    Module 8: Gap Detection & Opportunity Engine
    Purpose: Identify unmet needs and profitable gaps.
    """
    return {
        "gaps": [
            {
                "type": "Underserved Service",
                "description": "24/7 Co-working spaces in Yaba",
                "demand_score": 0.9,
                "potential_revenue": "₦5M/mo"
            },
            {
                "type": "Price Gap",
                "description": "Budget-friendly healthy food delivery (<₦2000)",
                "demand_score": 0.85,
                "potential_revenue": "₦3M/mo"
            }
        ]
    }
