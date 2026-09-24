from fastapi import APIRouter, Depends
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