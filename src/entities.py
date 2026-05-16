import pygame
from src.compartments import DEFAULT_LAYOUT, Compartment, SYSTEM_COLORS

CELL_SIZE = 40
SHIP_SIZE = CELL_SIZE * 3


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.compartments = []
        self.image = pygame.Surface((SHIP_SIZE, SHIP_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self._build_compartments()
        self._render_compartments()

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
            color = SYSTEM_COLORS[compartment.system_type]
            pygame.draw.rect(self.image, color, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.image, (40, 40, 60), (x, y, CELL_SIZE, CELL_SIZE), 1)

    def update(self):
        pass


class Player(Ship):
    def __init__(self, x, y):
        super().__init__(x, y)


class Enemy(Ship):
    def __init__(self, x, y):
        super().__init__(x, y)
