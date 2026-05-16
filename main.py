import pygame
import sys

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("didactic-happiness")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 20, 40))
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
