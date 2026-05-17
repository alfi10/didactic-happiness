import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from src.entities import Ship, Player, Enemy, DEFAULT_SHIP_HP
from src.combat import CombatSystem


def test_ship_initial_hp():
    ship = Ship(0, 0)
    assert ship.hp == DEFAULT_SHIP_HP
    assert ship.max_hp == DEFAULT_SHIP_HP


def test_take_damage_reduces_hp():
    ship = Ship(0, 0, hp=50)
    ship.take_damage(10)
    assert ship.hp == 40


def test_take_damage_clamps_at_zero():
    ship = Ship(0, 0, hp=5)
    ship.take_damage(100)
    assert ship.hp == 0


def test_destruction_on_zero_hp():
    ship = Ship(0, 0, hp=5)
    ship.take_damage(5)
    assert ship.is_destroyed()


def test_ship_not_destroyed_above_zero():
    ship = Ship(0, 0, hp=20)
    ship.take_damage(10)
    assert not ship.is_destroyed()


def test_fire_reduces_ship_hp(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    ship = Ship(0, 0, hp=50)
    compartment = ship.compartments[0]
    CombatSystem.fire(compartment, ship)
    assert ship.hp == 50 - CombatSystem.BASE_DAMAGE


def test_compartment_disabled_at_zero_hp(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    ship = Ship(0, 0)
    compartment = ship.compartments[0]
    compartment.hp = CombatSystem.BASE_DAMAGE
    CombatSystem.fire(compartment, ship)
    assert compartment.hp == 0
    assert compartment.active is False
