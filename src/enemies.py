from dataclasses import dataclass

from src.entities import Enemy


SCOUT_SCORE_REWARD = 12
FRIGATE_SCORE_REWARD = 18
CRUISER_SCORE_REWARD = 25


@dataclass(frozen=True)
class EnemyTemplate:
    name: str
    hp: int
    base_accuracy: int
    baseline_morale: int
    score_reward: int


T1_SCOUT = EnemyTemplate(
    name="T1 Scout",
    hp=60,
    base_accuracy=35,
    baseline_morale=40,
    score_reward=SCOUT_SCORE_REWARD,
)

T2_FRIGATE = EnemyTemplate(
    name="T2 Frigate",
    hp=90,
    base_accuracy=45,
    baseline_morale=50,
    score_reward=FRIGATE_SCORE_REWARD,
)

T3_CRUISER = EnemyTemplate(
    name="T3 Cruiser",
    hp=130,
    base_accuracy=55,
    baseline_morale=60,
    score_reward=CRUISER_SCORE_REWARD,
)


def template_for_combat(combat_count: int) -> EnemyTemplate:
    next_combat_number = combat_count + 1
    if next_combat_number <= 4:
        return T1_SCOUT
    if next_combat_number <= 9:
        return T2_FRIGATE
    return T3_CRUISER


def spawn_enemy_for_combat(combat_count: int, x: int = 0, y: int = 0) -> Enemy:
    template = template_for_combat(combat_count)
    return Enemy(
        x,
        y,
        hp=template.hp,
        base_accuracy=template.base_accuracy,
        morale=template.baseline_morale,
        score_reward=template.score_reward,
        template_name=template.name,
    )
