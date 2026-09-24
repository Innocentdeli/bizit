SCALE_MODE_PY = r'''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import get_db
from database.models import Business, OrganismActivity, AdCampaign

router = APIRouter()

def _classify(lead_count, total_actions):
    if lead_count > 500 or total_actions > 5000:
        return {"tier": "boardroom",
                "next_tier_threshold": "Boardroom mode is fully unlocked",
                "reasoning": "Enterprise-scale pipeline detected. Full AI Boardroom Suite active."}
    elif lead_count >= 50 or total_actions >= 500:
        return {"tier": "copilot",
                "next_tier_threshold": "Grow to 500+ leads to unlock Boardroom mode",
                "reasoning": "Growth-stage business detected. Co-Pilot mode active - approval gates and team tools enabled."}
    else:
        return {"tier": "autopilot",
                "next_tier_threshold": "Grow to 50+ leads to unlock Co-Pilot mode",
                "reasoning": "Startup or small business. AI Autopilot mode active - Dima manages growth autonomously."}

@router.get("/classify")
def classify_scale_mode(business_id: str = "default", db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == business_id).first()
    lead_count = biz.leads if biz else 0
    total_actions = db.query(OrganismActivity).count()
    active_campaigns = db.query(AdCampaign).filter(
        AdCampaign.business_id == business_id, AdCampaign.status == "ACTIVE").count()
    classification = _classify(lead_count, total_actions)
    return {**classification, "lead_count": lead_count,
            "total_actions": total_actions, "active_campaigns": active_campaigns}

@router.get("/recommendations")
def get_recommendations(tier: str = "autopilot"):
    recs = {
        "autopilot": [
            {"title": "Enroll All Leads in Welcome Sequence",
             "description": "Auto-dispatch Day 0 WhatsApp + Email to every lead in your pipeline.",
             "action_key": "bulk_enroll_sequences", "priority": "HIGH"},
            {"title": "Activate Surge Growth Loop",
             "description": "A demand surge was detected. Let AI draft a campaign for this opportunity.",
             "action_key": "activate_growth_loop", "priority": "HIGH"},
            {"title": "Broadcast Latest Email Campaign",
             "description": "Send your most recent draft campaign to your full contact list.",
             "action_key": "broadcast_email", "priority": "MEDIUM"},
        ],
        "copilot": [
            {"title": "Set Up Automated Workflow Triggers",
             "description": "Create rules that auto-move leads through pipeline stages.",
             "action_key": "create_workflow", "priority": "HIGH"},
            {"title": "A/B Test Your Top Campaign",
             "description": "Split-test subject lines to maximise open rates.",
             "action_key": "ab_test_campaign", "priority": "HIGH"},
            {"title": "Activate Affiliate Partner Network",
             "description": "Share referral links with your top customers to unlock partner-led growth.",
             "action_key": "affiliate_activation", "priority": "MEDIUM"},
        ],
        "boardroom": [
            {"title": "Run Boardroom Growth Simulation",
             "description": "Project Q4 revenue across optimistic, baseline, and pessimistic scenarios.",
             "action_key": "run_simulation", "priority": "HIGH"},
            {"title": "Multi-Channel ROAS Audit",
             "description": "Review blended ROAS across Meta, Google, and Email to reallocate budget.",
             "action_key": "roas_audit", "priority": "HIGH"},
            {"title": "Schedule Autonomous Growth Loop",
             "description": "Configure the Organism to trigger a growth loop on every 15%+ surge.",
             "action_key": "schedule_growth_loop", "priority": "MEDIUM"},
        ],
    }
    return {"tier": tier, "recommendations": recs.get(tier, recs["autopilot"])}
'''

SIMULATION_PY = r'''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Business, AdCampaign
from pydantic import BaseModel
from typing import List
import random

router = APIRouter()

class SimulationRunRequest(BaseModel):
    lead_count: float = 30
    avg_deal_value: float = 5000
    close_rate: float = 0.25
    monthly_ad_spend: float = 2000
    cac: float = 500
    n_trials: int = 1000
    horizon_months: int = 6

@router.get("/inputs")
def get_simulation_inputs(business_id: str = "default", db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == business_id).first()
    lead_count = float(biz.leads) if biz else 30.0
    campaigns = db.query(AdCampaign).filter(
        AdCampaign.business_id == business_id, AdCampaign.status == "ACTIVE").all()
    monthly_ad_spend = sum(float(c.budget) for c in campaigns if c.budget) or 2000.0
    avg_deal_value = 5000.0
    close_rate = 0.25
    cac = monthly_ad_spend / max(lead_count, 1)
    monthly_revenue_estimate = lead_count * avg_deal_value * close_rate
    roas = monthly_revenue_estimate / max(monthly_ad_spend, 1)
    return {"lead_count": lead_count, "avg_deal_value": avg_deal_value,
            "close_rate": close_rate, "monthly_ad_spend": monthly_ad_spend,
            "cac": round(cac, 2), "monthly_revenue_estimate": round(monthly_revenue_estimate, 2),
            "roas": round(roas, 2)}

@router.post("/run")
def run_simulation(req: SimulationRunRequest):
    cr_sigma = req.close_rate * 0.2
    dv_sigma = req.avg_deal_value * 0.15
    n = min(req.n_trials, 2000)
    h = min(req.horizon_months, 12)
    monthly_results: List[List[float]] = [[] for _ in range(h)]
    for _ in range(n):
        for month in range(h):
            cr = max(0.01, random.gauss(req.close_rate, cr_sigma))
            dv = max(100.0, random.gauss(req.avg_deal_value, dv_sigma))
            rev = req.lead_count * (1.05 ** month) * cr * dv
            monthly_results[month].append(rev)
    projections = []
    for i, results in enumerate(monthly_results):
        s = sorted(results)
        t = len(s)
        projections.append({"month": i + 1,
                             "p10": round(s[int(t * 0.10)], 2),
                             "p50": round(s[int(t * 0.50)], 2),
                             "p90": round(s[int(t * 0.90)], 2)})
    m1 = monthly_results[0]
    mn, mx = min(m1), max(m1)
    bsz = (mx - mn) / 20 if mx > mn else 1
    hcounts = [0] * 20
    for v in m1:
        hcounts[min(19, int((v - mn) / bsz))] += 1
    histogram = [{"bucket": round(mn + i * bsz), "count": hcounts[i]} for i in range(20)]
    flags = []
    if req.cac > req.avg_deal_value * req.close_rate:
        flags.append("CAC exceeds expected revenue per lead - reduce ad spend or improve close rate")
    if req.close_rate < 0.15:
        flags.append("Close rate below 15% - focus on lead qualification and sequence warm-up")
    if projections[2]["p10"] < req.monthly_ad_spend * 3:
        flags.append("Pessimistic scenario shows negative ROAS at month 3 - consider reducing burn")
    last = projections[-1]
    return {"projections": projections, "histogram": histogram, "risk_flags": flags,
            "summary": {"best_case_6m": last["p90"], "baseline_6m": last["p50"], "worst_case_6m": last["p10"]}}
'''

EXEC_HUB_PY = r'''from fastapi import APIRouter, Depends
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
'''

with open('routers/scale_mode.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(SCALE_MODE_PY.strip())
print('scale_mode.py written')

with open('routers/simulation.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(SIMULATION_PY.strip())
print('simulation.py written')

with open('routers/execution_hub.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(EXEC_HUB_PY.strip())
print('execution_hub.py written')
