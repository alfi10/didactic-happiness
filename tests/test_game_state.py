from src.game_state import GameState, TurnState


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
