from enum import Enum


class TurnState(Enum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2


class GameState:
    def __init__(self):
        self.turn_state = TurnState.PLAYER_TURN
        self.selected_compartment = None
        self.last_hit_compartment = None
        self.last_hit_time = 0

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
