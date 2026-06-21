import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init()

from src.entities import Player
from src.run_state import RunState
from src.non_combat import ACTIONS

PATCH_HULL   = ACTIONS[0]
FIELD_REPAIR = ACTIONS[1]
RALLY_CREW   = ACTIONS[2]
RECON_DRONE  = ACTIONS[3]


def test_patch_hull_restores_hp():
    p = Player(0, 0)
    p.hp = 50
    PATCH_HULL.apply(RunState(), p)
    assert p.hp == 80


def test_patch_hull_capped_at_max():
    p = Player(0, 0)
    p.hp = 90
    PATCH_HULL.apply(RunState(), p)
    assert p.hp == p.max_hp


def test_field_repair_restores_compartment():
    p = Player(0, 0)
    comp = p.compartments[0]
    comp.hp = 0
    comp.active = False
    FIELD_REPAIR.apply(RunState(), p, comp)
    assert comp.active is True
    assert comp.hp == comp.max_hp // 2


def test_field_repair_only_restores_selected_compartment():
    p = Player(0, 0)
    first, second = p.compartments[:2]
    first.active = False
    first.hp = 0
    second.active = False
    second.hp = 0
    FIELD_REPAIR.apply(RunState(), p, second)
    assert first.active is False


def test_field_repair_rejects_active_compartment():
    p = Player(0, 0)
    comp = p.compartments[0]
    assert FIELD_REPAIR.apply(RunState(), p, comp) is False


def test_field_repair_rejects_compartment_from_another_player():
    p = Player(0, 0)
    foreign = Player(0, 0).compartments[0]
    foreign.active = False
    foreign.hp = 0
    assert FIELD_REPAIR.apply(RunState(), p, foreign) is False


def test_field_repair_available_with_destroyed_compartment():
    p = Player(0, 0)
    p.compartments[0].active = False
    assert FIELD_REPAIR.is_available(RunState(), p) is True


def test_field_repair_unavailable_when_all_compartments_active():
    p = Player(0, 0)
    assert FIELD_REPAIR.is_available(RunState(), p) is False


def test_rally_crew_sets_morale():
    p = Player(0, 0)
    p.morale = 40
    RALLY_CREW.apply(RunState(), p)
    assert p.morale == 70


def test_rally_crew_noop_when_already_high():
    p = Player(0, 0)
    p.morale = 80
    RALLY_CREW.apply(RunState(), p)
    assert p.morale == 80


def test_rally_crew_available_below_70():
    p = Player(0, 0)
    p.morale = 69
    assert RALLY_CREW.is_available(RunState(), p) is True


def test_rally_crew_unavailable_at_70():
    p = Player(0, 0)
    p.morale = 70
    assert RALLY_CREW.is_available(RunState(), p) is False


def test_rally_crew_unavailable_above_70():
    p = Player(0, 0)
    p.morale = 71
    assert RALLY_CREW.is_available(RunState(), p) is False


def test_recon_drone_sets_flag():
    rs = RunState()
    RECON_DRONE.apply(rs, Player(0, 0))
    assert rs.scan_next_enemy is True
