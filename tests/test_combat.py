import random
from src.combat import CombatSystem
from src.compartments import Compartment, SystemType


def make_compartment(hp=20):
    return Compartment("Test", SystemType.HULL, 0, 0, hp=hp, max_hp=hp)


def test_fire_hit_reduces_hp(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    comp = make_compartment(hp=20)
    hit, damage = CombatSystem.fire(comp)
    assert hit is True
    assert damage == CombatSystem.BASE_DAMAGE
    assert comp.hp == 20 - CombatSystem.BASE_DAMAGE


def test_fire_miss_keeps_hp(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 100)
    comp = make_compartment(hp=20)
    hit, damage = CombatSystem.fire(comp)
    assert hit is False
    assert damage == 0
    assert comp.hp == 20


def test_fire_hp_does_not_go_negative(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    comp = make_compartment(hp=3)
    CombatSystem.fire(comp)
    assert comp.hp == 0


def test_compartment_defaults():
    comp = Compartment("X", SystemType.WEAPONS, 1, 2)
    assert comp.hp == 20
    assert comp.max_hp == 20
    assert comp.active is True
