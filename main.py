import math
import sys

import pygame

from src.entities import CELL_SIZE, SHIP_SIZE
from src.game_state import Screen
from src.game_controller import GameController
from src.intel import format_enemy_hp, display_hp_ratio, hp_visible
from src.non_combat import ACTIONS as NON_COMBAT_ACTIONS
from src.shop import SHOP_ITEMS

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

PLAYER_X = 50
ENEMY_X = WINDOW_WIDTH - 170
SHIP_Y = WINDOW_HEIGHT // 2 - 60

FIRE_BUTTON_WIDTH = 160
FIRE_BUTTON_HEIGHT = 44
FIRE_BUTTON_CENTER_Y = WINDOW_HEIGHT - 70
RESULT_BUTTON_WIDTH = 160
RESULT_BUTTON_HEIGHT = 44
TITLE_BUTTON_WIDTH = 220
TITLE_BUTTON_HEIGHT = 48
TITLE_BUTTON_GAP = 16
DEBUG_KILL_BUTTON_WIDTH = 120
FLEE_BUTTON_WIDTH = 120
ACTION_BUTTON_WIDTH = 260
ACTION_BUTTON_HEIGHT = 44
ACTION_SLOT_HEIGHT = 82
ACTION_START_Y = 200
REPAIR_BUTTON_WIDTH = 210
REPAIR_BUTTON_HEIGHT = 48
REPAIR_BUTTON_GAP = 16
SHOP_ROW_H = 68
SHOP_ROW_GAP = 6
SHOP_ROW_W = 680
SHOP_BUY_W = 100
SHOP_BUY_H = 36
CONSUMABLE_BUTTON_WIDTH = 150
CONSUMABLE_BUTTON_HEIGHT = 36
CONSUMABLE_BUTTON_GAP = 10
CONSUMABLE_STRIP_Y = WINDOW_HEIGHT - 126


def fire_button_rect():
    return pygame.Rect(
        WINDOW_WIDTH // 2 - FIRE_BUTTON_WIDTH // 2,
        FIRE_BUTTON_CENTER_Y - FIRE_BUTTON_HEIGHT // 2,
        FIRE_BUTTON_WIDTH,
        FIRE_BUTTON_HEIGHT,
    )

def continue_button_rect():
    return pygame.Rect(WINDOW_WIDTH // 2 - RESULT_BUTTON_WIDTH // 2,
                       WINDOW_HEIGHT // 2 + 90,
                       RESULT_BUTTON_WIDTH, RESULT_BUTTON_HEIGHT)

def quit_button_rect():
    return pygame.Rect(WINDOW_WIDTH // 2 - RESULT_BUTTON_WIDTH // 2,
                       WINDOW_HEIGHT // 2 + 90,
                       RESULT_BUTTON_WIDTH, RESULT_BUTTON_HEIGHT)

def title_button_rects():
    start_y = WINDOW_HEIGHT // 2 - 30
    return [
        pygame.Rect(
            WINDOW_WIDTH // 2 - TITLE_BUTTON_WIDTH // 2,
            start_y + i * (TITLE_BUTTON_HEIGHT + TITLE_BUTTON_GAP),
            TITLE_BUTTON_WIDTH,
            TITLE_BUTTON_HEIGHT,
        )
        for i in range(3)
    ]

def flee_button_rect():
    return pygame.Rect(
        WINDOW_WIDTH // 2 - FIRE_BUTTON_WIDTH // 2 - 10 - FLEE_BUTTON_WIDTH,
        FIRE_BUTTON_CENTER_Y - FIRE_BUTTON_HEIGHT // 2,
        FLEE_BUTTON_WIDTH,
        FIRE_BUTTON_HEIGHT,
    )

