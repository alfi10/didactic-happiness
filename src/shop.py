from dataclasses import dataclass
import random
from typing import Callable


@dataclass
class ShopItem:
    name: str
    kind: str            # "upgrade" | "consumable"
    cost: int
    max_stacks: int | None   # None = unlimited
    description: str
    apply: Callable      # apply(run_state, player) -> None; stubbed in M5


def _weapon_calibration(run_state, player):
    player.base_accuracy += 5


def _reinforced_hull(run_state, player):
    player.max_hp += 20
    player.hp += 20
    player.refresh()


def _targeting_ai(run_state, player):
    player.destroy_chance_bonus += 0.08


def _store_only(run_state, player):
    # Consumables are added to inventory by the shop flow in main.py.
    return None


def use_repair_kit(run_state, player) -> bool:
    if run_state.consumables.get("Repair Kit", 0) <= 0 or player.hp >= player.max_hp:
        return False
    player.hp = min(player.max_hp, player.hp + 25)
    player.refresh()
    _consume_consumable(run_state, "Repair Kit")
    return True


def use_morale_broadcast(run_state, player) -> bool:
    if run_state.consumables.get("Morale Broadcast", 0) <= 0 or player.morale >= 80:
        return False
    player.morale = 80
    _consume_consumable(run_state, "Morale Broadcast")
    return True


def use_sensor_ping(run_state, enemy) -> bool:
    if run_state.consumables.get("Sensor Ping", 0) <= 0:
        return False
    hidden = [comp for comp in enemy.compartments if not comp.revealed]
    if not hidden:
        return False
    random.choice(hidden).revealed = True
    enemy.refresh()
    _consume_consumable(run_state, "Sensor Ping")
    return True


def _consume_consumable(run_state, item_name):
    remaining = run_state.consumables.get(item_name, 0) - 1
    if remaining > 0:
        run_state.consumables[item_name] = remaining
    else:
        run_state.consumables.pop(item_name, None)


SHOP_ITEMS = [
    # Upgrades
    ShopItem("Weapon Calibration", "upgrade",    12, 3,    "+5 base accuracy",         _weapon_calibration),
    ShopItem("Reinforced Hull",    "upgrade",    18, 3,    "+20 max HP",               _reinforced_hull),
    ShopItem("Targeting AI",       "upgrade",    25, 2,    "+8% destroy chance",       _targeting_ai),
    # Consumables
    ShopItem("Repair Kit",         "consumable",  8, None, "+25 HP (in-combat)",       _store_only),
    ShopItem("Morale Broadcast",   "consumable",  6, None, "Morale → 80 (in-combat)",  _store_only),
    ShopItem("Sensor Ping",        "consumable",  5, None, "Reveal enemy compartment", _store_only),
]
