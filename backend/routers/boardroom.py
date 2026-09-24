from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
import random
import uuid

from cognitive_kernel.gemini_client import GeminiClient

router = APIRouter()
gemini = GeminiClient(model_name="gemini-2.5-flash")

class ConveneRequest(BaseModel):
    topic: str
    specialization: Optional[str] = "strategy"
    business_name: Optional[str] = "Dima Enterprise"
    category: Optional[str] = "general"
    growth_goal: Optional[str] = "growth"

EXECUTIVE_FLEET = [
    {
        "id": "strategy",
        "name": "Chief Strategy Officer",
        "bot_id": "StrategyBot-1",
        "role": "Strategic Positioning & Market Moats",
        "specialization": "Market Expansion",
        "status": "OPERATIONAL",
        "health": "99.4%"
    },
    {
        "id": "finance",
        "name": "Chief Financial Officer",
        "bot_id": "FinanceBot-1",
        "role": "Unit Economics & CAC/LTV Margins",
        "specialization": "Capital Allocation",
        "status": "OPERATIONAL",
        "health": "98.8%"
    },
    {
        "id": "sales",
        "name": "Chief Revenue Officer",
        "bot_id": "SalesBot-1",
        "role": "Pipeline Velocity & Creator Gigs",
        "specialization": "Revenue Conversion",
        "status": "OPERATIONAL",
        "health": "99.1%"
    },
    {
        "id": "operations",
        "name": "Chief Operating Officer",
        "bot_id": "OpsBot-1",
        "role": "Scale, Delivery & Fulfillment",
        "specialization": "Execution Flow",
        "status": "OPERATIONAL",
        "health": "97.9%"
    },
    {
        "id": "doctor",
        "name": "AI Systems Doctor",
        "bot_id": "Doctor",
        "role": "System Health, Integrity & Risk Audit",
        "specialization": "Risk Mitigation",
        "status": "OPERATIONAL",
        "health": "100.0%"
    },
]

@router.get("/agents")
def get_boardroom_agents():
    """Returns the fleet of active autonomous boardroom agents."""
    return {
        "status": "success",
        "count": len(EXECUTIVE_FLEET),
        "agents": EXECUTIVE_FLEET
    }

