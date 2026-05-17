from src.game_state import GameState, TurnState, ENEMY_ACQUIRE_MS, ENEMY_FIRE_MS


def test_initial_turn_is_player():
    state = GameState()
    assert state.is_player_turn()
    assert not state.is_enemy_turn()


def test_next_turn_toggles_state():
    state = GameState()
    state.next_turn()
    assert state.is_enemy_turn()
    state.next_turn()
    assert state.is_player_turn()


def test_initial_selection_is_none():
    state = GameState()
    assert state.selected_compartment is None


def test_select_sets_compartment():
    state = GameState()
    state.select("fake_compartment")
    assert state.selected_compartment == "fake_compartment"


def test_clear_selection_resets():
    state = GameState()
    state.select("fake")
    state.clear_selection()
    assert state.selected_compartment is None


def test_turn_count_starts_zero():
    state = GameState()
    assert state.turn_count == 0


def test_increment_turn_count():
    state = GameState()
    state.increment_turn_count()
    state.increment_turn_count()
    assert state.turn_count == 2


def test_enemy_target_acquired_threshold():
    state = GameState()
    state.start_enemy_turn("target", current_time=0)
    assert not state.enemy_target_acquired(ENEMY_ACQUIRE_MS - 1)
    assert state.enemy_target_acquired(ENEMY_ACQUIRE_MS)


def test_enemy_ready_to_fire_threshold():
    state = GameState()
    state.start_enemy_turn("target", current_time=0)
    assert not state.enemy_ready_to_fire(ENEMY_FIRE_MS - 1)
    assert state.enemy_ready_to_fire(ENEMY_FIRE_MS)


def test_clear_enemy_turn_resets():
    state = GameState()
    state.start_enemy_turn("target", current_time=500)
    state.clear_enemy_turn()
    assert state.enemy_target is None
    assert state.enemy_turn_start == 0


def test_debug_mode_starts_disabled():
    state = GameState()
    assert state.debug_mode is False


def test_toggle_debug_flips_flag():
    state = GameState()
    assert state.toggle_debug() is True
    assert state.debug_mode is True
    assert state.toggle_debug() is False
    assert state.debug_mode is False
