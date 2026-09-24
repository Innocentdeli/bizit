"""
BIZIT Ad Launch Engine — Meta Marketing API.
No ad platform was connected before this. Same honest contract as
mailer.py/sms.py/paystack.py: fails closed and reports why until
META_ACCESS_TOKEN + META_AD_ACCOUNT_ID are configured.

Deliberately scoped to campaign-shell creation only, and every campaign is
created PAUSED. Ad sets (targeting + budget schedule), ad creatives (actual
image/video + copy), and ads (which link a creative into an ad set) are NOT
created here — a real campaign needs all of that before Meta will let it
spend, and building that blind, with no live ad account to verify against,
is not something to ship silently. A merchant must finish setup (targeting,
creative, and un-pausing) in Meta Ads Manager before this campaign spends
anything. Verify this against a real ad account in Meta's sandbox before
trusting it for a live launch.
"""
import os
import logging
from typing import Optional

import httpx

logger = logging.getLogger("organism.meta_ads")

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID")  # numeric id, without the "act_" prefix
GRAPH_API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

OBJECTIVE_MAP = {
    "revenue": "OUTCOME_SALES",
    "leads": "OUTCOME_LEADS",
    "awareness": "OUTCOME_AWARENESS",
    "traffic": "OUTCOME_TRAFFIC",
    "engagement": "OUTCOME_ENGAGEMENT",
}


async def create_campaign(name: str, objective_key: str, daily_budget_ngn: float) -> Optional[dict]:
    """
    Creates a PAUSED campaign shell on the connected ad account. Returns
    {"campaign_id": ..., "status": "PAUSED"} on success, None if unconfigured
    or Meta rejects the request.
    """
    if not META_ACCESS_TOKEN or not META_AD_ACCOUNT_ID:
        logger.warning("📢 [META ADS] No META_ACCESS_TOKEN/META_AD_ACCOUNT_ID configured. Campaign not created.")
        return None

    objective = OBJECTIVE_MAP.get(objective_key, "OUTCOME_TRAFFIC")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{BASE_URL}/act_{META_AD_ACCOUNT_ID}/campaigns",
                params={"access_token": META_ACCESS_TOKEN},
                json={
                    "name": name,
                    "objective": objective,
                    "status": "PAUSED",
                    "special_ad_categories": [],
                    # Daily budget lives on the ad set in Meta's model, not the
                    # campaign — recorded here only so callers can see intent.
                },
            )
            data = resp.json()
            if resp.status_code in (200, 201) and data.get("id"):
                logger.info(f"📢 [META ADS] ✅ Created PAUSED campaign '{name}' ({data['id']}) — ad sets/creative still need manual setup.")
                return {"campaign_id": data["id"], "status": "PAUSED"}
            logger.error(f"📢 [META ADS] ❌ Campaign creation rejected: {data.get('error', {}).get('message')}")
            return None
    except Exception as e:
        logger.error(f"📢 [META ADS] ❌ Campaign creation failed: {e}")
        return None
