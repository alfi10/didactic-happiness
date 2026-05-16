import pygame

PLAYER_SIZE = 32
ENEMY_SIZE = 32


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill((0, 150, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y

    def update(self):
        pass


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y

    def update(self):
        pass
