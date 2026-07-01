import random
from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.combat import CombatSystem
from src.compartments import DESTROY_BONUS_DAMAGE, Compartment, SystemType
from src.enemies import spawn_enemy_for_combat
from src.entities import Enemy, Player
from src.game_state import GameState, Screen
from src.non_combat import ACTIONS as NON_COMBAT_ACTIONS
from src.run_state import RunState
from src.shop import SHOP_ITEMS, use_morale_broadcast, use_repair_kit, use_sensor_ping


class ActionType(Enum):
    START_RUN = "start_run"
    SELECT_TARGET = "select_target"
    FIRE = "fire"
    FLEE = "flee"
    CONTINUE = "continue"
    CHOOSE_NON_COMBAT = "choose_non_combat"
    FIELD_REPAIR = "field_repair"
    FIELD_REPAIR_BACK = "field_repair_back"
    BUY_ITEM = "buy_item"
    LEAVE_SHOP = "leave_shop"
    USE_CONSUMABLE = "use_consumable"


@dataclass(frozen=True)
class GameAction:
    type: ActionType
    payload: Any = None


@dataclass(frozen=True)
class ShipSnapshot:
    hp: int
    max_hp: int
    morale: int
    base_accuracy: int
    alive: bool


@dataclass(frozen=True)
class GameSnapshot:
    screen: Screen
    turn_state: str
    combat_count: int
    score: int
    target_score: int
    last_score_delta: int
    last_combat_result: str
    player: ShipSnapshot
    enemy: ShipSnapshot
    available_actions: tuple[GameAction, ...]


