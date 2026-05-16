import pygame
import sys
from src.entities import Player, Enemy

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("didactic-happiness")
clock = pygame.time.Clock()

sprites = pygame.sprite.Group()
player = Player(100, WINDOW_HEIGHT // 2 - 16)
enemy = Enemy(WINDOW_WIDTH - 132, WINDOW_HEIGHT // 2 - 16)
sprites.add(player)
sprites.add(enemy)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    sprites.update()
    screen.fill((20, 20, 40))
    sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
