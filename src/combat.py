import random
from src.compartments import Compartment, SystemType, DESTROY_BONUS_DAMAGE


class CombatSystem:
    BASE_ACCURACY = 70
    BASE_DAMAGE = 10
    DESTROY_CHANCE = 0.33
    DEAD_HIT_DAMAGE = 5

    HIT_MORALE_PENALTY = 10
    CREW_DESTROYED_MORALE_PENALTY = 25
    DESTROY_ENEMY_MORALE_REWARD = 15

    @staticmethod
    def fire(target_compartment: Compartment, target_ship=None, attacker_ship=None) -> tuple[bool, int]:
        threshold = CombatSystem.BASE_ACCURACY
        if attacker_ship is not None:
            threshold += attacker_ship.accuracy_modifier()

        roll = random.randint(0, 100)
        hit = roll <= threshold
        if not hit:
            return False, 0

        newly_revealed = not target_compartment.revealed
        target_compartment.revealed = True

        if not target_compartment.active:
            damage = CombatSystem.DEAD_HIT_DAMAGE
            if target_ship is not None:
                target_ship.take_damage(damage)
                target_ship.change_morale(-CombatSystem.HIT_MORALE_PENALTY)
                if newly_revealed:
                    target_ship.refresh()
            return True, damage

        target_compartment.hp = max(0, target_compartment.hp - CombatSystem.BASE_DAMAGE)
        destroyed_by_roll = random.random() < CombatSystem.DESTROY_CHANCE
        if destroyed_by_roll:
            target_compartment.hp = 0

        became_destroyed = target_compartment.hp == 0
        if became_destroyed:
            target_compartment.active = False

        bonus = DESTROY_BONUS_DAMAGE[target_compartment.system_type] if became_destroyed else 0
        damage = CombatSystem.BASE_DAMAGE + bonus

        if target_ship is not None:
            target_ship.take_damage(damage)
            target_ship.change_morale(-CombatSystem.HIT_MORALE_PENALTY)
            if became_destroyed and target_compartment.system_type == SystemType.CREW:
                target_ship.change_morale(-CombatSystem.CREW_DESTROYED_MORALE_PENALTY)
            if newly_revealed or became_destroyed:
                target_ship.refresh()

        if became_destroyed and attacker_ship is not None:
            attacker_ship.change_morale(CombatSystem.DESTROY_ENEMY_MORALE_REWARD)

        return True, damage

    @staticmethod
    def pick_enemy_target(enemy, player) -> Compartment:
        return random.choice(player.compartments)

    @staticmethod
    def enemy_attack(enemy, player) -> tuple[Compartment, bool, int]:
        if not player.compartments:
            return None, False, 0
        target = CombatSystem.pick_enemy_target(enemy, player)
        hit, damage = CombatSystem.fire(target, player, enemy)
        return target, hit, damage
