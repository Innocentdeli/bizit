"""
Covers _analyze_channel_mix: AI-driven channel weighting must fall back to the
fixed default split (and say so honestly via the ai_driven flag) whenever the
model's response is missing, malformed, or doesn't add up.
"""
from unittest.mock import AsyncMock, patch

from routers.marketing_os import (
    CHANNEL_CATALOG,
    DEFAULT_CHANNEL_PCTS,
    SynthesizeStrategyRequest,
    _analyze_channel_mix,
)

_REQ = SynthesizeStrategyRequest(
    objective_type="revenue", target_value=20000000.0, target_unit="NGN",
    budget_total=3000000.0, budget_currency="NGN", timeline_days=90,
    business_category="fashion", user_id="test_user",
)


def _valid_ai_response():
    # Deliberately different from the default split, so a passthrough vs.
    # fallback is unambiguous in assertions.
    weights = {"distributor_network": 30, "meta_ads": 15, "customer_referral": 15,
               "google_search": 10, "influencer_partnerships": 10, "email_sms_retention": 10,
               "field_marketing": 5, "experimental_growth": 5}
    return {"channels": [{"channel": k, "pct": v, "reasoning": "test"} for k, v in weights.items()]}


async def test_uses_ai_weights_when_response_is_valid():
    with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value=_valid_ai_response())):
        pcts, reasoning, ai_driven = await _analyze_channel_mix(_REQ)

    assert ai_driven is True
    assert set(pcts.keys()) == set(CHANNEL_CATALOG.keys())
    assert abs(sum(pcts.values()) - 100) < 0.01
    assert pcts["distributor_network"] == 30
    assert reasoning["distributor_network"] == "test"


async def test_falls_back_when_channel_missing():
    incomplete = _valid_ai_response()
    incomplete["channels"] = incomplete["channels"][:-1]  # drop one channel
    with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value=incomplete)):
        pcts, reasoning, ai_driven = await _analyze_channel_mix(_REQ)

    assert ai_driven is False
    assert pcts == DEFAULT_CHANNEL_PCTS


async def test_falls_back_when_percentages_dont_add_up():
    bad = _valid_ai_response()
    bad["channels"][0]["pct"] = 500  # way over 100 total
    with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value=bad)):
        pcts, reasoning, ai_driven = await _analyze_channel_mix(_REQ)

    assert ai_driven is False
    assert pcts == DEFAULT_CHANNEL_PCTS


async def test_falls_back_on_gemini_error():
    with patch("routers.marketing_os.gemini.generate_reasoning", new=AsyncMock(return_value={"error": "down"})):
        pcts, reasoning, ai_driven = await _analyze_channel_mix(_REQ)

    assert ai_driven is False
    assert pcts == DEFAULT_CHANNEL_PCTS