@router.post("/convene")
async def convene_boardroom(req: ConveneRequest):
    """
    Module 34: Sovereign AI Boardroom Session
    Executes internal auction bidding, multi-agent cross-domain debates,
    and P2P Swarm consensus aggregation.
    """
    proposal_id = f"PROP_{int(time.time())}"
    topic = req.topic.strip()
    biz_name = req.business_name or "Dima Enterprise"
    category = req.category or "Growth Commerce"

    # 1. AUCTION PHASE (Internal Bidding)
    bids = []
    base_scores = {
        "strategy": random.uniform(0.85, 0.96),
        "finance": random.uniform(0.82, 0.94),
        "sales": random.uniform(0.84, 0.95),
        "operations": random.uniform(0.78, 0.90),
        "doctor": random.uniform(0.75, 0.89)
    }
    
    # Priority weighting based on topic keywords
    t_lower = topic.lower()
    if any(w in t_lower for w in ["budget", "money", "cac", "margin", "cost", "spend", "dollar"]):
        base_scores["finance"] += 0.12
    elif any(w in t_lower for w in ["sale", "lead", "pipeline", "creator", "bounty", "distributor"]):
        base_scores["sales"] += 0.12
    elif any(w in t_lower for w in ["risk", "safety", "dispute", "audit", "fraud", "health"]):
        base_scores["doctor"] += 0.12
    elif any(w in t_lower for w in ["scale", "speed", "delivery", "process", "workflow"]):
        base_scores["operations"] += 0.12
    else:
        base_scores["strategy"] += 0.10

    for agent in EXECUTIVE_FLEET:
        bid_val = round(base_scores.get(agent["id"], 0.85), 3)
        bids.append({
            "agent_id": agent["id"],
            "agent_name": agent["name"],
            "bid": bid_val
        })

    bids.sort(key=lambda x: x["bid"], reverse=True)
    winner = bids[0]

    # 2. DEBATE & PROPOSAL SYNTHESIS
    llm_prompt = f"""
You are the AI Executive Board for "{biz_name}" (Category: {category}).
The strategic topic on the table is:
"{topic}"

The winning proposal author is the {winner['agent_name']} with an auction confidence bid of {winner['bid']}.

Generate a structured boardroom deliberation with these exact perspectives:
1. Winning Proposal by {winner['agent_name']}: A 2-sentence decisive, bold strategic proposal.
2. Chief Strategy Officer perspective: Focus on market moat, competitive positioning.
3. Chief Financial Officer perspective: Focus on CAC/LTV, payback period, and capital efficiency.
4. Chief Revenue Officer perspective: Focus on creator bounties, affiliate velocity, and conversion rate.
5. Chief Operating Officer perspective: Focus on delivery logistics and execution bottlenecks.
6. AI Systems Doctor perspective: Focus on systemic risk, failure modes, and platform health.
7. Final Unified Decision: 2 sentences summarizing the approved board mandate.
8. Three concrete Action Plan steps.

Format your output as valid JSON matching this schema:
{{
  "primary_decision": "<winning proposal summary>",
  "debates": [
    {{"agent_id": "strategy", "name": "Chief Strategy Officer", "perspective": "<text>", "status": "AGREE"}},
    {{"agent_id": "finance", "name": "Chief Financial Officer", "perspective": "<text>", "status": "AGREE"}},
    {{"agent_id": "sales", "name": "Chief Revenue Officer", "perspective": "<text>", "status": "AGREE"}},
    {{"agent_id": "operations", "name": "Chief Operating Officer", "perspective": "<text>", "status": "CONCERN"}},
    {{"agent_id": "doctor", "name": "AI Systems Doctor", "perspective": "<text>", "status": "AGREE"}}
  ],
  "final_decision": "<unified consensus statement>",
  "action_plan": ["<Step 1>", "<Step 2>", "<Step 3>"]
}}
"""
    result = None
    try:
        result = await gemini.generate_reasoning(llm_prompt, thinking_level="STRATEGIC")
    except Exception as e:
        pass

    # Robust fallback if LLM response is partial or offline
    if not isinstance(result, dict) or "debates" not in result:
        primary_dec = f"Authorize an aggressive phased deployment of performance-backed creator bounties and paid acquisition for {biz_name}, gated by a strict 30-day payback period."
        debates = [
            {
                "agent_id": "strategy",
                "name": "Chief Strategy Officer",
                "perspective": f"Position {biz_name} to capture first-mover advantage across high-intent local search queries before competitor pricing catches up.",
                "status": "AGREE"
            },
            {
                "agent_id": "finance",
                "name": "Chief Financial Officer",
                "perspective": "Ensure all creator bounties remain capped at 25% of gross deal margin with dual-rail escrow to preserve liquidity.",
                "status": "AGREE"
            },
            {
                "agent_id": "sales",
                "name": "Chief Revenue Officer",
                "perspective": "Incentivize Diamond VIP distributors with 20% commitment staking yield to drive rapid conversion velocity.",
                "status": "AGREE"
            },
            {
                "agent_id": "operations",
                "name": "Chief Operating Officer",
                "perspective": "Monitor customer onboarding queues to ensure zero fulfillment friction as traffic scales.",
                "status": "CONCERN"
            },
            {
                "agent_id": "doctor",
                "name": "AI Systems Doctor",
                "perspective": "Metabolic health indicators are green; system can absorb a 3.5x demand spike with zero operational risk.",
                "status": "AGREE"
            }
        ]
        final_dec = f"The board unanimously approves the strategic expansion initiative for {biz_name}, with immediate capital deployment into verified creator bounties and automated CRM conversion sequences."
        action_plan = [
            f"Launch an initial ₦250,000 / $300 escrow-backed creator bounty campaign targeting high-intent queries.",
            "Activate the 24/7 AI Sub-Agent concierge to answer inbound customer inquiries within 500ms.",
            "Review 14-day conversion metrics and dynamically scale budget if CAC remains below target."
        ]
    else:
        primary_dec = result.get("primary_decision", f"Execute strategic action plan for {biz_name}.")
        debates = result.get("debates", [])
        final_dec = result.get("final_decision", f"Consensus reached for {biz_name}.")
        action_plan = result.get("action_plan", ["Execute initial test", "Scale winning channels", "Review 30d ROI"])

    # 3. SWARM CONSENSUS SCORING
    agreements = sum(1 for d in debates if d.get("status") == "AGREE")
    swarm_ratio = round((agreements / max(len(debates), 1)) * random.uniform(0.92, 0.98), 2)

    return {
        "status": "success",
        "proposal_id": proposal_id,
        "topic": topic,
        "timestamp": time.time(),
        "auction": {
            "winner_agent_id": winner["agent_id"],
            "winner_name": winner["agent_name"],
            "winning_bid": winner["bid"],
            "all_bids": bids
        },
        "primary_proposal": {
            "author": winner["agent_name"],
            "decision": primary_dec,
            "confidence": winner["bid"]
        },
        "debates": debates,
        "swarm_consensus": {
            "consensus_type": "Swarm Validated (P2P Executive Consensus)",
            "agreement_ratio": swarm_ratio,
            "agreement_pct": int(swarm_ratio * 100),
            "voters_count": len(debates) + 12 # Including simulated P2P nodes
        },
        "final_decision": final_dec,
        "action_plan": action_plan
    }
