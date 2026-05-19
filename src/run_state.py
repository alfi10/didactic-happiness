from dataclasses import dataclass, field
import math

TARGET_SCORE = 120
TIER1_BASE = 12   # combats 1-4
TIER2_BASE = 18   # combats 5-9
TIER3_BASE = 25   # combats 10+


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

    def tier_base(self) -> int:
        if self.combat_count <= 4:
            return TIER1_BASE
        if self.combat_count <= 9:
            return TIER2_BASE
        return TIER3_BASE

    def award_combat_score(self, player_hp: int, player_max_hp: int) -> int:
        hp_bonus = math.floor((player_hp / player_max_hp) * 10) if player_max_hp else 0
        gained = self.tier_base() + hp_bonus
        self.score += gained
        self.last_score_delta = gained
        return gained

    def is_complete(self) -> bool:
        return self.score >= self.target_score