def debug_kill_button_rect():
    return pygame.Rect(
        WINDOW_WIDTH // 2 + FIRE_BUTTON_WIDTH // 2 + 10,
        FIRE_BUTTON_CENTER_Y - FIRE_BUTTON_HEIGHT // 2,
        DEBUG_KILL_BUTTON_WIDTH,
        FIRE_BUTTON_HEIGHT,
    )

def action_button_rects():
    cx = WINDOW_WIDTH // 2
    return [
        pygame.Rect(cx - ACTION_BUTTON_WIDTH // 2,
                    ACTION_START_Y + i * ACTION_SLOT_HEIGHT,
                    ACTION_BUTTON_WIDTH, ACTION_BUTTON_HEIGHT)
        for i in range(len(NON_COMBAT_ACTIONS))
    ]

def field_repair_button_rects(compartments):
    columns = 3
    total_width = columns * REPAIR_BUTTON_WIDTH + (columns - 1) * REPAIR_BUTTON_GAP
    start_x = WINDOW_WIDTH // 2 - total_width // 2
    start_y = 150
    return [
        pygame.Rect(
            start_x + (i % columns) * (REPAIR_BUTTON_WIDTH + REPAIR_BUTTON_GAP),
            start_y + (i // columns) * (REPAIR_BUTTON_HEIGHT + REPAIR_BUTTON_GAP),
            REPAIR_BUTTON_WIDTH,
            REPAIR_BUTTON_HEIGHT,
        )
        for i in range(len(compartments))
    ]

def field_repair_back_rect():
    return pygame.Rect(
        WINDOW_WIDTH // 2 - RESULT_BUTTON_WIDTH // 2,
        WINDOW_HEIGHT - 70,
        RESULT_BUTTON_WIDTH,
        RESULT_BUTTON_HEIGHT,
    )

def shop_row_rects():
    start_y = 75
    cx = WINDOW_WIDTH // 2
    result = []
    for i in range(len(SHOP_ITEMS)):
        y = start_y + i * (SHOP_ROW_H + SHOP_ROW_GAP)
        card = pygame.Rect(cx - SHOP_ROW_W // 2, y, SHOP_ROW_W, SHOP_ROW_H)
        buy = pygame.Rect(card.right - SHOP_BUY_W - 8,
                          card.centery - SHOP_BUY_H // 2,
                          SHOP_BUY_W, SHOP_BUY_H)
        result.append((card, buy))
    return result

def leave_shop_button_rect():
    return pygame.Rect(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT - 56, 160, 44)


def combat_consumable_items():
    return controller.combat_consumable_items()


def combat_consumable_button_rects(items):
    total_width = len(items) * CONSUMABLE_BUTTON_WIDTH + max(0, len(items) - 1) * CONSUMABLE_BUTTON_GAP
    start_x = WINDOW_WIDTH // 2 - total_width // 2
    return [
        pygame.Rect(
            start_x + i * (CONSUMABLE_BUTTON_WIDTH + CONSUMABLE_BUTTON_GAP),
            CONSUMABLE_STRIP_Y,
            CONSUMABLE_BUTTON_WIDTH,
            CONSUMABLE_BUTTON_HEIGHT,
        )
        for i in range(len(items))
    ]

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("didactic-happiness")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

sprites = pygame.sprite.Group()
controller = GameController(player_pos=(PLAYER_X, SHIP_Y), enemy_pos=(ENEMY_X, SHIP_Y))
player = controller.player
enemy = controller.enemy
sprites.add(player)
sprites.add(enemy)

game_state = controller.game_state
run_state = controller.run_state
debug_auto_kill = False
options_message_visible = False


def sync_controller_refs():
    global player, enemy, game_state, run_state
    player = controller.player
    enemy = controller.enemy
    game_state = controller.game_state
    run_state = controller.run_state


def sync_controller_refs_and_sprites(old_enemy=None):
    sync_controller_refs()
    if old_enemy is not None and enemy is not old_enemy:
        sprites.remove(old_enemy)
        sprites.add(enemy)

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

def draw_enemy_hp_bar(surface, ship, turn_count, debug=False):
    bar_width = SHIP_SIZE
    bar_height = 8
    x = ship.rect.x
    y = ship.rect.y - 20
    if debug:
        ratio = ship.hp / ship.max_hp if ship.max_hp else 0
        visible = True
        label = f"Enemy {ship.hp}/{ship.max_hp}"
    else:
        ratio = display_hp_ratio(ship.hp, ship.max_hp, turn_count)
        visible = hp_visible(turn_count)
        label = f"Enemy {format_enemy_hp(ship.hp, ship.max_hp, turn_count)}"
    pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height))
    if visible:
        pygame.draw.rect(surface, (200, 60, 60), (x, y, int(bar_width * ratio), bar_height))
    label_surf = small_font.render(label, True, (200, 200, 200))
    surface.blit(label_surf, (x, y - 18))


