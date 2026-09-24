from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Business
from pydantic import BaseModel
from typing import Optional
import re

router = APIRouter()

class BrandSyncRequest(BaseModel):
    business_id: str
    business_name: str
    category: Optional[str] = "SaaS"
    tagline: Optional[str] = ""
    brand_tone: Optional[str] = "Authoritative"
    value_proposition: Optional[str] = ""
    sender_email: Optional[str] = ""
    sender_name: Optional[str] = ""
    primary_color: Optional[str] = "#2563eb"
    logo_url: Optional[str] = ""

class GenerateCopyRequest(BaseModel):
    business_id: str
    channel: str
    trigger_term: str
    urgency_pct: float
    context: Optional[str] = ""

@router.post("/sync")
def sync_brand(req: BrandSyncRequest, db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == req.business_id).first()
    if biz:
        biz.name = req.business_name
        biz.category = req.category or biz.category
        if req.value_proposition:
            biz.description = req.value_proposition
        if req.sender_email:
            biz.contact_email = req.sender_email
    else:
        biz = Business(
            id=req.business_id, name=req.business_name,
            category=req.category or "SaaS", location="Global",
            description=req.value_proposition or "",
            contact_email=req.sender_email or "",
            verified=True, rating=5.0, review_count=0,
            profile_views=0, search_appearances=0, leads=0,
            visibility_boost=1.0, subscription_tier="pro",
        )
        db.add(biz)
    biz.ai_agent_prompt = "TONE:{}|TAGLINE:{}|COLOR:{}|SENDER:{}".format(
        req.brand_tone, req.tagline, req.primary_color, req.sender_name)
    biz.ai_agent_enabled = True
    db.commit()
    return {"status": "synced", "business_id": req.business_id}

@router.get("/profile")
def get_brand_profile(business_id: str, db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == business_id).first()
    if not biz:
        return {
            "business_name": "My Business", "category": "SaaS",
            "brand_tone": "Authoritative", "value_proposition": "",
            "sender_email": "",
            "prompt_injection": "You are writing as My Business. Keep output professional.",
        }
    brand_tone = "Authoritative"
    if biz.ai_agent_prompt:
        m = re.search(r"TONE:([^|]+)", biz.ai_agent_prompt)
        if m:
            brand_tone = m.group(1)
    prompt_injection = (
        "You are writing as {}, a {} company. "
        "Core value: {}. Tone: {}. Keep all output aligned with this brand.".format(
            biz.name, biz.category,
            biz.description or "delivering exceptional growth results",
            brand_tone
        )
    )
    return {
        "business_name": biz.name, "category": biz.category, "brand_tone": brand_tone,
        "value_proposition": biz.description or "", "sender_email": biz.contact_email or "",
        "prompt_injection": prompt_injection,
    }

@router.post("/generate-copy")
async def generate_copy(req: GenerateCopyRequest, db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == req.business_id).first()
    business_name = biz.name if biz else "My Business"
    value_prop = biz.description if biz else ""
    brand_tone = "Authoritative"
    if biz and biz.ai_agent_prompt:
        m = re.search(r"TONE:([^|]+)", biz.ai_agent_prompt)
        if m:
            brand_tone = m.group(1)

    subject_line = email_body = message_body = None
    ai_success = False
    try:
        from cognitive_kernel.gemini_client import GeminiClient
        gemini = GeminiClient(model_name="gemini-2.5-flash")
        if gemini.api_key:
            if req.channel == "email":
                prompt = (
                    "Write as {}. Tone: {}. Surge: {} +{:.0f}%. "
                    "Return JSON with subject_line and email_body (use {{first_name}}, {{company}}).".format(
                        business_name, brand_tone, req.trigger_term, req.urgency_pct))
            else:
                prompt = (
                    "Write WhatsApp msg as {}, max 280 chars, ends with question, uses {{first_name}}. "
                    "Surge: {} +{:.0f}%. JSON: {{\"message_body\": \"...\"}}".format(
                        business_name, req.trigger_term, req.urgency_pct))
            r = await gemini.generate_reasoning(prompt=prompt, thinking_level="FAST")
            if r and isinstance(r, dict):
                if req.channel == "email" and r.get("subject_line") and r.get("email_body"):
                    subject_line, email_body, ai_success = r["subject_line"], r["email_body"], True
                elif req.channel == "whatsapp" and r.get("message_body"):
                    message_body, ai_success = r["message_body"], True
    except Exception as e:
        print("[BRAND_COPY] {}".format(e))

    if not ai_success:
        if req.channel == "email":
            subject_line = "{}: {} demand up +{:.0f}% - act now".format(
                business_name, req.trigger_term, req.urgency_pct)
            email_body = (
                "Hi {first_name},\n\n"
                "Our market intelligence detected a {} surge (+{:.0f}% this week).\n\n"
                "{} is positioned to help {{company}} capitalise on this window.\n\n"
                "{}\n\n"
                "Best regards,\n{} Growth Team"
            ).format(
                req.trigger_term, req.urgency_pct, business_name,
                ("Our advantage: " + value_prop) if value_prop else "Reply to activate your growth strategy.",
                business_name
            )
        else:
            message_body = (
                "Hi {{first_name}} {} here. "
                "Spotted a {} surge (+{:.0f}% this week). "
                "Strong window for {{company}} - want the full breakdown? Reply YES."
            ).format(business_name, req.trigger_term, req.urgency_pct)

    return {
        "channel": req.channel, "subject_line": subject_line,
        "email_body": email_body, "message_body": message_body,
        "brand_name": business_name,
    }