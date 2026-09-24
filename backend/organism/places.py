"""
BIZIT Google Places Enricher
Pulls real business data (photos, hours, phone, website) from the Google Places API.
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger("organism.places")

PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"


async def search_place(business_name: str, location: str) -> Optional[str]:
    """Search for a business and return its Google Place ID."""
    if not PLACES_API_KEY:
        logger.warning("🗺️ [PLACES] No Google Places API key.")
        return None

    query = f"{business_name} {location}"
    url = f"{PLACES_BASE_URL}/findplacefromtext/json"
    params = {
        "input": query,
        "inputtype": "textquery",
        "fields": "place_id,name",
        "key": PLACES_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, params=params)
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0].get("place_id")
    except Exception as e:
        logger.error(f"🗺️ [PLACES] findplace error: {e}")
    return None


async def get_place_details(place_id: str) -> Dict[str, Any]:
    """Fetch full details for a Place ID — phone, website, hours, rating, photos."""
    if not PLACES_API_KEY:
        return {}

    url = f"{PLACES_BASE_URL}/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_phone_number,website,opening_hours,rating,user_ratings_total,photos,formatted_address,geometry",
        "key": PLACES_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, params=params)
            data = res.json()
            result = data.get("result", {})

            # Pull the first photo URL if available
            photo_url = None
            photos = result.get("photos", [])
            if photos:
                photo_ref = photos[0].get("photo_reference")
                if photo_ref:
                    photo_url = (
                        f"{PLACES_BASE_URL}/photo?maxwidth=800"
                        f"&photoreference={photo_ref}&key={PLACES_API_KEY}"
                    )

            # Parse opening hours into a readable string
            hours_text = None
            opening_hours = result.get("opening_hours", {})
            weekday_text = opening_hours.get("weekday_text", [])
            if weekday_text:
                hours_text = " | ".join(weekday_text[:3])  # First 3 days for brevity

            # Extract geometry (latitude/longitude)
            lat = None
            lng = None
            geometry = result.get("geometry", {})
            location = geometry.get("location", {})
            if location:
                lat = location.get("lat")
                lng = location.get("lng")

            return {
                "phone": result.get("formatted_phone_number"),
                "website": result.get("website"),
                "hours": hours_text,
                "rating": result.get("rating"),
                "review_count": result.get("user_ratings_total"),
                "photo_url": photo_url,
                "address": result.get("formatted_address"),
                "latitude": lat,
                "longitude": lng,
            }
    except Exception as e:
        logger.error(f"🗺️ [PLACES] details error: {e}")
    return {}


async def enrich_business_with_places(business_name: str, location: str) -> Dict[str, Any]:
    """
    Full pipeline: search → get place ID → fetch details.
    Returns a dict of enriched fields to update on the Business model.
    """
    place_id = await search_place(business_name, location)
    if not place_id:
        logger.info(f"🗺️ [PLACES] No place found for '{business_name}' in '{location}'")
        return {}

    details = await get_place_details(place_id)
    if details:
        logger.info(f"🗺️ [PLACES] ✅ Enriched '{business_name}' with real Google Places data")
    return details
