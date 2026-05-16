import random
from src.compartments import Compartment


class CombatSystem:
    BASE_ACCURACY = 70
    BASE_DAMAGE = 5

    @staticmethod
    def fire(target_compartment: Compartment) -> tuple[bool, int]:
        roll = random.randint(0, 100)
        hit = roll <= CombatSystem.BASE_ACCURACY
        damage = CombatSystem.BASE_DAMAGE if hit else 0
        if hit:
            target_compartment.hp = max(0, target_compartment.hp - damage)
        return hit, damage

    @staticmethod
    def enemy_attack(enemy, player) -> tuple[Compartment, bool, int]:
        active_compartments = [c for c in player.compartments if c.active]
        if not active_compartments:
            return None, False, 0
        target = random.choice(active_compartments)
        hit, damage = CombatSystem.fire(target)
        return target, hit, damage
