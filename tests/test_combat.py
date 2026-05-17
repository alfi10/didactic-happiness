import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from src.combat import CombatSystem
from src.compartments import Compartment, SystemType
from src.entities import Ship


def make_compartment(hp=20):
    return Compartment("Test", SystemType.HULL, 0, 0, hp=hp, max_hp=hp)


def force_hit_no_destroy(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    monkeypatch.setattr(random, "random", lambda: 0.99)


def force_hit_with_destroy(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    monkeypatch.setattr(random, "random", lambda: 0.0)


def force_miss(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 100)


def test_fire_hit_reduces_hp(monkeypatch):
    force_hit_no_destroy(monkeypatch)
    comp = make_compartment(hp=20)
    hit, damage = CombatSystem.fire(comp)
    assert hit is True
    assert damage == CombatSystem.BASE_DAMAGE
    assert comp.hp == 20 - CombatSystem.BASE_DAMAGE
    assert comp.active is True


def test_fire_miss_keeps_hp(monkeypatch):
    force_miss(monkeypatch)
    comp = make_compartment(hp=20)
    hit, damage = CombatSystem.fire(comp)
    assert hit is False
    assert damage == 0
    assert comp.hp == 20


def test_fire_hp_does_not_go_negative(monkeypatch):
    force_hit_no_destroy(monkeypatch)
    comp = make_compartment(hp=3)
    CombatSystem.fire(comp)
    assert comp.hp == 0
    assert comp.active is False


def test_compartment_defaults():
    comp = Compartment("X", SystemType.WEAPONS, 1, 2)
    assert comp.hp == 20
    assert comp.max_hp == 20
    assert comp.active is True


def test_destroy_roll_kills_compartment_instantly(monkeypatch):
    force_hit_with_destroy(monkeypatch)
    comp = make_compartment(hp=100)
    hit, damage = CombatSystem.fire(comp)
    assert hit is True
    assert comp.hp == 0
    assert comp.active is False
    assert damage == CombatSystem.BASE_DAMAGE + CombatSystem.DESTROY_BONUS_DAMAGE


def test_destroy_bonus_damage_applied_to_ship(monkeypatch):
    force_hit_with_destroy(monkeypatch)
    ship = Ship(0, 0, hp=200)
    comp = ship.compartments[0]
    CombatSystem.fire(comp, ship)
    expected = 200 - (CombatSystem.BASE_DAMAGE + CombatSystem.DESTROY_BONUS_DAMAGE)
    assert ship.hp == expected


def test_dead_compartment_hit_does_reduced_damage(monkeypatch):
    force_hit_no_destroy(monkeypatch)
    ship = Ship(0, 0, hp=200)
    comp = ship.compartments[0]
    comp.hp = 0
    comp.active = False
    hit, damage = CombatSystem.fire(comp, ship)
    assert hit is True
    assert damage == CombatSystem.DEAD_HIT_DAMAGE
    assert ship.hp == 200 - CombatSystem.DEAD_HIT_DAMAGE
    assert comp.hp == 0
    assert comp.active is False


def test_active_compartment_hit_damages_ship(monkeypatch):
    force_hit_no_destroy(monkeypatch)
    ship = Ship(0, 0, hp=200)
    comp = ship.compartments[0]
    CombatSystem.fire(comp, ship)
    assert ship.hp == 200 - CombatSystem.BASE_DAMAGE