def draw_debug_hud(surface, player, enemy, game_state, run_state):
    if not game_state.debug_mode:
        return
    lines = [
        "DEBUG MODE (F1)",
        f"Turn: {game_state.turn_count}",
        f"Player: HP {player.hp}/{player.max_hp}  Morale {player.morale}  Acc {player.base_accuracy:+d}{player.accuracy_modifier():+d}",
        f"Enemy:  HP {enemy.hp}/{enemy.max_hp}  Morale {enemy.morale}  Acc {enemy.base_accuracy:+d}{enemy.accuracy_modifier():+d}",
        f"Score: {run_state.score} / {run_state.target_score}  Combats: {run_state.combat_count}",
    ]
    y = 10
    for line in lines:
        surf = small_font.render(line, True, (255, 220, 100))
        surface.blit(surf, (10, y))
        y += 20

def draw_morale_bar(surface, ship):
    bar_width = SHIP_SIZE
    bar_height = 6
    x = ship.rect.x
    y = ship.rect.y - 10
    ratio = ship.morale / 100
    pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height))
    pygame.draw.rect(surface, (80, 180, 220), (x, y, int(bar_width * ratio), bar_height))

def draw_button(surface, rect, label, enabled=True):
    background = (50, 100, 180) if enabled else (45, 45, 55)
    border = (80, 140, 220) if enabled else (70, 70, 85)
    text_color = (255, 255, 255) if enabled else (120, 120, 130)
    pygame.draw.rect(surface, background, rect)
    pygame.draw.rect(surface, border, rect, 2)
    text = small_font.render(label, True, text_color)
    surface.blit(text, (rect.centerx - text.get_width() // 2,
                        rect.centery - text.get_height() // 2))


def draw_combat_consumables(surface, game_state):
    items = combat_consumable_items()
    if not items:
        return
    active_turn = game_state.is_player_turn()
    header = small_font.render("Consumables", True, (180, 180, 220))
    rects = combat_consumable_button_rects(items)
    first_rect = rects[0]
    surface.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, first_rect.y - 22))
    for item, rect in zip(items, rects):
        count = run_state.consumables[item.name]
        bg_color = (50, 100, 180) if active_turn else (45, 45, 55)
        border_color = (80, 140, 220) if active_turn else (70, 70, 85)
        text_color = (255, 255, 255) if active_turn else (120, 120, 130)
        pygame.draw.rect(surface, bg_color, rect)
        pygame.draw.rect(surface, border_color, rect, 2)
        label = small_font.render(f"{item.name} x{count}", True, text_color)
        surface.blit(
            label,
            (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2),
        )


def draw_fire_button(surface, game_state):
    if game_state.is_enemy_turn():
        return
    rect = fire_button_rect()
    active = game_state.selected_compartment is not None
    bg_color = (180, 40, 40) if active else (50, 50, 50)
    border_color = (220, 60, 60) if active else (90, 90, 90)
    text_color = (255, 255, 255) if active else (120, 120, 120)
    pygame.draw.rect(surface, bg_color, rect)
    pygame.draw.rect(surface, border_color, rect, 2)
    text_surf = small_font.render("Fire (space)", True, text_color)
    surface.blit(
        text_surf,
        (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2),
    )

