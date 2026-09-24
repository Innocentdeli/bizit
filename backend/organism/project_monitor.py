"""
Organism Cycle 11 — Autonomous Marketing Project Stage Monitor

Scans all active Marketing OS projects every cycle and:
  1. Flags projects stuck in a stage for > 72 hours with no progress
  2. Escalates stale Approval Gates pending for > 24 hours
  3. Marks completed projects where acquired_count >= target_count
  4. Auto-advances projects through RESOURCE -> CREATE stage when all gigs are assigned
  5. Auto-advances projects through CREATE -> APPROVE when all gigs are submitted
  6. In EXECUTE, autonomously schedules the field-marketing task and dispatches the
     retention email (if a recipient list is on file), then advances to MEASURE
  7. Fires any social/email channel dispatches whose scheduled_for time has passed
  8. Logs all actions to OrganismActivity
"""

import json
import logging
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database.database import SessionLocal
from database.models import OrganismActivity

logger = logging.getLogger("organism.cycle11")

STAGE_ORDER = ["GOAL", "ANALYZE", "STRATEGIZE", "PLAN", "RESOURCE", "CREATE", "APPROVE", "EXECUTE", "MEASURE", "OPTIMIZE"]
STAGE_TIMEOUT_HOURS = {
    "GOAL": 24, "ANALYZE": 24, "STRATEGIZE": 24,
    "PLAN": 48, "RESOURCE": 48, "CREATE": 72,
    "APPROVE": 24, "EXECUTE": 168, "MEASURE": 48, "OPTIMIZE": 72,
}


def _log_project_activity(db: Session, action: str, detail: str, project_title: str,
                           impact: str = "medium", autonomous: bool = True):
    """
    Persist an Organism activity record for a marketing_os project. Marketing OS
    projects aren't tied to a Business row, so business_id stays null and the
    project title is carried in business_name for display purposes.
    """
    activity = OrganismActivity(
        timestamp=time.time(),
        cycle="11",
        business_id=None,
        business_name=project_title,
        action=action,
        detail=detail,
        impact=impact,
        status="DONE",
        autonomous=autonomous,
    )
    db.add(activity)


