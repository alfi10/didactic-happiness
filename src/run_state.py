import math
from dataclasses import dataclass, field

TARGET_SCORE = 120


@dataclass
class RunState:
    combat_count: int = 0
    score: int = 0
    target_score: int = TARGET_SCORE
    owned_upgrades: dict = field(default_factory=dict)
    consumables: dict = field(default_factory=dict)
    pending_morale_penalty: int = 0
    scan_next_enemy: bool = False
    last_score_delta: int = 0

    def award_combat_score(self, player_hp: int, player_max_hp: int, tier_base: int) -> int:
        hp_bonus = math.floor((player_hp / player_max_hp) * 10) if player_max_hp else 0
        gained = tier_base + hp_bonus
        self.score += gained
        self.last_score_delta = gained
        return gained

    def is_complete(self) -> bool:
        return self.score >= self.target_score

    def register_flee(self):
        self.combat_count += 1
        self.pending_morale_penalty = 15
        self.last_score_delta = 0

    def consume_pending_morale_penalty(self) -> int:
        penalty = self.pending_morale_penalty
        self.pending_morale_penalty = 0
        return penalty
