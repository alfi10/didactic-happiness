import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from src.game_controller import ActionType, GameAction, GameController
from src.game_state import Screen, TurnState
from src.shop import SHOP_ITEMS


def test_controller_starts_on_title_with_start_action():
    controller = GameController(seed=1)
    snapshot = controller.snapshot()
    assert snapshot.screen == Screen.TITLE
    assert snapshot.available_actions == (GameAction(ActionType.START_RUN),)


def test_start_new_run_enters_combat():
    controller = GameController(seed=1)
    controller.step(GameAction(ActionType.START_RUN))
    assert controller.game_state.screen == Screen.COMBAT
    assert controller.game_state.turn_state == TurnState.PLAYER_TURN
    assert controller.run_state.score == 0


def test_selecting_target_makes_fire_available():
    controller = GameController(seed=1)
    controller.start_new_run()
    assert GameAction(ActionType.FIRE) not in controller.available_actions()
    assert controller.step(GameAction(ActionType.SELECT_TARGET, 0)) is True
    assert GameAction(ActionType.FIRE) in controller.available_actions()


def test_flee_requires_turn_two_and_enters_result_screen():
    controller = GameController(seed=1)
    controller.start_new_run()
    assert controller.flee() is False
    controller.game_state.turn_count = 2
    assert controller.flee() is True
    assert controller.game_state.screen == Screen.COMBAT_RESULT
    assert controller.game_state.last_combat_result == "flee"
    assert controller.run_state.combat_count == 1
    assert controller.run_state.pending_morale_penalty == 15


def test_non_combat_action_starts_next_combat_when_not_shop_cadence():
    controller = GameController(seed=1)
    controller.start_new_run()
    controller.run_state.combat_count = 1
    controller.game_state.screen = Screen.NON_COMBAT_ACTION
    old_enemy = controller.enemy
    controller.player.hp = 50

    assert controller.choose_non_combat_action("patch_hull") is True

    assert controller.game_state.screen == Screen.COMBAT
    assert controller.enemy is not old_enemy
    assert controller.player.hp == 80


def test_non_combat_action_routes_to_shop_on_fifth_combat():
    controller = GameController(seed=1)
    controller.start_new_run()
    controller.run_state.combat_count = 5
    controller.game_state.screen = Screen.NON_COMBAT_ACTION

    assert controller.choose_non_combat_action("recon_drone") is True

    assert controller.game_state.screen == Screen.SHOP
    assert controller.run_state.scan_next_enemy is True


def test_buy_item_deducts_score_and_applies_upgrade():
    controller = GameController(seed=1)
    controller.start_new_run()
    controller.game_state.screen = Screen.SHOP
    controller.run_state.score = 20
    item = next(item for item in SHOP_ITEMS if item.name == "Weapon Calibration")

    assert controller.buy_item(item) is True

    assert controller.run_state.score == 8
    assert controller.run_state.owned_upgrades["Weapon Calibration"] == 1
    assert controller.player.base_accuracy == 75


def test_update_combat_on_enemy_destroyed_awards_score_and_starts_resolution():
    controller = GameController(seed=1)
    controller.start_new_run()
    controller.enemy.hp = 0

    assert controller.update_combat(current_time=100) is True

    assert controller.run_state.combat_count == 1
    assert controller.run_state.score > 0
    assert controller.game_state.screen == Screen.COMBAT
    assert controller.game_state.pending_combat_screen == Screen.COMBAT_RESULT
