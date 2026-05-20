import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from src.entities import Enemy, Player
from src.run_state import RunState
from src.shop import (
    SHOP_ITEMS,
    ShopItem,
    use_morale_broadcast,
    use_repair_kit,
    use_sensor_ping,
)


def test_shop_has_six_items():
    assert len(SHOP_ITEMS) == 6


def test_shop_has_three_upgrades():
    assert sum(1 for i in SHOP_ITEMS if i.kind == "upgrade") == 3


def test_shop_has_three_consumables():
    assert sum(1 for i in SHOP_ITEMS if i.kind == "consumable") == 3


def test_upgrades_have_max_stacks():
    for item in SHOP_ITEMS:
        if item.kind == "upgrade":
            assert item.max_stacks is not None and item.max_stacks > 0


def test_consumables_have_no_max_stacks():
    for item in SHOP_ITEMS:
        if item.kind == "consumable":
            assert item.max_stacks is None


def test_shop_item_has_required_fields():
    item = SHOP_ITEMS[0]
    assert isinstance(item, ShopItem)
    assert item.name and item.kind and item.cost > 0 and item.description


def test_all_items_have_callable_apply():
    for item in SHOP_ITEMS:
        assert callable(item.apply)


def test_weapon_calibration_increases_base_accuracy():
    player = Player(0, 0)
    item = next(i for i in SHOP_ITEMS if i.name == "Weapon Calibration")
    item.apply(RunState(), player)
    assert player.base_accuracy == 75


def test_reinforced_hull_increases_max_and_current_hp():
    player = Player(0, 0)
    player.hp = 70
    item = next(i for i in SHOP_ITEMS if i.name == "Reinforced Hull")
    item.apply(RunState(), player)
    assert player.max_hp == 120
    assert player.hp == 90


def test_targeting_ai_increases_destroy_chance_bonus():
    player = Player(0, 0)
    item = next(i for i in SHOP_ITEMS if i.name == "Targeting AI")
    item.apply(RunState(), player)
    assert player.destroy_chance_bonus == 0.08


def test_consumable_purchase_apply_is_store_only():
    player = Player(0, 0)
    player.hp = 80
    player.morale = 45
    run_state = RunState()
    for name in ("Repair Kit", "Morale Broadcast", "Sensor Ping"):
        item = next(i for i in SHOP_ITEMS if i.name == name)
        item.apply(run_state, player)
    assert player.hp == 80
    assert player.morale == 45
    assert run_state.consumables == {}


def test_use_repair_kit_heals_and_consumes():
    player = Player(0, 0)
    player.hp = 60
    run_state = RunState(consumables={"Repair Kit": 2})
    used = use_repair_kit(run_state, player)
    assert used is True
    assert player.hp == 85
    assert run_state.consumables["Repair Kit"] == 1


def test_use_repair_kit_caps_at_max_hp():
    player = Player(0, 0)
    player.hp = 90
    run_state = RunState(consumables={"Repair Kit": 1})
    used = use_repair_kit(run_state, player)
    assert used is True
    assert player.hp == player.max_hp
    assert "Repair Kit" not in run_state.consumables


def test_use_repair_kit_noop_at_full_hp():
    player = Player(0, 0)
    run_state = RunState(consumables={"Repair Kit": 1})
    used = use_repair_kit(run_state, player)
    assert used is False
    assert run_state.consumables["Repair Kit"] == 1


def test_use_morale_broadcast_sets_morale_and_consumes():
    player = Player(0, 0)
    player.morale = 40
    run_state = RunState(consumables={"Morale Broadcast": 1})
    used = use_morale_broadcast(run_state, player)
    assert used is True
    assert player.morale == 80
    assert "Morale Broadcast" not in run_state.consumables


def test_use_morale_broadcast_noop_at_or_above_target():
    player = Player(0, 0)
    player.morale = 85
    run_state = RunState(consumables={"Morale Broadcast": 1})
    used = use_morale_broadcast(run_state, player)
    assert used is False
    assert run_state.consumables["Morale Broadcast"] == 1


def test_use_sensor_ping_reveals_one_hidden_compartment(monkeypatch):
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    enemy = Enemy(0, 0)
    run_state = RunState(consumables={"Sensor Ping": 1})
    hidden_before = [comp for comp in enemy.compartments if not comp.revealed]
    used = use_sensor_ping(run_state, enemy)
    hidden_after = [comp for comp in enemy.compartments if not comp.revealed]
    assert used is True
    assert len(hidden_after) == len(hidden_before) - 1
    assert "Sensor Ping" not in run_state.consumables


def test_use_sensor_ping_noop_when_nothing_hidden():
    enemy = Enemy(0, 0)
    for comp in enemy.compartments:
        comp.revealed = True
    enemy.refresh()
    run_state = RunState(consumables={"Sensor Ping": 1})
    used = use_sensor_ping(run_state, enemy)
    assert used is False
    assert run_state.consumables["Sensor Ping"] == 1
