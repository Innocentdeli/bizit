from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.database import get_db
from database.models import Business, OrganismActivity
from pydantic import BaseModel
from typing import Optional
import time, uuid, re

router = APIRouter()

class OrchestrateRequest(BaseModel):
    business_id: str
    surge_id: Optional[str] = None
    surge_term: str
    pct_change: float
    category: Optional[str] = "General"

def _log(db, business_id, action, detail, impact=None):
    db.add(OrganismActivity(
        timestamp=time.time(), cycle="GROWTH_LOOP",
        business_id=business_id, business_name=None,
        action=action, detail=detail, impact=impact,
        status="DONE", autonomous=False,
    ))
    db.commit()

@router.post("/orchestrate")
async def orchestrate_growth_loop(req: OrchestrateRequest, db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == req.business_id).first()
    business_name = biz.name if biz else "My Business"
    value_prop = biz.description if biz else ""
    category = (biz.category if biz else None) or req.category or "General"
    brand_tone = "Authoritative"
    if biz and biz.ai_agent_prompt:
        m = re.search(r"TONE:([^|]+)", biz.ai_agent_prompt)
        if m:
            brand_tone = m.group(1)

    email_subject = "{}: {} demand up +{:.0f}% - act now".format(
        business_name, req.surge_term, req.pct_change)
    email_body = (
        "Hi {first_name},\n\n"
        "Our market intelligence detected a {} surge (+{:.0f}% this week).\n\n"
        "As a client of {}, this is a high-signal window for {company} before the market reacts.\n\n"
        "{}\n\n"
        "Reply or click below to activate your personalised growth strategy.\n\n"
        "Best regards,\n{} Growth Team"
    ).format(
        req.surge_term, req.pct_change, business_name,
        ("Our advantage: " + value_prop) if value_prop else "We are positioned to help you capture this demand.",
        business_name
    )
    whatsapp_body = (
        "Hi {first_name} " + business_name + " here. "
        "Spotted a {} surge (+{:.0f}% this week). "
        "Strong opportunity for {company} - want the breakdown? Reply YES."
    ).format(req.surge_term, req.pct_change)

    try:
        from cognitive_kernel.gemini_client import GeminiClient
        gemini = GeminiClient(model_name="gemini-2.5-flash")
        if gemini.api_key:
            prompt = (
                "You are a growth copywriter writing as {} ({}). "
                "Tone: {}. Value prop: {}.\n"
                "Demand surge: '{}' +{:.0f}%.\n"
                "Write email_subject (max 70 chars), email_body (3 paras, uses {{first_name}} {{company}}, CTA), "
                "and whatsapp_body (max 280 chars, conversational, ends with question, uses {{first_name}}).\n"
                "Return JSON with keys: email_subject, email_body, whatsapp_body"
            ).format(business_name, category, brand_tone,
                     value_prop or "exceptional growth results",
                     req.surge_term, req.pct_change)
            r = await gemini.generate_reasoning(prompt=prompt, thinking_level="FAST")
            if r and isinstance(r, dict):
                if r.get("email_subject") and r.get("email_body") and r.get("whatsapp_body"):
                    email_subject = r["email_subject"]
                    email_body = r["email_body"]
                    whatsapp_body = r["whatsapp_body"]
    except Exception as e:
        print("[GROWTH_LOOP] Gemini error: {}".format(e))

    run_id = "loop_{}".format(uuid.uuid4().hex[:12])
    _log(db, req.business_id,
         "Growth Loop: {} +{:.0f}%".format(req.surge_term, req.pct_change),
         "Email + WhatsApp copy drafted for {} surge.".format(req.surge_term),
         "2 channel drafts generated for {}".format(business_name))

    return {
        "run_id": run_id,
        "surge_term": req.surge_term,
        "pct_change": req.pct_change,
        "email_subject": email_subject,
        "email_body": email_body,
        "whatsapp_body": whatsapp_body,
        "recommended_audience": "all_contacts",
        "status": "ready_for_dispatch",
    }

@router.get("/history")
def get_history(business_id: str, limit: int = 20, db: Session = Depends(get_db)):
    rows = (db.query(OrganismActivity)
            .filter(OrganismActivity.cycle == "GROWTH_LOOP")
            .order_by(desc(OrganismActivity.timestamp))
            .limit(limit).all())
    return {"count": len(rows), "runs": [
        {"id": a.id, "timestamp": a.timestamp, "action": a.action,
         "detail": a.detail, "impact": a.impact, "status": a.status}
        for a in rows
    ]}

# ?? AUTO-ENQUEUE (called by Organism worker autonomously) ?????????????????????

class AutoEnqueueRequest(BaseModel):
    business_id: str
    surge_term: str
    pct_change: float
    category: Optional[str] = "General"
    email_subject: str = ""
    email_body: str = ""
    whatsapp_body: str = ""
    source: str = "organism_auto"

@router.post("/auto-enqueue")
def auto_enqueue_growth_loop(req: AutoEnqueueRequest, db: Session = Depends(get_db)):
    """
    Called internally by the Organism when it autonomously detects a surge.
    Writes a GROWTH_LOOP activity with status=pending_review so the Execution Hub
    can surface it as a 1-click dispatch item ? no user action required to get here.
    """
    biz = db.query(Business).filter(Business.id == req.business_id).first()
    business_name = biz.name if biz else "Business"

    run_id = "auto_{}".format(uuid.uuid4().hex[:10])
    db.add(OrganismActivity(
        timestamp=time.time(),
        cycle="GROWTH_LOOP",
        business_id=req.business_id,
        business_name=business_name,
        action="[AUTO] Growth Loop Ready: {} +{:.0f}%".format(req.surge_term, req.pct_change),
        detail=(
            "Category: {} | Email: '{}' | WhatsApp drafted. "
            "Source: Organism autonomous trigger. Status: pending_review. "
            "Run ID: {}".format(req.category, req.email_subject[:60], run_id)
        ),
        impact="Auto-queued for {}: {} surge campaign".format(business_name, req.surge_term),
        status="pending_review",
        autonomous=True,
    ))
    db.commit()
    return {"run_id": run_id, "status": "pending_review", "business": business_name}


@router.get("/auto-queue-status")
def get_auto_queue_status(db: Session = Depends(get_db)):
    """
    Returns the count of autonomously queued growth loops pending dispatch.
    Used by the Execution Hub badge to show real-time pending count.
    """
    pending = (db.query(OrganismActivity)
               .filter(
                   OrganismActivity.cycle == "GROWTH_LOOP",
                   OrganismActivity.status == "pending_review"
               )
               .order_by(desc(OrganismActivity.timestamp))
               .limit(50)
               .all())

    return {
        "pending_count": len(pending),
        "items": [
            {
                "id": a.id,
                "timestamp": a.timestamp,
                "action": a.action,
                "detail": a.detail,
                "impact": a.impact,
                "business_name": a.business_name,
            }
            for a in pending
        ]
    }
