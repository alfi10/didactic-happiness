from enum import Enum


class TurnState(Enum):
    PLAYER_TURN = 1
    ENEMY_TURN = 2


class GameState:
    def __init__(self):
        self.turn_state = TurnState.PLAYER_TURN

    def next_turn(self):
        if self.turn_state == TurnState.PLAYER_TURN:
            self.turn_state = TurnState.ENEMY_TURN
        else:
            self.turn_state = TurnState.PLAYER_TURN

    def is_player_turn(self):
        return self.turn_state == TurnState.PLAYER_TURN

    def is_enemy_turn(self):
        return self.turn_state == TurnState.ENEMY_TURN
