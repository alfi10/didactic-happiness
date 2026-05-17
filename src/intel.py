import math


HP_HIDDEN_UNTIL_TURN = 5
HP_PRECISE_FROM_TURN = 10
HP_BRACKET = 20


def format_enemy_hp(hp: int, max_hp: int, turn_count: int) -> str:
    if turn_count < HP_HIDDEN_UNTIL_TURN:
        return "???"
    if turn_count < HP_PRECISE_FROM_TURN:
        bracketed = bracket_hp(hp)
        return f"~{bracketed}/{max_hp}"
    return f"{hp}/{max_hp}"


def bracket_hp(hp: int) -> int:
    if hp <= 0:
        return 0
    return math.ceil(hp / HP_BRACKET) * HP_BRACKET


def display_hp_ratio(hp: int, max_hp: int, turn_count: int) -> float:
    if turn_count < HP_HIDDEN_UNTIL_TURN:
        return 0.0
    if turn_count < HP_PRECISE_FROM_TURN:
        return min(1.0, bracket_hp(hp) / max_hp) if max_hp else 0.0
    return hp / max_hp if max_hp else 0.0


def hp_visible(turn_count: int) -> bool:
    return turn_count >= HP_HIDDEN_UNTIL_TURN
