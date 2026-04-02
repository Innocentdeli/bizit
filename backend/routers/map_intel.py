from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from database.database import get_db
from database.models import Business

router = APIRouter()

@router.get("/pins")
async def get_map_pins(lat: float, lng: float, radius: float = 10.0, db: Session = Depends(get_db)):
    """
    Module 2: Location & Map Intelligence
    Returns real business pins from the database within a roughly calculated radius.
    """
    # Simple bounding box for radius (approximate km to degrees)
    # 1 degree lat is ~111km. 1 degree lng varies but ~111km at equator.
    lat_delta = radius / 111.0
    lng_delta = radius / (111.0 * 0.8) # Adjust for mid-latitudes

    businesses = db.query(Business).filter(
        Business.lat >= lat - lat_delta,
        Business.lat <= lat + lat_delta,
        Business.lng >= lng - lng_delta,
        Business.lng <= lng + lng_delta
    ).all()

    return {
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius,
        "pins": [
            {
                "id": b.id,
                "name": b.name,
                "lat": b.lat,
                "lng": b.lng,
                "type": b.category
            } for b in businesses
        ]
    }

@router.get("/heatmaps/density")
async def get_density_heatmap(lat: float, lng: float, db: Session = Depends(get_db)):
    """
    Sub-Feature: Dynamic Density heatmaps (business concentration)
    """
    # Count businesses in specific zones or nearby
    businesses = db.query(Business).all()
    
    # Simple clustering logic for demo/prototype
    # In production, use PostGIS or specialized clustering
    zones = {}
    for b in businesses:
        if b.location:
            zone = b.location.split(',')[0].strip()
            zones[zone] = zones.get(zone, 0) + 1
            
    intensity_zones = [
        {"zone": zone, "score": min(1.0, count/10), "count": count}
        for zone, count in zones.items()
    ]

    return {
        "intensity_zones": sorted(intensity_zones, key=lambda x: x["score"], reverse=True)
    }
