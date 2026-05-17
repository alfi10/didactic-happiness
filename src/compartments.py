from enum import Enum
from dataclasses import dataclass


class SystemType(Enum):
    WEAPONS = 1
    HULL = 2
    CREW = 3
    CORE = 4


@dataclass
class Compartment:
    name: str
    system_type: SystemType
    row: int
    col: int
    hp: int = 20
    max_hp: int = 20
    active: bool = True
    revealed: bool = True


HIDDEN_COMPARTMENT_COLOR = (70, 70, 80)


SYSTEM_COLORS = {
    SystemType.WEAPONS: (180, 60, 60),
    SystemType.HULL: (100, 100, 120),
    SystemType.CREW: (60, 160, 80),
    SystemType.CORE: (200, 180, 60),
}

DESTROY_BONUS_DAMAGE = {
    SystemType.WEAPONS: 5,
    SystemType.HULL: 10,
    SystemType.CREW: 10,
    SystemType.CORE: 20,
}

WEAPONS_DESTROYED_ACCURACY_PENALTY = 15


def dimmed(color, factor=0.3):
    return tuple(int(c * factor) for c in color)

DEFAULT_LAYOUT = [
    ("Port Cannons", SystemType.WEAPONS),
    ("Reactor Hull", SystemType.HULL),
    ("Starboard Cannons", SystemType.WEAPONS),
    ("Port Crew", SystemType.CREW),
    ("Core Systems", SystemType.CORE),
    ("Starboard Crew", SystemType.CREW),
    ("Port Hull", SystemType.HULL),
    ("Turret System", SystemType.WEAPONS),
    ("Starboard Hull", SystemType.HULL),
]
