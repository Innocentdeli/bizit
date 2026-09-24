"""
Covers the Paystack payout rail: real transfers must fail closed (and say
why) whenever there's no verified payout account or Paystack itself rejects
the request — a gig must never be marked "paid" without a confirmed transfer.
"""
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from database.database import SessionLocal
from routers.marketing_os import (
    ApprovalGateDB,
    MarketingProjectDB,
    RegisterPayoutAccountRequest,
    ResolveGateRequest,
    TalentPayoutAccountDB,
    WorkforceTalentDB,
    WorkOrderGigDB,
    _execute_gig_payout,
    get_payout_account,
    register_payout_account,
    resolve_approval_gate,
)


def _project_and_gig(db, assign_talent_id="talent_1"):
    p = MarketingProjectDB(
        id=f"proj_{uuid.uuid4().hex[:8]}", user_id="test_user", title="Payout Test Project",
        deadline="2026-12-31", status="active", current_stage="CREATE",
        strategy_plan="{}", team_roster="[]",
    )
    db.add(p)
    db.flush()
    gig = WorkOrderGigDB(
        id=f"gig_{uuid.uuid4().hex[:8]}", project_id=p.id, user_id="test_user",
        title="Banner Design", deliverable_type="design", role_needed="Brand Designer",
        brief="b", budget=15000.0, deadline="2026-12-31", status="ai_approved",
        assigned_talent_id=assign_talent_id,
    )
    db.add(gig)
    gate = ApprovalGateDB(
        project_id=p.id, user_id="test_user", title="Approve payout",
        action_type="approve_gig_payout", gig_id=gig.id,
        description="test gate", cost_amount=15000.0, risk_level="low",
        status="pending_merchant",
    )
    db.add(gate)
    db.commit()
    return p, gig, gate


async def test_payout_fails_closed_with_no_assigned_talent():
    db = SessionLocal()
    try:
        _, gig, gate = _project_and_gig(db, assign_talent_id=None)
        result = await _execute_gig_payout(db, gate)
        assert result["sent"] is False
        assert "talent" in result["reason"].lower()
    finally:
        db.close()


async def test_payout_fails_closed_with_no_verified_account():
    db = SessionLocal()
    try:
        _, gig, gate = _project_and_gig(db, assign_talent_id="talent_no_account")
        result = await _execute_gig_payout(db, gate)
        assert result["sent"] is False
        db.commit()
        db.refresh(gig)
        assert gig.status == "payout_pending_bank_details"
    finally:
        db.close()


async def test_payout_succeeds_and_marks_gig_paid_with_verified_account():
    db = SessionLocal()
    try:
        _, gig, gate = _project_and_gig(db, assign_talent_id="talent_verified")
        db.add(TalentPayoutAccountDB(
            talent_id="talent_verified", bank_code="058", account_number="0123456789",
            paystack_recipient_code="RCP_test123", status="verified",
        ))
        db.commit()

        with patch("routers.marketing_os.paystack.initiate_transfer",
                   new=AsyncMock(return_value={"status": "success", "transfer_code": "TRF_test", "reference": "ref1"})):
            result = await _execute_gig_payout(db, gate)

        assert result["sent"] is True
        db.commit()
        db.refresh(gig)
        assert gig.status == "paid"
    finally:
        db.close()


async def test_payout_fails_closed_when_paystack_unconfigured():
    db = SessionLocal()
    try:
        _, gig, gate = _project_and_gig(db, assign_talent_id="talent_verified2")
        db.add(TalentPayoutAccountDB(
            talent_id="talent_verified2", bank_code="058", account_number="0123456789",
            paystack_recipient_code="RCP_test456", status="verified",
        ))
        db.commit()

        with patch("routers.marketing_os.paystack.initiate_transfer", new=AsyncMock(return_value=None)):
            result = await _execute_gig_payout(db, gate)

        assert result["sent"] is False
        db.commit()
        db.refresh(gig)
        assert gig.status == "payout_failed"
    finally:
        db.close()


async def test_resolve_gate_triggers_real_payout_attempt():
    db = SessionLocal()
    try:
        _, gig, gate = _project_and_gig(db, assign_talent_id="talent_inline")
        db.add(TalentPayoutAccountDB(
            talent_id="talent_inline", bank_code="058", account_number="0123456789",
            paystack_recipient_code="RCP_inline", status="verified",
        ))
        db.commit()

        with patch("routers.marketing_os.paystack.initiate_transfer",
                   new=AsyncMock(return_value={"status": "success", "transfer_code": "TRF_inline", "reference": "ref2"})):
            result = await resolve_approval_gate(gate.id, ResolveGateRequest(action="approve"), db)

        assert result["payout"]["sent"] is True
        db.refresh(gig)
        assert gig.status == "paid"
    finally:
        db.close()


async def test_resolve_gate_does_not_attempt_payout_for_non_payout_gates():
    db = SessionLocal()
    try:
        p = MarketingProjectDB(
            id=f"proj_{uuid.uuid4().hex[:8]}", user_id="test_user", title="Spend Gate Project",
            deadline="2026-12-31", status="active", current_stage="APPROVE",
            strategy_plan="{}", team_roster="[]",
        )
        db.add(p)
        db.flush()
        gate = ApprovalGateDB(
            project_id=p.id, user_id="test_user", title="Ad spend",
            action_type="spend_budget", description="d", cost_amount=5000.0,
            risk_level="high", status="pending_merchant",
        )
        db.add(gate)
        db.commit()

        with patch("routers.marketing_os.paystack.initiate_transfer", new=AsyncMock()) as mock_transfer:
            result = await resolve_approval_gate(gate.id, ResolveGateRequest(action="approve"), db)
            mock_transfer.assert_not_called()

        assert result["payout"] is None
    finally:
        db.close()


async def test_register_payout_account_reports_failure_when_unverifiable():
    db = SessionLocal()
    try:
        db.add(WorkforceTalentDB(
            id="talent_regfail", name="Reg Fail", email="regfail@test.dima",
            role="Brand Designer", capability_scores="{}",
        ))
        db.commit()

        with patch("routers.marketing_os.paystack.create_transfer_recipient", new=AsyncMock(return_value=None)):
            result = await register_payout_account(
                "talent_regfail",
                RegisterPayoutAccountRequest(account_number="0000000000", bank_code="999"),
                db,
            )

        assert result["verified"] is False
        assert result["status"] == "failed"
        assert result["message"] is not None
    finally:
        db.close()


async def test_register_payout_account_succeeds_and_is_readable_back():
    db = SessionLocal()
    try:
        db.add(WorkforceTalentDB(
            id="talent_regok", name="Reg OK", email="regok@test.dima",
            role="Brand Designer", capability_scores="{}",
        ))
        db.commit()

        with patch("routers.marketing_os.paystack.create_transfer_recipient",
                   new=AsyncMock(return_value={"recipient_code": "RCP_regok", "account_name": "Reg OK"})):
            result = await register_payout_account(
                "talent_regok",
                RegisterPayoutAccountRequest(account_number="0123456789", bank_code="058", bank_name="GTBank"),
                db,
            )
        assert result["verified"] is True

        fetched = await get_payout_account("talent_regok", db)
        assert fetched["registered"] is True
        assert fetched["status"] == "verified"
        assert fetched["account_number_masked"] == "***6789"
    finally:
        db.close()
