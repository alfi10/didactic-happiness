import pygame
import sys
import random
from src.entities import Player, Enemy, CELL_SIZE, SHIP_SIZE
from src.game_state import GameState, TurnState
from src.combat import CombatSystem

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
small_font = pygame.font.Font(None, 24)

sprites = pygame.sprite.Group()
player = Player(PLAYER_X, SHIP_Y)
enemy = Enemy(ENEMY_X, SHIP_Y)
sprites.add(player)
sprites.add(enemy)

game_state = GameState()
combat = CombatSystem()

def get_compartment_at(ship, mouse_x, mouse_y):
    if not ship.rect.collidepoint(mouse_x, mouse_y):
        return None
    offset_x = mouse_x - ship.rect.x
    offset_y = mouse_y - ship.rect.y
    col = int(offset_x // CELL_SIZE)
    row = int(offset_y // CELL_SIZE)
    for comp in ship.compartments:
        if comp.row == row and comp.col == col:
            return comp
    return None

def compartment_screen_rect(ship, compartment):
    x = ship.rect.x + compartment.col * CELL_SIZE
    y = ship.rect.y + compartment.row * CELL_SIZE
    return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

def draw_hp_bar(surface, ship, label):
    bar_width = SHIP_SIZE
    bar_height = 8
    x = ship.rect.x
    y = ship.rect.y - 20
    ratio = ship.hp / ship.max_hp if ship.max_hp else 0
    pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height))
    pygame.draw.rect(surface, (200, 60, 60), (x, y, int(bar_width * ratio), bar_height))
    label_surf = small_font.render(f"{label} {ship.hp}/{ship.max_hp}", True, (200, 200, 200))
    surface.blit(label_surf, (x, y - 18))

hovered_compartment = None
current_time = 0

running = True
while running:
    current_time = pygame.time.get_ticks()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    hovered_compartment = None
    if game_state.is_player_turn():
        hovered_compartment = get_compartment_at(enemy, mouse_x, mouse_y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state.is_player_turn() and hovered_compartment:
                game_state.select(hovered_compartment)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state.is_player_turn():
                if game_state.selected_compartment:
                    hit, damage = combat.fire(game_state.selected_compartment, enemy)
                    if hit:
                        game_state.register_hit(game_state.selected_compartment, current_time)
                    game_state.clear_selection()
                    game_state.next_turn()

                    target, enemy_hit, enemy_damage = combat.enemy_attack(enemy, player)
                    if target and enemy_hit:
                        game_state.register_hit(target, current_time)
                    game_state.next_turn()

    sprites.update()
    screen.fill((20, 20, 40))
    sprites.draw(screen)

    if player.alive():
        draw_hp_bar(screen, player, "Player")
    if enemy.alive():
        draw_hp_bar(screen, enemy, "Enemy")

    if game_state.last_hit_compartment and current_time - game_state.last_hit_time < 400:
        hit_rect = compartment_screen_rect(
            player if game_state.last_hit_compartment in player.compartments else enemy,
            game_state.last_hit_compartment
        )
        flash_surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        flash_surf.set_alpha(100)
        flash_surf.fill((255, 255, 255))
        screen.blit(flash_surf, hit_rect.topleft)

    if hovered_compartment:
        hover_rect = compartment_screen_rect(enemy, hovered_compartment)
        pygame.draw.rect(screen, (255, 255, 255), hover_rect, 2)

    if game_state.selected_compartment:
        select_rect = compartment_screen_rect(enemy, game_state.selected_compartment)
        pygame.draw.rect(screen, (255, 255, 0), select_rect, 2)
        target_text = small_font.render(f"Targeting: {game_state.selected_compartment.name}", True, (255, 255, 0))
        screen.blit(target_text, (WINDOW_WIDTH // 2 - target_text.get_width() // 2, 60))

    turn_text = "Your Turn" if game_state.is_player_turn() else "Enemy Turn"
    turn_surface = font.render(turn_text, True, (200, 200, 200))
    screen.blit(turn_surface, (WINDOW_WIDTH // 2 - turn_surface.get_width() // 2, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
