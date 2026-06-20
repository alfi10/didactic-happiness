import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from src.enemies import (
    CRUISER_SCORE_REWARD,
    FRIGATE_SCORE_REWARD,
    SCOUT_SCORE_REWARD,
    spawn_enemy_for_combat,
    template_for_combat,
    T1_SCOUT,
    T2_FRIGATE,
    T3_CRUISER,
)


def test_template_for_combat_starts_with_scout():
    assert template_for_combat(0) == T1_SCOUT


def test_template_for_combat_last_t1_boundary():
    assert template_for_combat(3) == T1_SCOUT


def test_template_for_combat_switches_to_frigate_at_combat_5():
    assert template_for_combat(4) == T2_FRIGATE


def test_template_for_combat_last_t2_boundary():
    assert template_for_combat(8) == T2_FRIGATE


def test_template_for_combat_switches_to_cruiser_at_combat_10():
    assert template_for_combat(9) == T3_CRUISER


def test_spawn_enemy_for_combat_uses_scout_stats():
    enemy = spawn_enemy_for_combat(0, 10, 20)
    assert enemy.rect.topleft == (10, 20)
    assert enemy.hp == 60
    assert enemy.max_hp == 60
    assert enemy.base_accuracy == 35
    assert enemy.morale == 40
    assert enemy.score_reward == SCOUT_SCORE_REWARD
    assert enemy.template_name == "T1 Scout"


def test_spawn_enemy_for_combat_uses_frigate_stats():
    enemy = spawn_enemy_for_combat(4)
    assert enemy.hp == 90
    assert enemy.base_accuracy == 45
    assert enemy.morale == 50
    assert enemy.score_reward == FRIGATE_SCORE_REWARD
    assert enemy.template_name == "T2 Frigate"


def test_spawn_enemy_for_combat_uses_cruiser_stats():
    enemy = spawn_enemy_for_combat(9)
    assert enemy.hp == 130
    assert enemy.base_accuracy == 55
    assert enemy.morale == 60
    assert enemy.score_reward == CRUISER_SCORE_REWARD
    assert enemy.template_name == "T3 Cruiser"
