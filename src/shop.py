from dataclasses import dataclass
from typing import Callable


@dataclass
class ShopItem:
    name: str
    kind: str            # "upgrade" | "consumable"
    cost: int
    max_stacks: int | None   # None = unlimited
    description: str
    apply: Callable      # apply(run_state, player) -> None; stubbed in M5


def _stub(run_state, player):
    pass


SHOP_ITEMS = [
    # Upgrades
    ShopItem("Weapon Calibration", "upgrade",    12, 3,    "+5 base accuracy",         _stub),
    ShopItem("Reinforced Hull",    "upgrade",    18, 3,    "+20 max HP",               _stub),
    ShopItem("Targeting AI",       "upgrade",    25, 2,    "+8% destroy chance",       _stub),
    # Consumables
    ShopItem("Repair Kit",         "consumable",  8, None, "+25 HP (in-combat)",       _stub),
    ShopItem("Morale Broadcast",   "consumable",  6, None, "Morale → 80 (in-combat)",  _stub),
    ShopItem("Sensor Ping",        "consumable",  5, None, "Reveal enemy compartment", _stub),
]
