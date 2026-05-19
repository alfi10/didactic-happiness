from enum import Enum


ENEMY_ACQUIRE_MS = 1000
ENEMY_FIRE_MS = 2000


class TurnState(Enum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2


class Screen(Enum):
    COMBAT = "combat"
    COMBAT_RESULT = "combat_result"
    GAME_OVER = "game_over"
    VICTORY = "victory"


class GameState:
    def __init__(self):
        self.turn_state = TurnState.PLAYER_TURN
        self.selected_compartment = None
        self.last_hit_compartment = None
        self.last_hit_time = 0
        self.turn_count = 0
        self.enemy_target = None
        self.enemy_turn_start = 0
        self.debug_mode = False
        self.screen = Screen.COMBAT
        self.last_combat_result = "win"  # "win" | "flee" (flee added in M4)

    def next_turn(self):
        if self.turn_state == TurnState.PLAYER_TURN:
            self.turn_state = TurnState.ENEMY_TURN
        else:
            self.turn_state = TurnState.PLAYER_TURN

    def is_player_turn(self):
        return self.turn_state == TurnState.PLAYER_TURN

    def is_enemy_turn(self):
        return self.turn_state == TurnState.ENEMY_TURN

    def select(self, compartment):
        self.selected_compartment = compartment

    def clear_selection(self):
        self.selected_compartment = None

    def register_hit(self, compartment, current_time):
        self.last_hit_compartment = compartment
        self.last_hit_time = current_time

    def start_enemy_turn(self, target, current_time):
        self.enemy_target = target
        self.enemy_turn_start = current_time

    def enemy_target_acquired(self, current_time):
        return current_time - self.enemy_turn_start >= ENEMY_ACQUIRE_MS

    def enemy_ready_to_fire(self, current_time):
        return current_time - self.enemy_turn_start >= ENEMY_FIRE_MS

    def clear_enemy_turn(self):
        self.enemy_target = None
        self.enemy_turn_start = 0

    def increment_turn_count(self):
        self.turn_count += 1

    def toggle_debug(self):
        self.debug_mode = not self.debug_mode
        return self.debug_mode

    def reset_for_combat(self):
        self.turn_state = TurnState.PLAYER_TURN
        self.turn_count = 0
        self.selected_compartment = None
        self.last_hit_compartment = None
        self.last_hit_time = 0
        self.enemy_target = None
        self.enemy_turn_start = 0
        self.screen = Screen.COMBAT
