from src.run_state import RunState, TARGET_SCORE, TIER1_BASE, TIER2_BASE, TIER3_BASE


def test_initial_state():
    rs = RunState()
    assert rs.combat_count == 0
    assert rs.score == 0
    assert rs.target_score == TARGET_SCORE
    assert not rs.is_complete()


def test_tier_base_t1_low():
    rs = RunState(combat_count=1)
    assert rs.tier_base() == TIER1_BASE


def test_tier_base_t1_high():
    rs = RunState(combat_count=4)
    assert rs.tier_base() == TIER1_BASE


def test_tier_base_t2_low():
    rs = RunState(combat_count=5)
    assert rs.tier_base() == TIER2_BASE


def test_tier_base_t2_high():
    rs = RunState(combat_count=9)
    assert rs.tier_base() == TIER2_BASE


def test_tier_base_t3():
    rs = RunState(combat_count=10)
    assert rs.tier_base() == TIER3_BASE


def test_tier_base_t3_high():
    rs = RunState(combat_count=15)
    assert rs.tier_base() == TIER3_BASE


def test_award_score_full_hp():
    rs = RunState(combat_count=1)
    gained = rs.award_combat_score(100, 100)
    assert gained == TIER1_BASE + 10
    assert rs.score == gained


def test_award_score_half_hp():
    rs = RunState(combat_count=1)
    gained = rs.award_combat_score(50, 100)
    assert gained == TIER1_BASE + 5


def test_award_score_zero_hp():
    rs = RunState(combat_count=1)
    gained = rs.award_combat_score(0, 100)
    assert gained == TIER1_BASE + 0


def test_award_score_accumulates():
    rs = RunState(combat_count=1)
    rs.award_combat_score(100, 100)
    rs.combat_count = 2
    rs.award_combat_score(100, 100)
    assert rs.score == (TIER1_BASE + 10) * 2


def test_award_score_zero_max_hp():
    rs = RunState(combat_count=1)
    gained = rs.award_combat_score(0, 0)
    assert gained == TIER1_BASE


def test_is_complete_false():
    rs = RunState(score=119)
    assert not rs.is_complete()


def test_is_complete_at_boundary():
    rs = RunState(score=120)
    assert rs.is_complete()


def test_is_complete_above():
    rs = RunState(score=150)
    assert rs.is_complete()


def test_last_score_delta_default_zero():
    rs = RunState()
    assert rs.last_score_delta == 0


def test_award_score_sets_last_delta():
    rs = RunState(combat_count=1)
    rs.award_combat_score(100, 100)
    assert rs.last_score_delta == TIER1_BASE + 10


def test_register_flee_increments_combat_count():
    rs = RunState(combat_count=3)
    rs.register_flee()
    assert rs.combat_count == 4


def test_register_flee_sets_morale_penalty():
    rs = RunState()
    rs.register_flee()
    assert rs.pending_morale_penalty == 15


def test_register_flee_zeros_score_delta():
    rs = RunState(last_score_delta=18)
    rs.register_flee()
    assert rs.last_score_delta == 0


def test_consume_pending_morale_penalty_returns_and_clears():
    rs = RunState(pending_morale_penalty=15)
    assert rs.consume_pending_morale_penalty() == 15
    assert rs.pending_morale_penalty == 0


def test_consume_pending_morale_penalty_when_zero():
    rs = RunState()
    assert rs.consume_pending_morale_penalty() == 0
