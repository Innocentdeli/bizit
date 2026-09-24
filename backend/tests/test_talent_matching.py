"""
Covers the talent-matching bugfix: roster assignment must pick the best-fit
talent by category capability score, not just the first row returned by the
query (the original bug).
"""
import json

from routers.marketing_os import WorkforceTalentDB, _match_talent_for_role, _ensure_seed_talent
from database.database import SessionLocal


def _talent(name, role, scores, reliability=95.0, conversion=90.0):
    return WorkforceTalentDB(
        name=name, email=f"{name.lower().replace(' ', '.')}@test.dima",
        role=role, capability_scores=json.dumps(scores),
        reliability_score=reliability, conversion_rating=conversion,
    )


def test_picks_highest_scoring_talent_for_category():
    low_tech = _talent("Fashion Designer", "Brand Designer", {"fashion": 96, "tech": 74})
    high_tech = _talent("Tech Designer", "Motion Graphics Designer", {"fashion": 50, "tech": 97})
    talents = [low_tech, high_tech]

    assert _match_talent_for_role(talents, "Designer", "tech").name == "Tech Designer"
    assert _match_talent_for_role(talents, "Designer", "fashion").name == "Fashion Designer"


def test_falls_back_to_full_pool_when_role_has_no_match():
    only_copywriter = _talent("Word Smith", "Copywriter", {"saas": 90})
    result = _match_talent_for_role([only_copywriter], "Video Producer", "saas")
    assert result is not None
    assert result.name == "Word Smith"


def test_returns_none_for_empty_pool():
    assert _match_talent_for_role([], "Designer", "fashion") is None


def test_seed_backfill_adds_missing_entries_without_touching_existing_rows():
    db = SessionLocal()
    try:
        db.add(_talent("Existing Person", "Brand Designer", {"fashion": 80}))
        db.commit()
        before_count = db.query(WorkforceTalentDB).count()
        assert before_count >= 1

        _ensure_seed_talent(db)

        after_count = db.query(WorkforceTalentDB).count()
        assert after_count >= before_count
        # The pre-existing row must survive untouched.
        existing = db.query(WorkforceTalentDB).filter(WorkforceTalentDB.name == "Existing Person").first()
        assert existing is not None
    finally:
        db.close()
