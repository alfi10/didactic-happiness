from dataclasses import dataclass
from typing import Callable


@dataclass
class NonCombatAction:
    key: str
    name: str
    description: str
    apply: Callable  # apply(run_state, player, target=None)
    is_available: Callable  # is_available(run_state, player) -> bool


def _always_available(run_state, player):
    return True


def _has_destroyed_compartments(run_state, player):
    return any(not compartment.active for compartment in player.compartments)


def _can_rally_crew(run_state, player):
    return player.morale < 70


def _patch_hull(run_state, player, target=None):
    player.hp = min(player.max_hp, player.hp + 30)
    player.refresh()


def _field_repair(run_state, player, target=None):
    if target is None or target.active:
        return False
    if not any(compartment is target for compartment in player.compartments):
        return False
    target.hp = max(1, target.max_hp // 2)
    target.active = True
    player.refresh()
    return True


def _rally_crew(run_state, player, target=None):
    if player.morale < 70:
        player.morale = 70


def _recon_drone(run_state, player, target=None):
    run_state.scan_next_enemy = True


ACTIONS = [
    NonCombatAction(
        "patch_hull", "Patch Hull", "Restore 30 HP", _patch_hull, _always_available
    ),
    NonCombatAction(
        "field_repair",
        "Field Repair",
        "Choose one destroyed compartment to restore",
        _field_repair,
        _has_destroyed_compartments,
    ),
    NonCombatAction(
        "rally_crew", "Rally Crew", "Set morale to 70", _rally_crew, _can_rally_crew
    ),
    NonCombatAction(
        "recon_drone",
        "Recon Drone",
        "Reveal all enemy compartments from turn 1",
        _recon_drone,
        _always_available,
    ),
]