def draw_flee_button(surface, game_state):
    if game_state.is_enemy_turn():
        return
    rect = flee_button_rect()
    active = game_state.turn_count >= 2
    bg_color = (140, 90, 40) if active else (50, 50, 50)
    border_color = (200, 140, 60) if active else (90, 90, 90)
    text_color = (255, 255, 255) if active else (120, 120, 120)
    pygame.draw.rect(surface, bg_color, rect)
    pygame.draw.rect(surface, border_color, rect, 2)
    text_surf = small_font.render("Flee", True, text_color)
    surface.blit(
        text_surf,
        (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2),
    )

def perform_flee():
    controller.flee()

def perform_fire():
    controller.fire_selected(current_time, debug_auto_kill=debug_auto_kill)


def debug_auto_hit():
    controller.debug_auto_hit(current_time)


def apply_debug_to_ships():
    controller.apply_debug_to_ships()


def start_new_run():
    global debug_auto_kill, options_message_visible
    sprites.empty()
    controller.start_new_run()
    sync_controller_refs()
    sprites.add(player, enemy)
    debug_auto_kill = False
    options_message_visible = False


def start_next_combat():
    sprites.remove(enemy)
    controller.start_next_combat()
    sync_controller_refs()
    sprites.add(enemy)


def complete_non_combat_action():
    old_enemy = enemy
    controller.complete_non_combat_action()
    sync_controller_refs_and_sprites(old_enemy)


def destroyed_player_compartments():
    return controller.destroyed_player_compartments()


def get_item_stacks(item):
    return controller.get_item_stacks(item)

def can_buy(item):
    return controller.can_buy(item)

def buy_item(item):
    controller.buy_item(item)


def use_combat_consumable(item_name):
    return controller.use_combat_consumable(item_name)


def handle_combat_consumable_click(mouse_x, mouse_y):
    items = combat_consumable_items()
    for item, rect in zip(items, combat_consumable_button_rects(items)):
        if rect.collidepoint(mouse_x, mouse_y):
            use_combat_consumable(item.name)
            return True
    return False


