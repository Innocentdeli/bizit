import os

TRIGGER_PY = r'''
"""
growth_loop_trigger.py
======================
Autonomous Growth Loop auto-queuer.
Called by the Organism SURGE cycle when a new SurgePricingEvent is created.

This is the missing link that makes Dima truly autonomous:
  SURGE detected ? auto-generate campaign + sequence ? queue in Execution Hub
  WITHOUT any human clicking.
"""

import time
import logging
import re
import asyncio
from typing import Optional
from sqlalchemy.orm import Session
from database.models import Business, OrganismActivity

logger = logging.getLogger("organism.growth_loop_trigger")


def _log_activity(db: Session, action: str, detail: str, impact: str = None, business: Business = None):
    """Log an autonomous activity to the Organism feed."""
    db.add(OrganismActivity(
        timestamp=time.time(),
        cycle="GROWTH_LOOP",
        business_id=business.id if business else None,
        business_name=business.name if business else None,
        action=action,
        detail=detail,
        impact=impact,
        status="DONE",
        autonomous=True,
    ))
    db.commit()


async def auto_queue_growth_loop(
    db: Session,
    surge_term: str,
    pct_change: float,
    category: str = "General",
    surge_id: Optional[str] = None,
    business: Optional[Business] = None,
):
    """
    Autonomous trigger: when the Organism detects a surge, auto-create a 
    pending growth loop run for every active business in that category.

    This populates the Execution Hub WITHOUT any user interaction.
    Users see it in pending_review status and can dispatch with 1 click.
    """
    try:
        # Find businesses matching this surge category
        query = db.query(Business)
        if category and category.lower() != "general":
            matched_businesses = query.filter(
                (Business.category.ilike(f"%{category}%")) |
                (Business.description.ilike(f"%{surge_term}%"))
            ).limit(5).all()
        else:
            matched_businesses = query.limit(3).all()

        if not matched_businesses and business:
            matched_businesses = [business]
        elif not matched_businesses:
            matched_businesses = query.limit(2).all()

        queued = 0

        for biz in matched_businesses:
            try:
                # Build brand-voiced copy using available data
                business_name = biz.name or "My Business"
                value_prop = biz.description or ""
                brand_tone = "Authoritative"
                if biz.ai_agent_prompt:
                    m = re.search(r"TONE:([^|]+)", biz.ai_agent_prompt)
                    if m:
                        brand_tone = m.group(1).strip()

                email_subject = "{}: {} demand up +{:.0f}% - window open now".format(
                    business_name, surge_term, pct_change)
                email_body = (
                    "Hi {{first_name}},\n\n"
                    "Our Autonomous Growth OS detected a {} surge (+{:.0f}% this week).\n\n"
                    "{} is positioned to help {{company}} capitalise on this window before competitors react.\n\n"
                    "{}\n\n"
                    "Reply to activate your personalised growth strategy.\n\n"
                    "Best regards,\n{} Growth Team"
                ).format(
                    surge_term, pct_change, business_name,
                    ("Our advantage: " + value_prop[:120]) if value_prop else "We are ready to deploy immediately.",
                    business_name
                )
                whatsapp_body = (
                    "Hi {{first_name}} {} here. ".format(business_name) +
                    "Spotted a {} surge (+{:.0f}% this week). ".format(surge_term, pct_change) +
                    "Strong window for {{company}} - want the breakdown? Reply YES."
                )

                # Try Gemini copy generation
                try:
                    from cognitive_kernel.gemini_client import GeminiClient
                    gemini = GeminiClient(model_name="gemini-2.5-flash")
                    if gemini.api_key:
                        prompt = (
                            "You are a growth copywriter writing as {} ({}). "
                            "Tone: {}.\n"
                            "Demand surge: '{}' +{:.0f}%.\n"
                            "Write: email_subject (max 70 chars), email_body (2 paras, uses {{first_name}} {{company}}), "
                            "whatsapp_body (max 280 chars, conversational, ends with question, uses {{first_name}}).\n"
                            "Return JSON: {{email_subject, email_body, whatsapp_body}}"
                        ).format(business_name, category, brand_tone, surge_term, pct_change)
                        r = await gemini.generate_reasoning(prompt=prompt, thinking_level="FAST")
                        if r and isinstance(r, dict) and r.get("email_subject"):
                            email_subject = r["email_subject"]
                            email_body = r["email_body"]
                            whatsapp_body = r["whatsapp_body"]
                except Exception:
                    pass  # fall back to templates above

                # Store as a pending AutoQueuedLoop in OrganismActivity
                # The Next.js execution-hub action reads these via the FastAPI /growth-loop/auto-queued endpoint
                _log_activity(
                    db,
                    action=f"[AUTO] Growth Loop Queued: {surge_term} +{pct_change:.0f}%",
                    detail=(
                        f"Business: {business_name} | Category: {category} | "
                        f"Email subject: '{email_subject[:60]}...' | "
                        f"WhatsApp ready. Status: pending_review. "
                        f"Visit Execution Hub to dispatch."
                    ),
                    impact=f"Auto-queued surge campaign for {business_name}",
                    business=biz,
                )

                queued += 1

                # Also signal via the growth_loop router to write a real pending record
                try:
                    import httpx
                    async with httpx.AsyncClient(timeout=8.0) as client:
                        await client.post(
                            "http://localhost:8002/growth-loop/auto-enqueue",
                            json={
                                "business_id": biz.id,
                                "surge_term": surge_term,
                                "pct_change": pct_change,
                                "category": category,
                                "email_subject": email_subject,
                                "email_body": email_body,
                                "whatsapp_body": whatsapp_body,
                                "source": "organism_auto",
                            }
                        )
                except Exception as e:
                    logger.warning(f"[AUTO_QUEUE] Could not POST to growth-loop router: {e}")

            except Exception as e:
                logger.error(f"[AUTO_QUEUE] Failed to queue for biz {biz.id}: {e}")

        logger.info(f"[AUTO_QUEUE] Autonomous Growth Loop queued for {queued} businesses | surge: {surge_term} +{pct_change:.0f}%")
        return queued

    except Exception as e:
        logger.error(f"[AUTO_QUEUE] Trigger failed: {e}")
        return 0
'''

with open(r'organism\growth_loop_trigger.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(TRIGGER_PY.lstrip())
print('growth_loop_trigger.py written')
