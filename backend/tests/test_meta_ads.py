"""
Covers the Meta Ads campaign-shell launch endpoint: it must fail closed and
report honestly when unconfigured/rejected, tenant-check ownership, and never
represent a campaign as anything other than a paused, incomplete shell.
"""
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from database.database import SessionLocal
from routers.marketing_os import (
    ChannelDispatchDB,
    LaunchMetaAdsRequest,
    MarketingProjectDB,
    launch_meta_ads_campaign,
)


def _project(db, **overrides):
    defaults = dict(
        id=f"proj_{uuid.uuid4().hex[:8]}", user_id="owner_user", title="Meta Ads Test Project",
        deadline="2026-12-31", status="active", current_stage="EXECUTE",
        strategy_plan="{}", team_roster="[]",
    )
    defaults.update(overrides)
    p = MarketingProjectDB(**defaults)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


async def test_launch_reports_failure_when_meta_unconfigured():
    db = SessionLocal()
    try:
        p = _project(db)
        req = LaunchMetaAdsRequest(user_id="owner_user", daily_budget=5000.0, objective="traffic")

        with patch("routers.marketing_os.meta_ads.create_campaign", new=AsyncMock(return_value=None)):
            result = await launch_meta_ads_campaign(p.id, req, db)

        assert result["status"] == "failed"
        assert result["campaign_id"] is None
        dispatch = db.query(ChannelDispatchDB).filter(ChannelDispatchDB.project_id == p.id).first()
        assert dispatch.channel == "meta_ads"
        assert dispatch.status == "failed"
    finally:
        db.close()


async def test_launch_creates_paused_campaign_and_never_claims_it_is_live():
    db = SessionLocal()
    try:
        p = _project(db)
        req = LaunchMetaAdsRequest(user_id="owner_user", daily_budget=5000.0, objective="revenue")

        with patch("routers.marketing_os.meta_ads.create_campaign",
                   new=AsyncMock(return_value={"campaign_id": "23851xxxx", "status": "PAUSED"})):
            result = await launch_meta_ads_campaign(p.id, req, db)

        assert result["status"] == "created_paused"
        assert result["campaign_id"] == "23851xxxx"
        assert "PAUSED" in result["message"] or "paused" in result["message"].lower()
        assert "manager" in result["message"].lower()  # still points the user at Meta Ads Manager to finish setup
    finally:
        db.close()


async def test_launch_rejects_wrong_tenant():
    db = SessionLocal()
    try:
        p = _project(db)
        req = LaunchMetaAdsRequest(user_id="someone_else", daily_budget=5000.0)
        with pytest.raises(HTTPException) as exc_info:
            await launch_meta_ads_campaign(p.id, req, db)
        assert exc_info.value.status_code == 403
    finally:
        db.close()


async def test_launch_404s_for_unknown_project():
    db = SessionLocal()
    try:
        req = LaunchMetaAdsRequest(user_id="owner_user", daily_budget=5000.0)
        with pytest.raises(HTTPException) as exc_info:
            await launch_meta_ads_campaign("proj_does_not_exist", req, db)
        assert exc_info.value.status_code == 404
    finally:
        db.close()