def render_shop():
    screen.fill((20, 20, 40))
    header = font.render("Shop", True, (220, 180, 80))
    screen.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, 22))
    score_surf = small_font.render(
        f"Score: {run_state.score} / {run_state.target_score}", True, (200, 200, 200))
    screen.blit(score_surf, (WINDOW_WIDTH // 2 - score_surf.get_width() // 2, 50))

    for item, (card, buy) in zip(SHOP_ITEMS, shop_row_rects()):
        stacks = get_item_stacks(item)
        affordable = can_buy(item)
        card_color = (35, 35, 60) if affordable else (28, 28, 45)
        pygame.draw.rect(screen, card_color, card)
        pygame.draw.rect(screen, (70, 70, 100), card, 1)

        name_surf = small_font.render(item.name, True, (220, 220, 255))
        screen.blit(name_surf, (card.x + 10, card.y + 6))

        desc_surf = small_font.render(item.description, True, (150, 150, 180))
        screen.blit(desc_surf, (card.x + 10, card.y + 26))

        kind_tag = "UPG" if item.kind == "upgrade" else "USE"
        stack_str = f"[{kind_tag}]  owned: {stacks}"
        if item.max_stacks:
            stack_str += f" / {item.max_stacks}"
        stack_surf = small_font.render(stack_str, True, (120, 120, 140))
        screen.blit(stack_surf, (card.x + 10, card.y + 46))

        buy_bg = (50, 130, 80) if affordable else (45, 45, 45)
        buy_bd = (80, 180, 110) if affordable else (65, 65, 65)
        pygame.draw.rect(screen, buy_bg, buy)
        pygame.draw.rect(screen, buy_bd, buy, 2)
        buy_col = (255, 255, 255) if affordable else (90, 90, 90)
        cost_surf = small_font.render(f"{item.cost} pts", True, buy_col)
        screen.blit(cost_surf, (buy.centerx - cost_surf.get_width() // 2,
                                buy.centery - cost_surf.get_height() // 2))

    draw_button(screen, leave_shop_button_rect(), "Leave Shop")


def render_title():
    screen.fill((12, 18, 36))
    pygame.draw.circle(screen, (35, 72, 112), (120, 90), 170)
    pygame.draw.circle(screen, (24, 48, 82), (720, 520), 230)

    title = font.render("DIDACTIC HAPPINESS", True, (235, 225, 175))
    screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 105))
    subtitle = small_font.render(
        "Tactical space combat", True, (145, 180, 205)
    )
    screen.blit(
        subtitle,
        (WINDOW_WIDTH // 2 - subtitle.get_width() // 2, 150),
    )

    labels = ("Start Game", "Options", "Quit")
    for label, rect in zip(labels, title_button_rects()):
        draw_button(screen, rect, label)

    if options_message_visible:
        message = small_font.render(
            "Options are not available yet.", True, (220, 190, 110)
        )
        screen.blit(
            message,
            (WINDOW_WIDTH // 2 - message.get_width() // 2, WINDOW_HEIGHT - 65),
        )


def render_combat_result():
    screen.fill((20, 20, 40))
    if game_state.last_combat_result == "flee":
        header = font.render(f"Combat {run_state.combat_count} Abandoned", True, (200, 140, 60))
        screen.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, WINDOW_HEIGHT // 2 - 110))
        delta = font.render("Fled — +0 Score", True, (200, 140, 60))
        screen.blit(delta, (WINDOW_WIDTH // 2 - delta.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
        sub = small_font.render("Morale −15 applied at next combat", True, (180, 160, 140))
        screen.blit(sub, (WINDOW_WIDTH // 2 - sub.get_width() // 2, WINDOW_HEIGHT // 2 - 10))
    else:
        header = font.render(f"Combat {run_state.combat_count} Complete", True, (255, 220, 80))
        screen.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, WINDOW_HEIGHT // 2 - 110))
        delta = font.render(f"+{run_state.last_score_delta} Score", True, (100, 255, 100))
        screen.blit(delta, (WINDOW_WIDTH // 2 - delta.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
    total = small_font.render(f"Total: {run_state.score} / {run_state.target_score}", True, (200, 200, 200))
    screen.blit(total, (WINDOW_WIDTH // 2 - total.get_width() // 2, WINDOW_HEIGHT // 2 + 30))
    draw_button(screen, continue_button_rect(), "Continue")


def render_non_combat_action():
    screen.fill((20, 20, 40))
    header = font.render("Choose an Action", True, (200, 200, 255))
    screen.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, 25))

    hull = small_font.render(
        f"Hull: {player.hp} / {player.max_hp}", True, (200, 200, 200)
    )
    morale = small_font.render(
        f"Morale: {player.morale} / 100", True, (200, 200, 200)
    )
    destroyed = destroyed_player_compartments()
    screen.blit(hull, (WINDOW_WIDTH // 2 - hull.get_width() // 2, 70))
    screen.blit(morale, (WINDOW_WIDTH // 2 - morale.get_width() // 2, 94))

    destroyed_names = [compartment.name for compartment in destroyed]
    destroyed_rows = [
        ", ".join(destroyed_names[index:index + 3])
        for index in range(0, len(destroyed_names), 3)
    ] or ["None"]
    for row_index, names in enumerate(destroyed_rows):
        prefix = "Destroyed: " if row_index == 0 else ""
        destroyed_text = small_font.render(
            f"{prefix}{names}", True, (180, 160, 160)
        )
        screen.blit(
            destroyed_text,
            (
                WINDOW_WIDTH // 2 - destroyed_text.get_width() // 2,
                122 + row_index * 20,
            ),
        )

    for action, rect in zip(NON_COMBAT_ACTIONS, action_button_rects()):
        available = action.is_available(run_state, player)
        draw_button(screen, rect, action.name, enabled=available)
        description_color = (140, 140, 160) if available else (90, 90, 105)
        desc = small_font.render(action.description, True, description_color)
        screen.blit(desc, (WINDOW_WIDTH // 2 - desc.get_width() // 2, rect.bottom + 4))


def render_field_repair():
    screen.fill((20, 20, 40))
    header = font.render("Field Repair", True, (200, 200, 255))
    screen.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, 40))
    prompt = small_font.render(
        "Choose a destroyed compartment to restore to half HP",
        True,
        (160, 160, 190),
    )
    screen.blit(prompt, (WINDOW_WIDTH // 2 - prompt.get_width() // 2, 90))

    destroyed = destroyed_player_compartments()
    for compartment, rect in zip(destroyed, field_repair_button_rects(destroyed)):
        draw_button(screen, rect, compartment.name)
    draw_button(screen, field_repair_back_rect(), "Back")


def render_game_over():
    screen.fill((20, 20, 40))
    header = font.render("GAME OVER", True, (255, 80, 80))
    screen.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, WINDOW_HEIGHT // 2 - 110))
    score_text = font.render(f"Score: {run_state.score} / {run_state.target_score}", True, (200, 200, 200))
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
    combats = small_font.render(f"Combats survived: {run_state.combat_count}", True, (160, 160, 160))
    screen.blit(combats, (WINDOW_WIDTH // 2 - combats.get_width() // 2, WINDOW_HEIGHT // 2 + 10))
    draw_button(screen, quit_button_rect(), "Back to Menu")


def render_victory():
    screen.fill((20, 20, 40))
    header = font.render("VICTORY!", True, (100, 255, 100))
    screen.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, WINDOW_HEIGHT // 2 - 110))
    score_text = font.render(f"Score: {run_state.score} / {run_state.target_score}", True, (200, 200, 200))
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
    combats = small_font.render(f"Combats: {run_state.combat_count}", True, (160, 160, 160))
    screen.blit(combats, (WINDOW_WIDTH // 2 - combats.get_width() // 2, WINDOW_HEIGHT // 2 + 10))
    draw_button(screen, quit_button_rect(), "Back to Menu")


def draw_combat_resolution(surface, game_state, current_time):
    progress = game_state.combat_resolution_progress(current_time)
    destination = game_state.pending_combat_screen
    victory = destination in (Screen.COMBAT_RESULT, Screen.VICTORY)
    label = "VICTORY" if victory else "DEFEAT"
    color = (100, 255, 100) if victory else (255, 80, 80)

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 10, 24, int(180 * progress)))
    surface.blit(overlay, (0, 0))

    # Temporary placeholder until final combat-resolution artwork is available.
    label_surface = font.render(label, True, color)
    scale = 1.0 + 0.12 * math.sin(progress * math.pi * 4)
    scaled_size = (
        max(1, int(label_surface.get_width() * scale)),
        max(1, int(label_surface.get_height() * scale)),
    )
    label_surface = pygame.transform.smoothscale(label_surface, scaled_size)
    surface.blit(
        label_surface,
        (
            WINDOW_WIDTH // 2 - label_surface.get_width() // 2,
            WINDOW_HEIGHT // 2 - label_surface.get_height() // 2,
        ),
    )


hovered_compartment = None
current_time = 0

running = True
while running:
    current_time = pygame.time.get_ticks()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    hovered_compartment = None
    if (
        game_state.screen == Screen.COMBAT
        and game_state.is_player_turn()
        and not game_state.combat_resolution_active()
    ):
        hovered_compartment = get_compartment_at(enemy, mouse_x, mouse_y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                game_state.toggle_debug()
                apply_debug_to_ships()
                if not game_state.debug_mode:
                    debug_auto_kill = False
            elif (
                event.key == pygame.K_SPACE
                and game_state.screen == Screen.COMBAT
                and game_state.is_player_turn()
                and not game_state.combat_resolution_active()
            ):
                perform_fire()
            elif (event.key == pygame.K_d
                  and game_state.debug_mode
                  and game_state.screen == Screen.COMBAT
                  and not game_state.combat_resolution_active()):
                debug_auto_kill = not debug_auto_kill
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state.screen == Screen.TITLE:
                start_rect, options_rect, quit_rect = title_button_rects()
                if start_rect.collidepoint(mouse_x, mouse_y):
                    start_new_run()
                elif options_rect.collidepoint(mouse_x, mouse_y):
                    options_message_visible = True
                elif quit_rect.collidepoint(mouse_x, mouse_y):
                    running = False
            elif game_state.screen == Screen.COMBAT:
                if game_state.is_player_turn() and not game_state.combat_resolution_active():
                    if handle_combat_consumable_click(mouse_x, mouse_y):
                        pass
                    elif flee_button_rect().collidepoint(mouse_x, mouse_y) and game_state.turn_count >= 2:
                        perform_flee()
                    elif fire_button_rect().collidepoint(mouse_x, mouse_y) and game_state.selected_compartment:
                        perform_fire()
                    elif hovered_compartment:
                        controller.select_compartment(hovered_compartment)
                if (
                    game_state.debug_mode
                    and not game_state.combat_resolution_active()
                    and debug_kill_button_rect().collidepoint(mouse_x, mouse_y)
                ):
                    debug_auto_kill = not debug_auto_kill
            elif game_state.screen == Screen.COMBAT_RESULT:
                if continue_button_rect().collidepoint(mouse_x, mouse_y):
                    controller.continue_from_combat_result()
            elif game_state.screen == Screen.NON_COMBAT_ACTION:
                for action, rect in zip(NON_COMBAT_ACTIONS, action_button_rects()):
                    if (
                        rect.collidepoint(mouse_x, mouse_y)
                        and action.is_available(run_state, player)
                    ):
                        old_enemy = enemy
                        controller.choose_non_combat_action(action.key)
                        sync_controller_refs_and_sprites(old_enemy)
                        break
            elif game_state.screen == Screen.FIELD_REPAIR:
                destroyed = destroyed_player_compartments()
                for compartment, rect in zip(
                    destroyed, field_repair_button_rects(destroyed)
                ):
                    if rect.collidepoint(mouse_x, mouse_y):
                        old_enemy = enemy
                        controller.apply_field_repair(compartment)
                        sync_controller_refs_and_sprites(old_enemy)
                        break
                if field_repair_back_rect().collidepoint(mouse_x, mouse_y):
                    controller.back_from_field_repair()
            elif game_state.screen == Screen.SHOP:
                for item, (card, buy) in zip(SHOP_ITEMS, shop_row_rects()):
                    if buy.collidepoint(mouse_x, mouse_y):
                        buy_item(item)
                        break
                if leave_shop_button_rect().collidepoint(mouse_x, mouse_y):
                    start_next_combat()
            elif game_state.screen in (Screen.GAME_OVER, Screen.VICTORY):
                if quit_button_rect().collidepoint(mouse_x, mouse_y):
                    game_state.screen = Screen.TITLE
                    options_message_visible = False

    if (
        game_state.screen == Screen.COMBAT
        and not game_state.combat_resolution_active()
        and player.alive()
        and enemy.alive()
        and game_state.is_enemy_turn()
        and game_state.enemy_target is not None
    ):
        controller.resolve_enemy_turn(current_time, force=game_state.debug_mode)

    controller.update_combat(current_time)

    sprites.update()

    if game_state.screen == Screen.TITLE:
        render_title()

    elif game_state.screen == Screen.COMBAT:
        screen.fill((20, 20, 40))
        sprites.draw(screen)

        if player.alive():
            draw_hp_bar(screen, player, "Player")
            draw_morale_bar(screen, player)
        if enemy.alive():
            draw_enemy_hp_bar(screen, enemy, game_state.turn_count, debug=game_state.debug_mode)
            if game_state.debug_mode:
                draw_morale_bar(screen, enemy)

        if game_state.last_hit_compartment and current_time - game_state.last_hit_time < 400:
            hit_rect = compartment_screen_rect(
                player if game_state.last_hit_compartment in player.compartments else enemy,
                game_state.last_hit_compartment,
            )
            flash_surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
            flash_surf.set_alpha(100)
            flash_surf.fill((255, 255, 255))
            screen.blit(flash_surf, hit_rect.topleft)

        resolving_combat = game_state.combat_resolution_active()

        if hovered_compartment and game_state.is_player_turn() and not resolving_combat:
            hover_rect = compartment_screen_rect(enemy, hovered_compartment)
            pygame.draw.rect(screen, (255, 255, 255), hover_rect, 2)

        if (
            game_state.selected_compartment
            and game_state.is_player_turn()
            and not resolving_combat
        ):
            select_rect = compartment_screen_rect(enemy, game_state.selected_compartment)
            pygame.draw.rect(screen, (255, 255, 0), select_rect, 2)
            target_name = (
                game_state.selected_compartment.name
                if enemy.is_compartment_visible(game_state.selected_compartment)
                else "Unknown compartment"
            )
            target_text = small_font.render(
                f"Targeting: {target_name}", True, (255, 255, 0)
            )
            screen.blit(target_text, (WINDOW_WIDTH // 2 - target_text.get_width() // 2, 60))

        if (
            game_state.is_enemy_turn()
            and not resolving_combat
            and game_state.enemy_target is not None
            and game_state.enemy_target_acquired(current_time)
        ):
            enemy_target_rect = compartment_screen_rect(player, game_state.enemy_target)
            pygame.draw.rect(screen, (220, 60, 60), enemy_target_rect, 2)

        if not resolving_combat:
            draw_fire_button(screen, game_state)
            draw_flee_button(screen, game_state)
            draw_combat_consumables(screen, game_state)
        if game_state.debug_mode and not resolving_combat:
            label = "Auto-Kill: ON" if debug_auto_kill else "Auto-Kill (D)"
            bg = (180, 140, 0) if debug_auto_kill else (50, 100, 180)
            border = (220, 180, 0) if debug_auto_kill else (80, 140, 220)
            rect = debug_kill_button_rect()
            pygame.draw.rect(screen, bg, rect)
            pygame.draw.rect(screen, border, rect, 2)
            lbl_surf = small_font.render(label, True, (255, 255, 255))
            screen.blit(lbl_surf, (rect.centerx - lbl_surf.get_width() // 2,
                                   rect.centery - lbl_surf.get_height() // 2))
        draw_debug_hud(screen, player, enemy, game_state, run_state)

        if resolving_combat:
            draw_combat_resolution(screen, game_state, current_time)
        else:
            turn_text = "Your Turn" if game_state.is_player_turn() else "Enemy Turn"
            turn_surface = font.render(turn_text, True, (200, 200, 200))
            screen.blit(turn_surface, (WINDOW_WIDTH // 2 - turn_surface.get_width() // 2, 20))

    elif game_state.screen == Screen.COMBAT_RESULT:
        render_combat_result()

    elif game_state.screen == Screen.NON_COMBAT_ACTION:
        render_non_combat_action()

    elif game_state.screen == Screen.FIELD_REPAIR:
        render_field_repair()

    elif game_state.screen == Screen.SHOP:
        render_shop()

    elif game_state.screen == Screen.GAME_OVER:
        render_game_over()

    elif game_state.screen == Screen.VICTORY:
        render_victory()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
