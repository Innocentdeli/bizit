"""
Covers the P0 fix: gig deliverables must be genuinely AI-audited, never
rubber-stamped, and a failed/degraded audit must fail closed (no payout gate).
"""
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from database.database import SessionLocal
from routers.marketing_os import (
    ApprovalGateDB,
    MarketingProjectDB,
    WorkOrderGigDB,
    _run_creative_audit,
    submit_gig_deliverable,
    SubmitGigRequest,
)


def _make_gig(db, **overrides):
    project = MarketingProjectDB(
        id=f"proj_{uuid.uuid4().hex[:8]}", user_id="test_user", title="Test Project",
        deadline="2026-12-31", status="active", current_stage="CREATE",
    )
    db.add(project)
    db.flush()
    gig = WorkOrderGigDB(
        id=f"gig_{uuid.uuid4().hex[:8]}", project_id=project.id, user_id="test_user",
        title="Test Gig", deliverable_type="design", role_needed="Brand Designer",
        brief="Make a banner", budget=20000.0, deadline="2026-12-31", status="in_progress",
        **overrides,
    )
    db.add(gig)
    db.commit()
    return gig


@pytest.mark.parametrize(
    "gemini_result",
    [
        {"score": 90, "recommendation": "approve", "dimensions_check": "PASSED", "brand_alignment": "HIGH", "policy_check": "CLEAN", "issues": []},
    ],
)
async def test_creative_audit_passes_through_real_result(gemini_result):
    with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value=dict(gemini_result))):
        audit = await _run_creative_audit(_FakeGig(), None)
    assert audit["score"] == 90
    assert audit["recommendation"] == "approve"
    assert "degraded" not in audit


async def test_creative_audit_fails_closed_on_gemini_error():
    with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value={"error": "RESOURCE_EXHAUSTED"})):
        audit = await _run_creative_audit(_FakeGig(), None)
    assert audit["score"] == 0
    assert audit["recommendation"] == "request_revision"
    assert audit["degraded"] is True


class _FakeGig:
    """Just needs the attributes _run_creative_audit reads."""
    role_needed = "Brand Designer"
    deliverable_type = "design"
    brief = "Make a banner"
    budget = 20000.0
    deliverable_url = "https://example.com/banner.png"


async def test_submit_gig_deliverable_approves_and_creates_payout_gate():
    db = SessionLocal()
    try:
        gig = _make_gig(db)
        req = SubmitGigRequest(deliverable_url="https://example.com/d.png", deliverable_notes=None)
        approve_result = {
            "score": 92, "recommendation": "approve", "dimensions_check": "PASSED",
            "brand_alignment": "HIGH", "policy_check": "CLEAN", "issues": [], "correction_notes": "",
        }
        with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value=approve_result)):
            result = await submit_gig_deliverable(gig.id, req, db)

        assert result["gig_status"] == "ai_approved"
        db.refresh(gig)
        assert gig.status == "ai_approved"
        gates = db.query(ApprovalGateDB).filter(ApprovalGateDB.project_id == gig.project_id).all()
        assert len(gates) == 1
        assert gates[0].action_type == "approve_gig_payout"
    finally:
        db.close()


async def test_submit_gig_deliverable_requests_revision_without_payout_gate():
    db = SessionLocal()
    try:
        gig = _make_gig(db)
        req = SubmitGigRequest(deliverable_url="https://example.com/d.png", deliverable_notes=None)
        weak_result = {
            "score": 40, "recommendation": "request_revision", "dimensions_check": "FAILED",
            "brand_alignment": "LOW", "policy_check": "CLEAN", "issues": ["off-brand colors"],
            "correction_notes": "Use brand palette.",
        }
        with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value=weak_result)):
            result = await submit_gig_deliverable(gig.id, req, db)

        assert result["gig_status"] == "revision_requested"
        db.refresh(gig)
        assert gig.status == "revision_requested"
        gates = db.query(ApprovalGateDB).filter(ApprovalGateDB.project_id == gig.project_id).all()
        assert len(gates) == 0
    finally:
        db.close()


async def test_submit_gig_deliverable_fails_closed_when_audit_unavailable():
    db = SessionLocal()
    try:
        gig = _make_gig(db)
        req = SubmitGigRequest(deliverable_url="https://example.com/d.png", deliverable_notes=None)
        with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value={"error": "no key"})):
            result = await submit_gig_deliverable(gig.id, req, db)

        assert result["gig_status"] == "revision_requested"
        assert result["ai_audit"]["degraded"] is True
        gates = db.query(ApprovalGateDB).filter(ApprovalGateDB.project_id == gig.project_id).all()
        assert len(gates) == 0
    finally:
        db.close()
