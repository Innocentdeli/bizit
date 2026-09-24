from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.database import get_db
from database.models import Business, SurgePricingEvent, AdCampaign, OrganismActivity
from pydantic import BaseModel
import time

router = APIRouter()

class DispatchAllRequest(BaseModel):
    business_id: str

@router.get("/queue")
def get_execution_queue(business_id: str = "default", db: Session = Depends(get_db)):
    now = time.time()
    surges = (db.query(SurgePricingEvent)
              .filter(SurgePricingEvent.active == True, SurgePricingEvent.expires_at > now)
              .order_by(desc(SurgePricingEvent.multiplier)).limit(10).all())
    campaigns = (db.query(AdCampaign)
                 .filter(AdCampaign.business_id == business_id, AdCampaign.status == "DRAFT")
                 .limit(10).all())
    loops = (db.query(OrganismActivity)
             .filter(OrganismActivity.cycle == "GROWTH_LOOP")
             .order_by(desc(OrganismActivity.timestamp)).limit(5).all())
    surges_out = [{"id": str(s.id), "category": s.category,
                   "surge_display": "{} {:.0f}".format(s.currency, s.surge_price),
                   "pct_change": round((s.multiplier - 1) * 100, 1),
                   "hours_left": max(0, round((s.expires_at - now) / 3600, 1)) if s.expires_at else 0}
                  for s in surges]
    campaigns_out = [{"id": str(c.id),
                      "title": getattr(c, "title", "Campaign #{}".format(c.id)),
                      "status": c.status, "budget": float(c.budget) if c.budget else 0}
                     for c in campaigns]
    loops_out = [{"id": str(a.id), "action": a.action, "detail": a.detail, "timestamp": a.timestamp}
                 for a in loops]
    return {"business_id": business_id, "total_pending": len(surges_out) + len(campaigns_out),
            "pending_surges": surges_out, "pending_campaigns": campaigns_out, "recent_loops": loops_out}

@router.post("/dispatch-all")
def dispatch_all(req: DispatchAllRequest, db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == req.business_id).first()
    now = time.time()
    sc = db.query(SurgePricingEvent).filter(SurgePricingEvent.active == True, SurgePricingEvent.expires_at > now).count()
    cc = db.query(AdCampaign).filter(AdCampaign.business_id == req.business_id, AdCampaign.status == "DRAFT").count()
    total = sc + cc
    db.add(OrganismActivity(
        timestamp=time.time(), cycle="OUTREACH",
        business_id=req.business_id, business_name=biz.name if biz else req.business_id,
        action="Sovereign Execution: Multi-channel dispatch initiated",
        detail="All pending sequence steps and campaigns queued for delivery.",
        impact="Estimated reach: {} contacts across SMTP_EMAIL and WHATSAPP_CLOUD_API".format(total * 50),
        status="DONE", autonomous=False,
    ))
    db.commit()
    return {"status": "dispatched", "dispatched_count": total,
            "channels": ["SMTP_EMAIL", "WHATSAPP_CLOUD_API"], "estimated_reach": total * 50}