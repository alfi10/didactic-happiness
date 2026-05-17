import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from src.entities import Ship, DEFAULT_MORALE, MORALE_BASELINE, MAX_MORALE
from src.combat import CombatSystem
from src.compartments import SystemType


def force_hit_no_destroy(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    monkeypatch.setattr(random, "random", lambda: 0.99)


def force_hit_with_destroy(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    monkeypatch.setattr(random, "random", lambda: 0.0)


def test_ship_initial_morale():
    ship = Ship(0, 0)
    assert ship.morale == DEFAULT_MORALE


def test_change_morale_clamps_high():
    ship = Ship(0, 0)
    ship.change_morale(1000)
    assert ship.morale == MAX_MORALE


def test_change_morale_clamps_low():
    ship = Ship(0, 0)
    ship.change_morale(-1000)
    assert ship.morale == 0


def test_drift_morale_below_baseline():
    ship = Ship(0, 0)
    ship.morale = 30
    ship.drift_morale()
    assert ship.morale == 31


def test_drift_morale_above_baseline():
    ship = Ship(0, 0)
    ship.morale = 80
    ship.drift_morale()
    assert ship.morale == 79


def test_drift_morale_at_baseline_unchanged():
    ship = Ship(0, 0)
    ship.morale = MORALE_BASELINE
    ship.drift_morale()
    assert ship.morale == MORALE_BASELINE


def test_taking_damage_drops_morale(monkeypatch):
    force_hit_no_destroy(monkeypatch)
    ship = Ship(0, 0)
    starting_morale = ship.morale
    CombatSystem.fire(ship.compartments[0], ship)
    assert ship.morale == starting_morale - CombatSystem.HIT_MORALE_PENALTY


def test_crew_destroyed_drops_extra_morale(monkeypatch):
    force_hit_with_destroy(monkeypatch)
    ship = Ship(0, 0)
    crew = next(c for c in ship.compartments if c.system_type == SystemType.CREW)
    starting_morale = ship.morale
    CombatSystem.fire(crew, ship)
    expected = starting_morale - CombatSystem.HIT_MORALE_PENALTY - CombatSystem.CREW_DESTROYED_MORALE_PENALTY
    assert ship.morale == expected


def test_destroying_enemy_compartment_boosts_attacker_morale(monkeypatch):
    force_hit_with_destroy(monkeypatch)
    attacker = Ship(0, 0)
    target = Ship(0, 0)
    starting_morale = attacker.morale
    CombatSystem.fire(target.compartments[0], target, attacker)
    assert attacker.morale == starting_morale + CombatSystem.DESTROY_ENEMY_MORALE_REWARD


def test_accuracy_modifier_morale_boost():
    ship = Ship(0, 0)
    ship.morale = 100
    assert ship.accuracy_modifier() == 10


def test_accuracy_modifier_morale_penalty():
    ship = Ship(0, 0)
    ship.morale = 0
    assert ship.accuracy_modifier() == -10


def test_accuracy_modifier_combines_morale_and_weapons():
    ship = Ship(0, 0)
    ship.morale = 100
    weapons = next(c for c in ship.compartments if c.system_type == SystemType.WEAPONS)
    weapons.active = False
    assert ship.accuracy_modifier() == 10 - 15
