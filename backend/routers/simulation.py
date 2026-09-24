from fastapi import APIRouter, Depends
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


# ─────────────────────────────────────────────────────────────────────────────
# DIGITAL TWIN SHADOW STRESS-TESTER & ADVERSE CONDITIONS SIMULATOR
# ─────────────────────────────────────────────────────────────────────────────

class ShadowStressTestRequest(BaseModel):
    creator_drop_pct: int = 40        # -40% creator deliverable completion
    ad_cpc_multiplier: float = 1.8    # 1.8x CPC ad inflation shock
    churn_shock_pct: int = 25         # +25% monthly churn surge
    current_cash_reserve: float = 10000000.0 # ₦10,000,000 baseline
    monthly_burn_rate: float = 1200000.0     # ₦1,200,000 baseline
    monthly_gross_revenue: float = 2500000.0 # ₦2,500,000 baseline
    horizon_months: int = 6

@router.post("/shadow-stress-test")
def run_shadow_stress_test(req: ShadowStressTestRequest):
    """
    Module 24: Digital Twin Shadow Simulator & Adverse Shock Stress-Tester.
    Simulates survival runway, cash reserve depletion deltas, and synthesizes
    automated AI mitigation playbooks under extreme market conditions.
    """
    timeline = []
    cash = req.current_cash_reserve
    base_cash = req.current_cash_reserve
    
    # Shock factors
    creator_efficiency = max(0.1, 1.0 - (req.creator_drop_pct / 100.0))
    cpc_factor = max(1.0, req.ad_cpc_multiplier)
    churn_factor = 1.0 + (req.churn_shock_pct / 100.0)
    
    # Monthly burn expands due to ad inflation
    stressed_burn = req.monthly_burn_rate * (1.0 + (cpc_factor - 1.0) * 0.4)
    # Revenue contracts due to creator drops & churn
    stressed_rev = req.monthly_gross_revenue * creator_efficiency * (1.0 / churn_factor)
    
    runway_depleted_month = None

    for m in range(1, req.horizon_months + 1):
        # Baseline projection (no shock)
        base_net = (req.monthly_gross_revenue * (1.04 ** m)) - req.monthly_burn_rate
        base_cash += base_net
        
        # Stressed projection
        stressed_net = stressed_rev - stressed_burn
        cash += stressed_net
        
        if cash <= 0 and runway_depleted_month is None:
            runway_depleted_month = m
            cash = 0.0

        risk_level = "CRITICAL" if cash < (req.monthly_burn_rate * 2) else "ELEVATED" if cash < (req.monthly_burn_rate * 4) else "STABLE"

        timeline.append({
            "month": m,
            "stressed_cash_reserve": round(max(0.0, cash), 2),
            "baseline_cash_reserve": round(base_cash, 2),
            "net_monthly_delta": round(stressed_net, 2),
            "risk_level": risk_level
        })

    cash_reserve_delta = round(cash - base_cash, 2)
    
    # Calculate survival runway in months
    net_burn_rate = max(100.0, stressed_burn - stressed_rev)
    runway_months = round(req.current_cash_reserve / net_burn_rate, 1) if net_burn_rate > 0 else 99.0
    
    # Systemic risk score (0-100)
    risk_score = min(100, int((req.creator_drop_pct * 0.35) + ((cpc_factor - 1.0) * 30) + (req.churn_shock_pct * 0.35)))

    # Actionable AI mitigation playbooks
    mitigation_playbooks = [
        {
            "priority": "P0_IMMEDIATE",
            "title": "Enforce High-Ticket Staking Protocol",
            "impact": "+35% Deliverable Reliability",
            "description": "Lock 20% collateral on creator bounties to completely eliminate ghost claims and low-effort submissions under creator supply shortages."
        },
        {
            "priority": "P1_URGENT",
            "title": "Pivot Budget to Viral Video Bounties",
            "impact": "-48% Effective Customer Acquisition Cost",
            "description": "Reallocate 65% of inflated paid CPC ad spend into organic 9:16 vertical video clipping bounties on TikTok and Reels."
        },
        {
            "priority": "P2_STABILIZATION",
            "title": "Activate 24/7 AI Sub-Agent Lead Interceptor",
            "impact": "+22% Inbound Lead-to-Close Rate",
            "description": "Deploy the autonomous AI concierge to intercept after-hours inquiries and recover checkout abandonment before customers churn."
        }
    ]

    return {
        "status": "success",
        "systemic_risk_score": risk_score,
        "risk_classification": "CRITICAL RISK" if risk_score > 65 else "ELEVATED RISK" if risk_score > 35 else "MANAGED RISK",
        "survival_runway_months": runway_months,
        "cash_reserve_delta": cash_reserve_delta,
        "timeline": timeline,
        "mitigation_playbooks": mitigation_playbooks
    }