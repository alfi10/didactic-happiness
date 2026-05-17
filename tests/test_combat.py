import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from src.combat import CombatSystem
from src.compartments import Compartment, SystemType, DESTROY_BONUS_DAMAGE
from src.entities import Ship


def make_compartment(hp=20, system_type=SystemType.HULL):
    return Compartment("Test", system_type, 0, 0, hp=hp, max_hp=hp)


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
    comp = make_compartment(hp=100, system_type=SystemType.HULL)
    hit, damage = CombatSystem.fire(comp)
    assert hit is True
    assert comp.hp == 0
    assert comp.active is False
    assert damage == CombatSystem.BASE_DAMAGE + DESTROY_BONUS_DAMAGE[SystemType.HULL]


def test_destroy_bonus_damage_per_type(monkeypatch):
    force_hit_with_destroy(monkeypatch)
    for system_type, bonus in DESTROY_BONUS_DAMAGE.items():
        comp = make_compartment(hp=100, system_type=system_type)
        hit, damage = CombatSystem.fire(comp)
        assert hit is True
        assert damage == CombatSystem.BASE_DAMAGE + bonus, f"{system_type.name} mismatch"


def test_core_destruction_deals_extra_damage(monkeypatch):
    force_hit_with_destroy(monkeypatch)
    ship = Ship(0, 0, hp=200)
    core = next(c for c in ship.compartments if c.system_type == SystemType.CORE)
    CombatSystem.fire(core, ship)
    expected = 200 - (CombatSystem.BASE_DAMAGE + DESTROY_BONUS_DAMAGE[SystemType.CORE])
    assert ship.hp == expected


def test_weapons_destruction_lowers_accuracy(monkeypatch):
    force_hit_with_destroy(monkeypatch)
    ship = Ship(0, 0, hp=200)
    weapons = next(c for c in ship.compartments if c.system_type == SystemType.WEAPONS)
    assert ship.accuracy_modifier() == 0
    CombatSystem.fire(weapons, ship)
    assert weapons.active is False
    ship.morale = 50
    assert ship.accuracy_modifier() == -15


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


def test_attacker_accuracy_modifier_applied(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 80)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    attacker = Ship(0, 0)
    attacker.morale = 100
    target_ship = Ship(0, 0)
    comp = target_ship.compartments[0]
    hit, _ = CombatSystem.fire(comp, target_ship, attacker)
    assert hit is True


def test_attacker_low_morale_reduces_accuracy(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 65)
    monkeypatch.setattr(random, "random", lambda: 0.99)
    attacker = Ship(0, 0)
    attacker.morale = 0
    target_ship = Ship(0, 0)
    comp = target_ship.compartments[0]
    hit, _ = CombatSystem.fire(comp, target_ship, attacker)
    assert hit is False
