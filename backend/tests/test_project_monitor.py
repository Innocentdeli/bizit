"""
Covers Organism Cycle 11 (organism/project_monitor.py) — this is the exact
code path that was silently broken all along (imported a function that didn't
exist, swallowed by a blanket except). These tests pin: stage auto-advance,
EXECUTE-stage autonomous dispatch, idempotency, and that a project never
"completes" a channel it didn't actually attempt.
"""
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from database.database import SessionLocal
from database.models import OrganismActivity
from routers.marketing_os import (
    ChannelDispatchDB,
    MarketingProjectDB,
    RetentionRecipientDB,
    WorkforceTalentDB,
    WorkOrderGigDB,
    _ensure_seed_talent,
)
from organism.project_monitor import run_project_stage_monitor


def _project(db, **overrides):
    defaults = dict(
        id=f"proj_{uuid.uuid4().hex[:8]}", user_id="test_user", title="Cycle11 Test Project",
        objective_type="revenue", target_revenue=1000000, target_count=10, target_unit="customers",
        budget_total=200000, budget_currency="NGN", deadline="2026-12-31",
        status="active", strategy_plan="{}", team_roster="[]",
    )
    defaults.update(overrides)
    p = MarketingProjectDB(**defaults)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


async def test_resource_stage_advances_to_create_once_all_gigs_assigned():
    db = SessionLocal()
    try:
        p = _project(db, current_stage="RESOURCE")
        db.add(WorkOrderGigDB(
            id=f"gig_{uuid.uuid4().hex[:8]}", project_id=p.id, user_id="test_user",
            title="G1", deliverable_type="design", role_needed="Brand Designer", brief="b",
            budget=1000.0, deadline="2026-12-31", status="open", assigned_talent_id="talent_1",
        ))
        db.commit()

        await run_project_stage_monitor()

        db.refresh(p)
        assert p.current_stage == "CREATE"
    finally:
        db.close()


async def test_resource_stage_does_not_advance_with_unassigned_gigs():
    db = SessionLocal()
    try:
        p = _project(db, current_stage="RESOURCE")
        db.add(WorkOrderGigDB(
            id=f"gig_{uuid.uuid4().hex[:8]}", project_id=p.id, user_id="test_user",
            title="G1", deliverable_type="design", role_needed="Brand Designer", brief="b",
            budget=1000.0, deadline="2026-12-31", status="open", assigned_talent_id=None,
        ))
        db.commit()

        await run_project_stage_monitor()

        db.refresh(p)
        assert p.current_stage == "RESOURCE"
    finally:
        db.close()


async def test_execute_stage_schedules_field_task_and_blocks_email_without_recipients():
    db = SessionLocal()
    try:
        _ensure_seed_talent(db)
        p = _project(db, current_stage="EXECUTE")

        with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value={"error": "no key"})):
            await run_project_stage_monitor()

        db.refresh(p)
        # Only field_marketing was dispatchable (no recipients on file for email) —
        # the project must NOT be marked as if both channels ran.
        assert p.current_stage == "EXECUTE"

        dispatches = db.query(ChannelDispatchDB).filter(ChannelDispatchDB.project_id == p.id).all()
        channels = {d.channel for d in dispatches}
        assert channels == {"field_marketing"}

        activities = db.query(OrganismActivity).filter(
            OrganismActivity.business_name == p.title[:40], OrganismActivity.action == "EMAIL CHANNEL BLOCKED"
        ).all()
        assert len(activities) == 1
    finally:
        db.close()


async def test_execute_stage_advances_to_measure_once_both_channels_attempted():
    db = SessionLocal()
    try:
        _ensure_seed_talent(db)
        p = _project(db, current_stage="EXECUTE")
        db.add(RetentionRecipientDB(project_id=p.id, contact="owner@example.com", contact_type="email"))
        db.commit()

        draft = {"subject": "Hi", "body_html": "<p>Hi</p>"}
        with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value=draft)), \
             patch("organism.mailer.send_transactional_email", return_value=True):
            await run_project_stage_monitor()

        db.refresh(p)
        assert p.current_stage == "MEASURE"

        dispatches = db.query(ChannelDispatchDB).filter(ChannelDispatchDB.project_id == p.id).all()
        channels = {d.channel for d in dispatches}
        assert channels == {"field_marketing", "email_sms_retention"}
        email_dispatch = next(d for d in dispatches if d.channel == "email_sms_retention")
        assert email_dispatch.sent_count == 1
        assert email_dispatch.status == "sent"
    finally:
        db.close()


async def test_execute_stage_actions_are_idempotent_across_cycles():
    db = SessionLocal()
    try:
        _ensure_seed_talent(db)
        p = _project(db, current_stage="EXECUTE")

        with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value={"error": "no key"})):
            await run_project_stage_monitor()
            await run_project_stage_monitor()

        dispatches = db.query(ChannelDispatchDB).filter(
            ChannelDispatchDB.project_id == p.id, ChannelDispatchDB.channel == "field_marketing"
        ).all()
        assert len(dispatches) == 1  # not duplicated on the second cycle
    finally:
        db.close()


async def test_project_marked_completed_once_target_reached():
    db = SessionLocal()
    try:
        p = _project(db, current_stage="MEASURE", target_count=5, acquired_count=5)

        await run_project_stage_monitor()

        db.refresh(p)
        assert p.status == "completed"
    finally:
        db.close()
