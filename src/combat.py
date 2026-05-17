import random
from src.compartments import Compartment


class CombatSystem:
    BASE_ACCURACY = 70
    BASE_DAMAGE = 10
    DESTROY_CHANCE = 0.33
    DESTROY_BONUS_DAMAGE = 10
    DEAD_HIT_DAMAGE = 5

    @staticmethod
    def fire(target_compartment: Compartment, target_ship=None) -> tuple[bool, int]:
        roll = random.randint(0, 100)
        hit = roll <= CombatSystem.BASE_ACCURACY
        if not hit:
            return False, 0

        if not target_compartment.active:
            damage = CombatSystem.DEAD_HIT_DAMAGE
            if target_ship is not None:
                target_ship.take_damage(damage)
            return True, damage

        target_compartment.hp = max(0, target_compartment.hp - CombatSystem.BASE_DAMAGE)
        destroyed_by_roll = random.random() < CombatSystem.DESTROY_CHANCE
        if destroyed_by_roll:
            target_compartment.hp = 0

        became_destroyed = target_compartment.hp == 0
        if became_destroyed:
            target_compartment.active = False

        damage = CombatSystem.BASE_DAMAGE + (CombatSystem.DESTROY_BONUS_DAMAGE if became_destroyed else 0)
        if target_ship is not None:
            target_ship.take_damage(damage)
            if became_destroyed:
                target_ship.refresh()
        return True, damage

    @staticmethod
    def enemy_attack(enemy, player) -> tuple[Compartment, bool, int]:
        if not player.compartments:
            return None, False, 0
        target = random.choice(player.compartments)
        hit, damage = CombatSystem.fire(target, player)
        return target, hit, damage
