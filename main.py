import pygame
import sys
from src.entities import Player, Enemy
from src.game_state import GameState, TurnState

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

PLAYER_X = 50
ENEMY_X = WINDOW_WIDTH - 170
SHIP_Y = WINDOW_HEIGHT // 2 - 60

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("didactic-happiness")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

sprites = pygame.sprite.Group()
player = Player(PLAYER_X, SHIP_Y)
enemy = Enemy(ENEMY_X, SHIP_Y)
sprites.add(player)
sprites.add(enemy)

game_state = GameState()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_state.next_turn()

    sprites.update()
    screen.fill((20, 20, 40))
    sprites.draw(screen)

    turn_text = "Your Turn" if game_state.is_player_turn() else "Enemy Turn"
    turn_surface = font.render(turn_text, True, (200, 200, 200))
    screen.blit(turn_surface, (WINDOW_WIDTH // 2 - turn_surface.get_width() // 2, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
