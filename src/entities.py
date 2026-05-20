import pygame
from src.compartments import (
    DEFAULT_LAYOUT,
    Compartment,
    SystemType,
    SYSTEM_COLORS,
    HIDDEN_COMPARTMENT_COLOR,
    WEAPONS_DESTROYED_ACCURACY_PENALTY,
    dimmed,
)

CELL_SIZE = 40
SHIP_SIZE = CELL_SIZE * 3
DEFAULT_SHIP_HP = 100
DEFAULT_MORALE = 50
MAX_MORALE = 100
MORALE_BASELINE = 50
PLAYER_BASE_ACCURACY = 70
ENEMY_BASE_ACCURACY = 40


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, hp=DEFAULT_SHIP_HP, base_accuracy=PLAYER_BASE_ACCURACY):
        super().__init__()
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.morale = DEFAULT_MORALE
        self.base_accuracy = base_accuracy
        self.destroy_chance_bonus = 0.0
        self.force_reveal = False
        self.compartments = []
        self.image = pygame.Surface((SHIP_SIZE, SHIP_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self._build_compartments()
        self._render_compartments()

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.kill()

    def is_destroyed(self):
        return self.hp == 0

    def change_morale(self, delta):
        self.morale = max(0, min(MAX_MORALE, self.morale + delta))

    def drift_morale(self):
        if self.morale < MORALE_BASELINE:
            self.change_morale(1)
        elif self.morale > MORALE_BASELINE:
            self.change_morale(-1)

    def accuracy_modifier(self):
        morale_delta = (self.morale - MORALE_BASELINE) // 10 * 2
        weapons_penalty = sum(
            WEAPONS_DESTROYED_ACCURACY_PENALTY
            for c in self.compartments
            if c.system_type == SystemType.WEAPONS and not c.active
        )
        return morale_delta - weapons_penalty

    def _build_compartments(self):
        for i, (name, system_type) in enumerate(DEFAULT_LAYOUT):
            row = i // 3
            col = i % 3
            compartment = Compartment(name, system_type, row, col)
            self.compartments.append(compartment)

    def _render_compartments(self):
        self.image.fill((20, 20, 40))
        for compartment in self.compartments:
            x = compartment.col * CELL_SIZE
            y = compartment.row * CELL_SIZE
            visible = compartment.revealed or self.force_reveal
            if not visible:
                color = HIDDEN_COMPARTMENT_COLOR
            else:
                base_color = SYSTEM_COLORS[compartment.system_type]
                color = base_color if compartment.active else dimmed(base_color)
            pygame.draw.rect(self.image, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.image, (40, 40, 60), (x, y, CELL_SIZE, CELL_SIZE), 1)

    def refresh(self):
        self._render_compartments()

    def update(self):
        pass


class Player(Ship):
    def __init__(self, x, y):
        super().__init__(x, y)


class Enemy(Ship):
    def __init__(self, x, y):
        super().__init__(x, y, base_accuracy=ENEMY_BASE_ACCURACY)
        for compartment in self.compartments:
            compartment.revealed = False
        self.refresh()
