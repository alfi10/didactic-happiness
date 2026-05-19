from dataclasses import dataclass
from typing import Callable


@dataclass
class NonCombatAction:
    name: str
    description: str
    apply: Callable  # apply(run_state, player) -> None


def _patch_hull(run_state, player):
    player.hp = min(player.max_hp, player.hp + 30)
    player.refresh()

def _field_repair(run_state, player):
    destroyed = [c for c in player.compartments if not c.active]
    if destroyed:
        comp = destroyed[0]
        comp.hp = max(1, comp.max_hp // 2)
        comp.active = True
        player.refresh()

def _rally_crew(run_state, player):
    if player.morale < 70:
        player.morale = 70

def _recon_drone(run_state, player):
    run_state.scan_next_enemy = True


ACTIONS = [
    NonCombatAction("Patch Hull",   "Restore 30 HP",                            _patch_hull),
    NonCombatAction("Field Repair", "Restore one destroyed compartment",         _field_repair),
    NonCombatAction("Rally Crew",   "Set morale to 70",                          _rally_crew),
    NonCombatAction("Recon Drone",  "Reveal all enemy compartments from turn 1", _recon_drone),
]