def _parse_when(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


async def _run_execute_stage_actions(db: Session, project, project_title: str) -> int:
    """
    Once a project reaches EXECUTE, autonomously act on the channels that don't
    need a human trigger: schedule the field-marketing task, and dispatch the
    retention email if a recipient list has been provided. Idempotent — only
    fires once per channel per project.
    """
    from routers.marketing_os import ChannelDispatchDB, WorkforceTalentDB, RetentionRecipientDB, gemini
    from organism.mailer import send_transactional_email

    existing = db.query(ChannelDispatchDB).filter(ChannelDispatchDB.project_id == project.id).all()
    channels_seen = {d.channel for d in existing}
    actions = 0

    if "field_marketing" not in channels_seen:
        talent = db.query(WorkforceTalentDB).filter(WorkforceTalentDB.role.ilike("%Field%")).first()
        detail = (f"Auto-scheduled by Cycle 11 — assigned to {talent.name}." if talent
                   else "Auto-scheduled by Cycle 11 — no matching field/call talent found yet.")
        dispatch = ChannelDispatchDB(
            project_id=project.id, user_id=project.user_id, channel="field_marketing", action_type="call",
            assigned_talent_id=talent.id if talent else None,
            task_description=f"Kick off on-ground / phone outreach for '{project.title}'.",
            scheduled_for=(datetime.utcnow() + timedelta(days=1)).isoformat(),
            status="scheduled", detail=detail,
        )
        db.add(dispatch)
        db.flush()
        actions += 1
        _log_project_activity(db, "AUTO-SCHEDULED FIELD TASK", detail, project_title)

    if "email_sms_retention" not in channels_seen:
        recipients = db.query(RetentionRecipientDB).filter(
            RetentionRecipientDB.project_id == project.id,
            RetentionRecipientDB.contact_type == "email",
        ).all()
        if recipients:
            draft = await gemini.generate_reasoning(
                f"Write a short retention/reactivation marketing email for the project '{project.title}' "
                f"(objective: {project.objective_type}, target: {project.target_count} {project.target_unit}).\n\n"
                'Respond with JSON only: {"subject": "<string>", "body_html": "<string, simple inline-styled HTML>"}',
                system_instruction="You are the Dima Retention Copywriter. Write punchy, high-conversion email copy for a Nigerian SMB audience.",
                thinking_level="TACTICAL",
            )
            if "error" in draft or not draft.get("subject") or not draft.get("body_html"):
                subject, body_html = f"An update from {project.title}", "<p>We have an update for you.</p>"
            else:
                subject, body_html = draft["subject"], draft["body_html"]

            sent, failed = 0, 0
            for r in recipients:
                if send_transactional_email(r.contact, subject, body_html, from_name=project.title):
                    sent += 1
                else:
                    failed += 1
            status = "failed" if sent == 0 else ("partial_failure" if failed > 0 else "sent")
            dispatch = ChannelDispatchDB(
                project_id=project.id, user_id=project.user_id, channel="email_sms_retention", action_type="email",
                subject=subject, body=body_html, recipient_count=len(recipients),
                sent_count=sent, failed_count=failed, status=status,
                detail="Auto-dispatched by Cycle 11.",
            )
            db.add(dispatch)
            db.flush()
            actions += 1
            _log_project_activity(db, "AUTO-DISPATCHED RETENTION EMAIL",
                                   f"Sent to {sent}/{len(recipients)} recipients.", project_title)
        else:
            _log_project_activity(
                db, "EMAIL CHANNEL BLOCKED",
                "No retention recipient list on file — add contacts via "
                "POST /marketing-os/project/{id}/retention/recipients to enable autonomous email dispatch.",
                project_title, impact="low", autonomous=False,
            )

    return actions


async def _fire_due_scheduled_posts(db: Session) -> int:
    """Publishes (simulated — no external platform credentials exist) any social post whose scheduled_for time has passed."""
    from routers.marketing_os import ChannelDispatchDB

    now = datetime.utcnow()
    due = db.query(ChannelDispatchDB).filter(
        ChannelDispatchDB.channel == "social_media", ChannelDispatchDB.status == "scheduled"
    ).all()
    fired = 0
    for post in due:
        when = _parse_when(post.scheduled_for)
        if when and when <= now:
            post.status = "published_simulated"
            fired += 1
            _log_project_activity(
                db, "SCHEDULED POST FIRED",
                f"'{post.subject or 'Untitled post'}' was due at {post.scheduled_for} — marked published. "
                "No live platform (Meta/TikTok/etc.) is connected, so this is a simulated publish.",
                post.project_id, impact="low",
            )
    return fired


async def run_project_stage_monitor():
    db: Session = SessionLocal()
    actions_logged = 0
    try:
        from routers.marketing_os import MarketingProjectDB, WorkOrderGigDB, ApprovalGateDB

        now = datetime.utcnow()
        projects = db.query(MarketingProjectDB).filter(MarketingProjectDB.status == "active").all()

        for project in projects:
            project_title = project.title[:40] + "..." if len(project.title) > 40 else project.title

            # 1. Check if project is complete
            if project.acquired_count >= project.target_count and project.target_count > 0:
                project.status = "completed"
                project.current_stage = "OPTIMIZE"
                db.flush()
                _log_project_activity(db, "PROJECT COMPLETED",
                    f"Acquired {project.acquired_count}/{project.target_count} {project.target_unit}. Marking project complete.",
                    project_title, impact="high")
                actions_logged += 1
                continue

            # 2. Check if stuck in current stage
            updated = project.updated_at or project.created_at
            if updated:
                hours_in_stage = (now - updated).total_seconds() / 3600
                timeout = STAGE_TIMEOUT_HOURS.get(project.current_stage, 48)
                if hours_in_stage > timeout:
                    _log_project_activity(db, "STAGE STALL DETECTED",
                        f"Project has been in stage [{project.current_stage}] for {hours_in_stage:.0f}h "
                        f"(threshold: {timeout}h). Investigate or reassign resources.",
                        project_title, impact="medium", autonomous=False)
                    actions_logged += 1

            # 3. Auto-advance RESOURCE -> CREATE when all gigs are assigned
            if project.current_stage == "RESOURCE":
                gigs = db.query(WorkOrderGigDB).filter(WorkOrderGigDB.project_id == project.id).all()
                if gigs:
                    unassigned = [g for g in gigs if not g.assigned_talent_id and g.status == "open"]
                    if not unassigned:
                        project.current_stage = "CREATE"
                        db.flush()
                        _log_project_activity(db, "STAGE ADVANCED: RESOURCE -> CREATE",
                            f"All {len(gigs)} work order gigs are assigned. Project advanced to CREATE stage.",
                            project_title, impact="high")
                        actions_logged += 1

            # 4. Auto-advance CREATE -> APPROVE when all gigs are submitted
            if project.current_stage == "CREATE":
                gigs = db.query(WorkOrderGigDB).filter(WorkOrderGigDB.project_id == project.id).all()
                if gigs:
                    pending = [g for g in gigs if g.status not in ("ai_approved", "merchant_approved", "paid", "submitted")]
                    if not pending:
                        project.current_stage = "APPROVE"
                        db.flush()
                        _log_project_activity(db, "STAGE ADVANCED: CREATE -> APPROVE",
                            f"All {len(gigs)} deliverables have been submitted or AI-approved. Advancing to APPROVE stage.",
                            project_title, impact="high")
                        actions_logged += 1

            # 5. EXECUTE: autonomously act on the channels that don't need a human trigger
            if project.current_stage == "EXECUTE":
                acted = await _run_execute_stage_actions(db, project, project_title)
                actions_logged += acted
                from routers.marketing_os import ChannelDispatchDB
                channels_seen = {d.channel for d in db.query(ChannelDispatchDB).filter(
                    ChannelDispatchDB.project_id == project.id).all()}
                if {"field_marketing", "email_sms_retention"}.issubset(channels_seen):
                    project.current_stage = "MEASURE"
                    db.flush()
                    _log_project_activity(db, "STAGE ADVANCED: EXECUTE -> MEASURE",
                        "Field-marketing task scheduled and retention email dispatched. Moving to performance measurement.",
                        project_title, impact="high")
                    actions_logged += 1

            # 6. Flag stale Approval Gates
            gates = db.query(ApprovalGateDB).filter(
                ApprovalGateDB.project_id == project.id,
                ApprovalGateDB.status == "pending_merchant"
            ).all()
            for gate in gates:
                gate_age_hours = (now - gate.created_at).total_seconds() / 3600 if gate.created_at else 0
                if gate_age_hours > 24:
                    _log_project_activity(db, "APPROVAL GATE ESCALATION",
                        f"Gate '{gate.title[:50]}' has been pending for {gate_age_hours:.0f}h. "
                        f"Risk: {gate.risk_level.upper()}. Blocking {project.current_stage} stage.",
                        project_title, impact="high", autonomous=False)
                    actions_logged += 1

        fired = await _fire_due_scheduled_posts(db)
        actions_logged += fired

        db.commit()
        logger.info(f"[Cycle 11] Project monitor complete. Actions logged: {actions_logged}")

    except Exception as e:
        logger.error(f"[Cycle 11] Error: {e}")
        db.rollback()
    finally:
        db.close()
