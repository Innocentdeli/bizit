"""
Covers the new talent self-service endpoints: claiming a pre-seeded profile
vs. applying fresh (new applications must land pending review, never
immediately assignable), the by-email lookup used to link a logged-in
account to its catalog profile, and the ownership check on gig submission
that didn't exist before this.
"""
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from database.database import SessionLocal
from routers.marketing_os import (
    ApplyAsTalentRequest,
    MarketingProjectDB,
    SubmitGigRequest,
    WorkforceTalentDB,
    WorkOrderGigDB,
    apply_as_talent,
    get_talent_by_email,
    submit_gig_deliverable,
)


async def test_apply_creates_pending_review_application_for_new_email():
    db = SessionLocal()
    try:
        email = f"newtalent_{uuid.uuid4().hex[:8]}@example.com"
        req = ApplyAsTalentRequest(name="New Person", email=email, role="Copywriter", categories=["saas"])
        result = await apply_as_talent(req, db)

        assert result["status"] == "applied"
        assert result["talent"]["availability"] == "pending_review"
    finally:
        db.close()


async def test_apply_claims_existing_pre_seeded_profile_without_resetting_stats():
    db = SessionLocal()
    try:
        email = f"seeded_{uuid.uuid4().hex[:8]}@example.com"
        db.add(WorkforceTalentDB(
            id=f"talent_{uuid.uuid4().hex[:8]}", name="Seeded Person", email=email,
            role="Brand Designer", capability_scores="{}",
            reliability_score=98.0, completed_gigs=42, availability="available",
        ))
        db.commit()

        req = ApplyAsTalentRequest(name="Seeded Person", email=email, role="Brand Designer")
        result = await apply_as_talent(req, db)

        assert result["status"] == "claimed"
        assert result["talent"]["completed_gigs"] == 42  # existing stats preserved, not reset
        assert result["talent"]["availability"] == "available"  # not silently downgraded to pending_review
    finally:
        db.close()


async def test_get_talent_by_email_is_case_insensitive_and_404s_when_unknown():
    db = SessionLocal()
    try:
        email = f"CaseTest_{uuid.uuid4().hex[:8]}@Example.com"
        db.add(WorkforceTalentDB(
            id=f"talent_{uuid.uuid4().hex[:8]}", name="Case Test", email=email,
            role="Copywriter", capability_scores="{}",
        ))
        db.commit()

        found = await get_talent_by_email(email.lower(), db)
        assert found["name"] == "Case Test"

        with pytest.raises(HTTPException) as exc_info:
            await get_talent_by_email("nobody_here@example.com", db)
        assert exc_info.value.status_code == 404
    finally:
        db.close()


async def test_submit_gig_rejects_wrong_talent_email():
    db = SessionLocal()
    try:
        talent_id = f"talent_{uuid.uuid4().hex[:8]}"
        db.add(WorkforceTalentDB(
            id=talent_id, name="Assigned Talent", email="assigned@example.com",
            role="Brand Designer", capability_scores="{}",
        ))
        p = MarketingProjectDB(
            id=f"proj_{uuid.uuid4().hex[:8]}", user_id="test_user", title="Ownership Test",
            deadline="2026-12-31", status="active", current_stage="CREATE",
            strategy_plan="{}", team_roster="[]",
        )
        db.add(p)
        db.flush()
        gig = WorkOrderGigDB(
            id=f"gig_{uuid.uuid4().hex[:8]}", project_id=p.id, user_id="test_user",
            title="Banner", deliverable_type="design", role_needed="Brand Designer",
            brief="b", budget=10000.0, deadline="2026-12-31", status="in_progress",
            assigned_talent_id=talent_id,
        )
        db.add(gig)
        db.commit()

        req = SubmitGigRequest(deliverable_url="https://example.com/x.png", talent_email="someone_else@example.com")
        with pytest.raises(HTTPException) as exc_info:
            await submit_gig_deliverable(gig.id, req, db)
        assert exc_info.value.status_code == 403
    finally:
        db.close()


async def test_submit_gig_allows_correct_talent_email():
    db = SessionLocal()
    try:
        talent_id = f"talent_{uuid.uuid4().hex[:8]}"
        db.add(WorkforceTalentDB(
            id=talent_id, name="Assigned Talent", email="rightful@example.com",
            role="Brand Designer", capability_scores="{}",
        ))
        p = MarketingProjectDB(
            id=f"proj_{uuid.uuid4().hex[:8]}", user_id="test_user", title="Ownership Test 2",
            deadline="2026-12-31", status="active", current_stage="CREATE",
            strategy_plan="{}", team_roster="[]",
        )
        db.add(p)
        db.flush()
        gig = WorkOrderGigDB(
            id=f"gig_{uuid.uuid4().hex[:8]}", project_id=p.id, user_id="test_user",
            title="Banner", deliverable_type="design", role_needed="Brand Designer",
            brief="b", budget=10000.0, deadline="2026-12-31", status="in_progress",
            assigned_talent_id=talent_id,
        )
        db.add(gig)
        db.commit()

        req = SubmitGigRequest(deliverable_url="https://example.com/x.png", talent_email="Rightful@Example.com")
        with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value={"error": "no key"})):
            result = await submit_gig_deliverable(gig.id, req, db)
        assert result["status"] == "submitted"
    finally:
        db.close()
