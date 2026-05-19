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
    FIELD_REPAIR.apply(RunState(), p)
    assert comp.active is True
    assert comp.hp == comp.max_hp // 2


def test_field_repair_noop_when_all_active():
    p = Player(0, 0)
    FIELD_REPAIR.apply(RunState(), p)
    assert all(c.active for c in p.compartments)


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


def test_recon_drone_sets_flag():
    rs = RunState()
    RECON_DRONE.apply(rs, Player(0, 0))
    assert rs.scan_next_enemy is True
