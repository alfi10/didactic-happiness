import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from src.entities import Player, Enemy, Ship
from src.combat import CombatSystem
from src.intel import format_enemy_hp, bracket_hp, display_hp_ratio, hp_visible


def force_hit_no_destroy(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    monkeypatch.setattr(random, "random", lambda: 0.99)


def force_miss(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 100)


def test_player_compartments_start_revealed():
    player = Player(0, 0)
    assert all(c.revealed for c in player.compartments)


def test_enemy_compartments_start_hidden():
    enemy = Enemy(0, 0)
    assert all(not c.revealed for c in enemy.compartments)


def test_fire_hit_reveals_compartment(monkeypatch):
    force_hit_no_destroy(monkeypatch)
    enemy = Enemy(0, 0)
    target = enemy.compartments[0]
    assert target.revealed is False
    CombatSystem.fire(target, enemy)
    assert target.revealed is True


def test_fire_miss_does_not_reveal(monkeypatch):
    force_miss(monkeypatch)
    enemy = Enemy(0, 0)
    target = enemy.compartments[0]
    CombatSystem.fire(target, enemy)
    assert target.revealed is False


def test_format_enemy_hp_hidden_before_turn_5():
    assert format_enemy_hp(73, 100, 0) == "???"
    assert format_enemy_hp(73, 100, 4) == "???"


def test_format_enemy_hp_bracketed_5_to_9():
    assert format_enemy_hp(73, 100, 5) == "~80/100"
    assert format_enemy_hp(81, 100, 7) == "~100/100"
    assert format_enemy_hp(0, 100, 5) == "~0/100"
    assert format_enemy_hp(100, 100, 9) == "~100/100"


def test_format_enemy_hp_precise_from_turn_10():
    assert format_enemy_hp(73, 100, 10) == "73/100"
    assert format_enemy_hp(0, 100, 12) == "0/100"


def test_bracket_hp_rounds_up_to_20():
    assert bracket_hp(0) == 0
    assert bracket_hp(1) == 20
    assert bracket_hp(20) == 20
    assert bracket_hp(21) == 40
    assert bracket_hp(73) == 80
    assert bracket_hp(100) == 100


def test_hp_visible():
    assert not hp_visible(0)
    assert not hp_visible(4)
    assert hp_visible(5)
    assert hp_visible(100)


def test_display_hp_ratio_zero_before_turn_5():
    assert display_hp_ratio(50, 100, 0) == 0.0


def test_display_hp_ratio_bracketed_5_to_9():
    assert display_hp_ratio(73, 100, 5) == 0.8


def test_display_hp_ratio_precise_from_turn_10():
    assert display_hp_ratio(73, 100, 10) == 0.73


def test_force_reveal_default_false():
    enemy = Enemy(0, 0)
    assert enemy.force_reveal is False


def test_force_reveal_overrides_render_without_changing_state():
    enemy = Enemy(0, 0)
    enemy.force_reveal = True
    enemy.refresh()
    assert all(not c.revealed for c in enemy.compartments)


def test_enemy_has_lower_base_accuracy():
    enemy = Enemy(0, 0)
    player = Player(0, 0)
    assert enemy.base_accuracy < player.base_accuracy
    assert enemy.base_accuracy == 40
    assert player.base_accuracy == 70
