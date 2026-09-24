
import time
import logging
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import OrganismActivity
from routers.marketing_network import MarketGoalDB, GoalAllocationDB

logger = logging.getLogger("organism.goal_reallocation")

def _log_activity(db: Session, action: str, detail: str, impact: str = None, business_id: str = None):
    activity = OrganismActivity(
        timestamp=time.time(),
        cycle="GOAL_REALLOCATION",
        business_id=business_id,
        business_name=None,
        action=action,
        detail=detail,
        impact=impact,
        status="DONE",
        autonomous=True,
    )
    db.add(activity)
    db.commit()

async def run_goal_reallocation_cycle():
    logger.info("[GOAL_REALLOCATION] Starting Cycle 10: Adaptive Capital & Channel Optimization...")
    db: Session = SessionLocal()
    try:
        active_goals = db.query(MarketGoalDB).filter(MarketGoalDB.status == "active").all()
        if not active_goals:
            logger.info("[GOAL_REALLOCATION] No active market goals found to optimize.")
            return {"status": "skipped", "message": "No active goals"}

        reallocations_checked = 0
        signals_triggered = 0

        for goal in active_goals:
            reallocations_checked += 1
            allocations = db.query(GoalAllocationDB).filter(
                GoalAllocationDB.goal_id == goal.id,
                GoalAllocationDB.status == "active"
            ).all()

            ceiling = goal.cac_ceiling if goal.cac_ceiling > 0 else 1.0
            paused_channels = []
            scaled_channels = []

            for alloc in allocations:
                if alloc.actual_cac <= 0:
                    continue
                
                # Critical underperformance (CAC > 1.5x ceiling with at least 3 conversions)
                if alloc.actual_cac > ceiling * 1.5 and alloc.conversions >= 3:
                    paused_channels.append(f"{alloc.channel_name} (CAC: {goal.budget_currency} {alloc.actual_cac:,.0f} vs ceiling {goal.budget_currency} {ceiling:,.0f})")
                    signals_triggered += 1

                # High performance (CAC < 0.7x ceiling with at least 5 conversions)
                elif alloc.actual_cac < ceiling * 0.7 and alloc.conversions >= 5:
                    scaled_channels.append(f"{alloc.channel_name} (CAC: {goal.budget_currency} {alloc.actual_cac:,.0f})")
                    signals_triggered += 1

            if paused_channels or scaled_channels:
                detail_parts = []
                if paused_channels:
                    detail_parts.append(f"Flagged for budget pause/reduction: {', '.join(paused_channels)}")
                if scaled_channels:
                    detail_parts.append(f"Recommended for budget expansion: {', '.join(scaled_channels)}")
                detail = " | ".join(detail_parts)

                _log_activity(
                    db,
                    action=f"Adaptive Reallocation: {goal.title}",
                    detail=detail,
                    impact=f"Acquired: {goal.acquired_count:,.0f}/{goal.target_value:,.0f} {goal.targetUnit if hasattr(goal, 'targetUnit') else goal.target_unit}",
                    business_id=goal.user_id,
                )
            else:
                _log_activity(
                    db,
                    action=f"Goal Surveillance Audit: {goal.title}",
                    detail=f"All {len(allocations)} active distribution channels operating within healthy CAC threshold.",
                    impact=f"Budget deployed: {goal.budget_currency} {goal.budget_spent:,.0f}/{goal.budget_total:,.0f}",
                    business_id=goal.user_id,
                )

        db.commit()
        logger.info(f"[GOAL_REALLOCATION] Cycle complete. Reviewed {reallocations_checked} goals, raised {signals_triggered} channel signals.")
        return {"status": "success", "goals_reviewed": reallocations_checked, "signals": signals_triggered}

    except Exception as e:
        logger.error(f"[GOAL_REALLOCATION] Cycle failed: {e}")
        db.rollback()
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()
