"""
Covers the channel dispatch endpoints: they must report what actually
happened (per-recipient success/failure) rather than always claiming success,
and must respect the tenant-ownership check.
"""
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from database.database import SessionLocal
from routers.marketing_os import (
    ChannelDispatchDB,
    DispatchEmailRequest,
    DispatchSmsRequest,
    MarketingProjectDB,
    RetentionRecipientDB,
    ScheduleFieldTaskRequest,
    WorkforceTalentDB,
    _ensure_seed_talent,
    dispatch_email_channel,
    dispatch_sms_channel,
    schedule_field_task,
)


def _project(db, **overrides):
    p = MarketingProjectDB(
        id=f"proj_{uuid.uuid4().hex[:8]}", user_id="owner_user", title="Dispatch Test Project",
        deadline="2026-12-31", status="active", current_stage="EXECUTE",
        strategy_plan="{}", team_roster="[]", **overrides,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


async def test_email_dispatch_reports_partial_failure_honestly():
    db = SessionLocal()
    try:
        p = _project(db)
        req = DispatchEmailRequest(user_id="owner_user", recipients=["a@example.com", "b@example.com"], talking_point="sale")
        draft = {"subject": "Hi", "body_html": "<p>Hi</p>"}

        with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value=draft)), \
             patch("routers.marketing_os.send_transactional_email", side_effect=[True, False]):
            result = await dispatch_email_channel(p.id, req, db)

        assert result["sent_count"] == 1
        assert result["failed_count"] == 1
        assert result["status"] == "partial_failure"
    finally:
        db.close()


async def test_email_dispatch_rejects_wrong_tenant():
    db = SessionLocal()
    try:
        p = _project(db)
        req = DispatchEmailRequest(user_id="someone_else", recipients=["a@example.com"], talking_point=None)
        with pytest.raises(HTTPException) as exc_info:
            await dispatch_email_channel(p.id, req, db)
        assert exc_info.value.status_code == 403
    finally:
        db.close()


async def test_sms_dispatch_reports_unsent_when_no_provider_configured():
    db = SessionLocal()
    try:
        p = _project(db)
        db.add(RetentionRecipientDB(project_id=p.id, contact="+2348000000000", contact_type="phone"))
        db.commit()
        req = DispatchSmsRequest(user_id="owner_user", talking_point="reminder")

        with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value={"body": "Reminder!"})), \
             patch("routers.marketing_os.send_sms", return_value=False):
            result = await dispatch_sms_channel(p.id, req, db)

        assert result["status"] == "failed"
        assert result["sent_count"] == 0
        assert result["failed_count"] == 1
    finally:
        db.close()


async def test_field_task_schedule_matches_named_talent():
    db = SessionLocal()
    try:
        _ensure_seed_talent(db)
        p = _project(db)
        talent = db.query(WorkforceTalentDB).filter(WorkforceTalentDB.role.ilike("%Field%")).first()
        req = ScheduleFieldTaskRequest(
            user_id="owner_user", task_type="call", talent_id=talent.id,
            target_description="Call the client", scheduled_for="2026-12-01T10:00:00",
        )
        result = await schedule_field_task(p.id, req, db)

        assert result["status"] == "scheduled"
        assert result["assigned_talent"] == talent.name
        dispatch = db.query(ChannelDispatchDB).filter(ChannelDispatchDB.id == result["dispatch_id"]).first()
        assert dispatch.channel == "field_marketing"
        assert dispatch.assigned_talent_id == talent.id
    finally:
        db.close()


async def test_field_task_schedule_rejects_unknown_talent():
    db = SessionLocal()
    try:
        p = _project(db)
        req = ScheduleFieldTaskRequest(
            user_id="owner_user", task_type="call", talent_id="does_not_exist",
            target_description="Call the client", scheduled_for="2026-12-01T10:00:00",
        )
        with pytest.raises(HTTPException) as exc_info:
            await schedule_field_task(p.id, req, db)
        assert exc_info.value.status_code == 404
    finally:
        db.close()