class GameController:
    def __init__(
        self,
        player_pos: tuple[int, int] = (0, 0),
        enemy_pos: tuple[int, int] = (0, 0),
        seed: int | None = None,
    ):
        if seed is not None:
            random.seed(seed)
        self.player_pos = player_pos
        self.enemy_pos = enemy_pos
        self.combat = CombatSystem()
        self.player = Player(*player_pos)
        self.enemy = spawn_enemy_for_combat(0, *enemy_pos)
        self.game_state = GameState()
        self.run_state = RunState()

    def snapshot(self) -> GameSnapshot:
        return GameSnapshot(
            screen=self.game_state.screen,
            turn_state=self.game_state.turn_state.name,
            combat_count=self.run_state.combat_count,
            score=self.run_state.score,
            target_score=self.run_state.target_score,
            last_score_delta=self.run_state.last_score_delta,
            last_combat_result=self.game_state.last_combat_result,
            player=self._ship_snapshot(self.player),
            enemy=self._ship_snapshot(self.enemy),
            available_actions=self.available_actions(),
        )

    def available_actions(self) -> tuple[GameAction, ...]:
        screen = self.game_state.screen
        if screen == Screen.TITLE:
            return (GameAction(ActionType.START_RUN),)
        if screen == Screen.COMBAT_RESULT:
            return (GameAction(ActionType.CONTINUE),)
        if screen == Screen.NON_COMBAT_ACTION:
            return tuple(
                GameAction(ActionType.CHOOSE_NON_COMBAT, action.key)
                for action in NON_COMBAT_ACTIONS
                if action.is_available(self.run_state, self.player)
            )
        if screen == Screen.FIELD_REPAIR:
            actions = [
                GameAction(ActionType.FIELD_REPAIR, self.player.compartments.index(compartment))
                for compartment in self.destroyed_player_compartments()
            ]
            actions.append(GameAction(ActionType.FIELD_REPAIR_BACK))
            return tuple(actions)
        if screen == Screen.SHOP:
            actions = [
                GameAction(ActionType.BUY_ITEM, item.name)
                for item in SHOP_ITEMS
                if self.can_buy(item)
            ]
            actions.append(GameAction(ActionType.LEAVE_SHOP))
            return tuple(actions)
        if screen == Screen.COMBAT:
            return self._combat_actions()
        return ()

    def step(self, action: GameAction, current_time: int = 0) -> bool:
        if action.type == ActionType.START_RUN:
            self.start_new_run()
            return True
        if action.type == ActionType.SELECT_TARGET:
            return self.select_enemy_compartment(int(action.payload))
        if action.type == ActionType.FIRE:
            return self.fire_selected(current_time)
        if action.type == ActionType.FLEE:
            return self.flee()
        if action.type == ActionType.CONTINUE:
            return self.continue_from_combat_result()
        if action.type == ActionType.CHOOSE_NON_COMBAT:
            return self.choose_non_combat_action(str(action.payload))
        if action.type == ActionType.FIELD_REPAIR:
            return self.field_repair_by_index(int(action.payload))
        if action.type == ActionType.FIELD_REPAIR_BACK:
            return self.back_from_field_repair()
        if action.type == ActionType.BUY_ITEM:
            item = next((item for item in SHOP_ITEMS if item.name == action.payload), None)
            return self.buy_item(item) if item is not None else False
        if action.type == ActionType.LEAVE_SHOP:
            self.start_next_combat()
            return True
        if action.type == ActionType.USE_CONSUMABLE:
            return self.use_combat_consumable(str(action.payload))
        return False

    def start_new_run(self, preserve_debug: bool = True):
        debug_mode = self.game_state.debug_mode if preserve_debug else False
        self.player = Player(*self.player_pos)
        self.enemy = spawn_enemy_for_combat(0, *self.enemy_pos)
        self.run_state = RunState()
        self.game_state = GameState()
        self.game_state.debug_mode = debug_mode
        self.game_state.reset_for_combat()
        self.apply_debug_to_ships()

    def select_enemy_compartment(self, compartment_index: int) -> bool:
        if not self._can_select_target() or not 0 <= compartment_index < len(self.enemy.compartments):
            return False
        self.game_state.select(self.enemy.compartments[compartment_index])
        return True

    def select_compartment(self, compartment: Compartment | None) -> bool:
        if compartment is None or compartment not in self.enemy.compartments:
            return False
        if not self._can_select_target():
            return False
        self.game_state.select(compartment)
        return True

    def fire_selected(self, current_time: int, debug_auto_kill: bool = False) -> bool:
        if not self._can_fire():
            return False
        if debug_auto_kill and self.game_state.debug_mode:
            return self.debug_auto_hit(current_time)
        target = self.game_state.selected_compartment
        hit, _ = self.combat.fire(target, self.enemy, self.player)
        if hit:
            self.game_state.register_hit(target, current_time)
        self._start_enemy_turn(current_time)
        return True

    def debug_auto_hit(self, current_time: int) -> bool:
        if not (
            self.game_state.is_player_turn()
            and self.game_state.debug_mode
            and self._ship_alive(self.player)
            and self._ship_alive(self.enemy)
            and not self.game_state.combat_resolution_active()
        ):
            return False
        target = self.game_state.selected_compartment
        if target is None or target not in self.enemy.compartments:
            target = next((compartment for compartment in self.enemy.compartments if compartment.active), None)
        if target is None:
            return False

        target.revealed = True
        target.hp = 0
        target.active = False
        bonus = DESTROY_BONUS_DAMAGE[target.system_type]
        damage = CombatSystem.BASE_DAMAGE + bonus
        self.enemy.take_damage(damage)
        self.enemy.change_morale(-CombatSystem.HIT_MORALE_PENALTY)
        if target.system_type == SystemType.CREW:
            self.enemy.change_morale(-CombatSystem.CREW_DESTROYED_MORALE_PENALTY)
        self.enemy.refresh()
        self.player.change_morale(CombatSystem.DESTROY_ENEMY_MORALE_REWARD)
        self.game_state.register_hit(target, current_time)
        self._start_enemy_turn(current_time)
        return True

    def flee(self) -> bool:
        if not (
            self.game_state.screen == Screen.COMBAT
            and self.game_state.is_player_turn()
            and self.game_state.turn_count >= 2
            and self._ship_alive(self.player)
            and self._ship_alive(self.enemy)
            and not self.game_state.combat_resolution_active()
        ):
            return False
        self.run_state.register_flee()
        self.game_state.last_combat_result = "flee"
        self.game_state.clear_selection()
        self.game_state.clear_enemy_turn()
        self.game_state.screen = Screen.COMBAT_RESULT
        return True

    def resolve_enemy_turn(self, current_time: int, force: bool = False) -> bool:
        if not (
            self.game_state.screen == Screen.COMBAT
            and not self.game_state.combat_resolution_active()
            and self._ship_alive(self.player)
            and self._ship_alive(self.enemy)
            and self.game_state.is_enemy_turn()
            and self.game_state.enemy_target is not None
        ):
            return False
        if not (force or self.game_state.enemy_ready_to_fire(current_time)):
            return False

        target = self.game_state.enemy_target
        hit, _ = self.combat.fire(target, self.player, self.enemy)
        if hit:
            self.game_state.register_hit(target, current_time)
        self.game_state.clear_enemy_turn()
        self.game_state.next_turn()
        self.game_state.increment_turn_count()
        self.player.drift_morale()
        self.enemy.drift_morale()
        return True

    def update_combat(self, current_time: int) -> bool:
        if self.game_state.screen != Screen.COMBAT:
            return False
        if self.game_state.combat_resolution_active():
            return self.game_state.complete_combat_resolution(current_time)
        if not self._ship_alive(self.enemy):
            self.run_state.combat_count += 1
            self.run_state.award_combat_score(
                self.player.hp,
                self.player.max_hp,
                self.enemy.score_reward,
            )
            self.game_state.last_combat_result = "win"
            destination = Screen.VICTORY if self.run_state.is_complete() else Screen.COMBAT_RESULT
            self.game_state.start_combat_resolution(destination, current_time)
            return True
        if not self._ship_alive(self.player):
            self.game_state.start_combat_resolution(Screen.GAME_OVER, current_time)
            return True
        return False

    def continue_from_combat_result(self) -> bool:
        if self.game_state.screen != Screen.COMBAT_RESULT:
            return False
        self.game_state.screen = Screen.NON_COMBAT_ACTION
        return True

    def choose_non_combat_action(self, action_key: str) -> bool:
        if self.game_state.screen != Screen.NON_COMBAT_ACTION:
            return False
        action = self._non_combat_action(action_key)
        if action is None or not action.is_available(self.run_state, self.player):
            return False
        if action.key == "field_repair":
            self.game_state.screen = Screen.FIELD_REPAIR
            return True
        action.apply(self.run_state, self.player)
        self.complete_non_combat_action()
        return True

    def field_repair_by_index(self, compartment_index: int) -> bool:
        if not 0 <= compartment_index < len(self.player.compartments):
            return False
        return self.apply_field_repair(self.player.compartments[compartment_index])

    def apply_field_repair(self, compartment: Compartment) -> bool:
        if self.game_state.screen != Screen.FIELD_REPAIR:
            return False
        action = self._non_combat_action("field_repair")
        if action is None or not action.apply(self.run_state, self.player, compartment):
            return False
        self.complete_non_combat_action()
        return True

    def back_from_field_repair(self) -> bool:
        if self.game_state.screen != Screen.FIELD_REPAIR:
            return False
        self.game_state.screen = Screen.NON_COMBAT_ACTION
        return True

    def complete_non_combat_action(self):
        if self.run_state.combat_count % 5 == 0:
            self.game_state.screen = Screen.SHOP
        else:
            self.start_next_combat()

    def start_next_combat(self):
        self.enemy = spawn_enemy_for_combat(self.run_state.combat_count, *self.enemy_pos)
        if self.game_state.debug_mode or self.run_state.scan_next_enemy:
            self.enemy.force_reveal = True
            self.enemy.refresh()
        self.run_state.scan_next_enemy = False
        self.game_state.reset_for_combat()
        self.game_state.last_combat_result = "win"
        penalty = self.run_state.consume_pending_morale_penalty()
        if penalty:
            self.player.change_morale(-penalty)

    def destroyed_player_compartments(self) -> list[Compartment]:
        return [compartment for compartment in self.player.compartments if not compartment.active]

    def get_item_stacks(self, item) -> int:
        if item.kind == "upgrade":
            return self.run_state.owned_upgrades.get(item.name, 0)
        return self.run_state.consumables.get(item.name, 0)

    def can_buy(self, item) -> bool:
        stacks = self.get_item_stacks(item)
        return (
            self.run_state.score >= item.cost
            and (item.max_stacks is None or stacks < item.max_stacks)
        )

    def buy_item(self, item) -> bool:
        if item is None or self.game_state.screen != Screen.SHOP or not self.can_buy(item):
            return False
        self.run_state.score -= item.cost
        item.apply(self.run_state, self.player)
        if item.kind == "upgrade":
            self.run_state.owned_upgrades[item.name] = self.get_item_stacks(item) + 1
        else:
            self.run_state.consumables[item.name] = self.get_item_stacks(item) + 1
        return True

    def combat_consumable_items(self):
        return [
            item for item in SHOP_ITEMS
            if item.kind == "consumable" and self.run_state.consumables.get(item.name, 0) > 0
        ]

    def use_combat_consumable(self, item_name: str) -> bool:
        if not (
            self.game_state.screen == Screen.COMBAT
            and self.game_state.is_player_turn()
            and self._ship_alive(self.player)
            and self._ship_alive(self.enemy)
            and not self.game_state.combat_resolution_active()
        ):
            return False
        if item_name == "Repair Kit":
            return use_repair_kit(self.run_state, self.player)
        if item_name == "Morale Broadcast":
            return use_morale_broadcast(self.run_state, self.player)
        if item_name == "Sensor Ping":
            return use_sensor_ping(self.run_state, self.enemy)
        return False

    def apply_debug_to_ships(self):
        self.enemy.force_reveal = self.game_state.debug_mode
        self.enemy.refresh()

    def _combat_actions(self) -> tuple[GameAction, ...]:
        if (
            not self.game_state.is_player_turn()
            or self.game_state.combat_resolution_active()
            or not self._ship_alive(self.player)
            or not self._ship_alive(self.enemy)
        ):
            return ()

        actions = [
            GameAction(ActionType.SELECT_TARGET, index)
            for index, _ in enumerate(self.enemy.compartments)
        ]
        if self.game_state.selected_compartment is not None:
            actions.append(GameAction(ActionType.FIRE))
        if self.game_state.turn_count >= 2:
            actions.append(GameAction(ActionType.FLEE))
        actions.extend(
            GameAction(ActionType.USE_CONSUMABLE, item.name)
            for item in self.combat_consumable_items()
        )
        return tuple(actions)

    def _start_enemy_turn(self, current_time: int):
        self.game_state.clear_selection()
        self.game_state.next_turn()
        target = self.combat.pick_enemy_target(self.enemy, self.player)
        self.game_state.start_enemy_turn(target, current_time)

    def _can_select_target(self) -> bool:
        return (
            self.game_state.screen == Screen.COMBAT
            and self.game_state.is_player_turn()
            and self._ship_alive(self.player)
            and self._ship_alive(self.enemy)
            and not self.game_state.combat_resolution_active()
        )

    def _can_fire(self) -> bool:
        return (
            self.game_state.screen == Screen.COMBAT
            and self.game_state.is_player_turn()
            and self.game_state.selected_compartment is not None
            and self._ship_alive(self.player)
            and self._ship_alive(self.enemy)
            and not self.game_state.combat_resolution_active()
        )

    def _non_combat_action(self, action_key: str):
        return next((action for action in NON_COMBAT_ACTIONS if action.key == action_key), None)

    @staticmethod
    def _ship_snapshot(ship) -> ShipSnapshot:
        return ShipSnapshot(
            hp=ship.hp,
            max_hp=ship.max_hp,
            morale=ship.morale,
            base_accuracy=ship.base_accuracy,
            alive=GameController._ship_alive(ship),
        )

    @staticmethod
    def _ship_alive(ship) -> bool:
        return ship.hp > 0
