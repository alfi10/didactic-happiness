import pygame
import sys
from src.entities import Player, Enemy, CELL_SIZE, SHIP_SIZE
from src.enemies import spawn_enemy_for_combat
from src.game_state import GameState, Screen
from src.combat import CombatSystem
from src.intel import format_enemy_hp, display_hp_ratio, hp_visible
from src.run_state import RunState
from src.compartments import DESTROY_BONUS_DAMAGE, SystemType
from src.non_combat import ACTIONS as NON_COMBAT_ACTIONS
from src.shop import SHOP_ITEMS, use_repair_kit, use_morale_broadcast, use_sensor_ping

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
    total_h = len(NON_COMBAT_ACTIONS) * ACTION_SLOT_HEIGHT
    start_y = WINDOW_HEIGHT // 2 - total_h // 2
    cx = WINDOW_WIDTH // 2
    return [
        pygame.Rect(cx - ACTION_BUTTON_WIDTH // 2,
                    start_y + i * ACTION_SLOT_HEIGHT,
                    ACTION_BUTTON_WIDTH, ACTION_BUTTON_HEIGHT)
        for i in range(len(NON_COMBAT_ACTIONS))
    ]

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
    return [
        item for item in SHOP_ITEMS
        if item.kind == "consumable" and run_state.consumables.get(item.name, 0) > 0
    ]


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
player = Player(PLAYER_X, SHIP_Y)
enemy = spawn_enemy_for_combat(0, ENEMY_X, SHIP_Y)
sprites.add(player)
sprites.add(enemy)

game_state = GameState()
combat = CombatSystem()
run_state = RunState()
debug_auto_kill = False
options_message_visible = False

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

def draw_button(surface, rect, label):
    pygame.draw.rect(surface, (50, 100, 180), rect)
    pygame.draw.rect(surface, (80, 140, 220), rect, 2)
    text = small_font.render(label, True, (255, 255, 255))
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
    if not (game_state.is_player_turn() and game_state.turn_count >= 2):
        return
    run_state.register_flee()
    game_state.last_combat_result = "flee"
    game_state.clear_selection()
    game_state.clear_enemy_turn()
    game_state.screen = Screen.COMBAT_RESULT

def perform_fire():
    if not (game_state.is_player_turn() and game_state.selected_compartment):
        return
    if debug_auto_kill and game_state.debug_mode:
        debug_auto_hit()
        return
    hit, _ = combat.fire(game_state.selected_compartment, enemy, player)
    if hit:
        game_state.register_hit(game_state.selected_compartment, current_time)
    game_state.clear_selection()
    game_state.next_turn()
    target = combat.pick_enemy_target(enemy, player)
    game_state.start_enemy_turn(target, current_time)


def debug_auto_hit():
    if not (game_state.is_player_turn() and game_state.debug_mode):
        return
    target = game_state.selected_compartment
    if target is None or target not in enemy.compartments:
        target = next((c for c in enemy.compartments if c.active), None)
    if target is None:
        return
    target.revealed = True
    target.hp = 0
    target.active = False
    bonus = DESTROY_BONUS_DAMAGE[target.system_type]
    damage = CombatSystem.BASE_DAMAGE + bonus
    enemy.take_damage(damage)
    enemy.change_morale(-CombatSystem.HIT_MORALE_PENALTY)
    if target.system_type == SystemType.CREW:
        enemy.change_morale(-CombatSystem.CREW_DESTROYED_MORALE_PENALTY)
    enemy.refresh()
    player.change_morale(CombatSystem.DESTROY_ENEMY_MORALE_REWARD)
    game_state.register_hit(target, current_time)
    game_state.clear_selection()
    game_state.next_turn()
    e_target = combat.pick_enemy_target(enemy, player)
    game_state.start_enemy_turn(e_target, current_time)


def apply_debug_to_ships():
    enemy.force_reveal = game_state.debug_mode
    enemy.refresh()


def start_new_run():
    global player, enemy, game_state, run_state, debug_auto_kill, options_message_visible
    debug_mode = game_state.debug_mode
    sprites.empty()
    player = Player(PLAYER_X, SHIP_Y)
    enemy = spawn_enemy_for_combat(0, ENEMY_X, SHIP_Y)
    sprites.add(player, enemy)
    run_state = RunState()
    game_state = GameState()
    game_state.debug_mode = debug_mode
    game_state.reset_for_combat()
    debug_auto_kill = False
    options_message_visible = False
    apply_debug_to_ships()


def start_next_combat():
    global enemy
    sprites.remove(enemy)
    enemy = spawn_enemy_for_combat(run_state.combat_count, ENEMY_X, SHIP_Y)
    sprites.add(enemy)
    if game_state.debug_mode or run_state.scan_next_enemy:
        enemy.force_reveal = True
        enemy.refresh()
    run_state.scan_next_enemy = False
    game_state.reset_for_combat()
    game_state.last_combat_result = "win"
    penalty = run_state.consume_pending_morale_penalty()
    if penalty:
        player.change_morale(-penalty)


def get_item_stacks(item):
    if item.kind == "upgrade":
        return run_state.owned_upgrades.get(item.name, 0)
    return run_state.consumables.get(item.name, 0)

def can_buy(item):
    stacks = get_item_stacks(item)
    return (run_state.score >= item.cost and
            (item.max_stacks is None or stacks < item.max_stacks))

def buy_item(item):
    if not can_buy(item):
        return
    run_state.score -= item.cost
    item.apply(run_state, player)
    if item.kind == "upgrade":
        run_state.owned_upgrades[item.name] = get_item_stacks(item) + 1
    else:
        run_state.consumables[item.name] = get_item_stacks(item) + 1


def use_combat_consumable(item_name):
    if not (game_state.screen == Screen.COMBAT and game_state.is_player_turn()):
        return False
    if item_name == "Repair Kit":
        return use_repair_kit(run_state, player)
    if item_name == "Morale Broadcast":
        return use_morale_broadcast(run_state, player)
    if item_name == "Sensor Ping":
        return use_sensor_ping(run_state, enemy)
    return False


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
    screen.blit(header, (WINDOW_WIDTH // 2 - header.get_width() // 2, 40))
    for action, rect in zip(NON_COMBAT_ACTIONS, action_button_rects()):
        draw_button(screen, rect, action.name)
        desc = small_font.render(action.description, True, (140, 140, 160))
        screen.blit(desc, (WINDOW_WIDTH // 2 - desc.get_width() // 2, rect.bottom + 4))


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


hovered_compartment = None
current_time = 0

running = True
while running:
    current_time = pygame.time.get_ticks()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    hovered_compartment = None
    if game_state.screen == Screen.COMBAT and game_state.is_player_turn():
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
            elif event.key == pygame.K_SPACE and game_state.screen == Screen.COMBAT and game_state.is_player_turn():
                perform_fire()
            elif (event.key == pygame.K_d
                  and game_state.debug_mode
                  and game_state.screen == Screen.COMBAT):
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
                if game_state.is_player_turn():
                    if handle_combat_consumable_click(mouse_x, mouse_y):
                        pass
                    elif flee_button_rect().collidepoint(mouse_x, mouse_y) and game_state.turn_count >= 2:
                        perform_flee()
                    elif fire_button_rect().collidepoint(mouse_x, mouse_y) and game_state.selected_compartment:
                        perform_fire()
                    elif hovered_compartment:
                        game_state.select(hovered_compartment)
                if game_state.debug_mode and debug_kill_button_rect().collidepoint(mouse_x, mouse_y):
                    debug_auto_kill = not debug_auto_kill
            elif game_state.screen == Screen.COMBAT_RESULT:
                if continue_button_rect().collidepoint(mouse_x, mouse_y):
                    game_state.screen = Screen.NON_COMBAT_ACTION
            elif game_state.screen == Screen.NON_COMBAT_ACTION:
                for action, rect in zip(NON_COMBAT_ACTIONS, action_button_rects()):
                    if rect.collidepoint(mouse_x, mouse_y):
                        action.apply(run_state, player)
                        if run_state.combat_count % 5 == 0:
                            game_state.screen = Screen.SHOP
                        else:
                            start_next_combat()
                        break
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

    if game_state.screen == Screen.COMBAT and game_state.is_enemy_turn() and game_state.enemy_target is not None:
        if game_state.debug_mode or game_state.enemy_ready_to_fire(current_time):
            target = game_state.enemy_target
            hit, _ = combat.fire(target, player, enemy)
            if hit:
                game_state.register_hit(target, current_time)
            game_state.clear_enemy_turn()
            game_state.next_turn()
            game_state.increment_turn_count()
            player.drift_morale()
            enemy.drift_morale()

    if game_state.screen == Screen.COMBAT:
        if not enemy.alive():
            run_state.combat_count += 1
            run_state.award_combat_score(player.hp, player.max_hp, enemy.score_reward)
            if run_state.is_complete():
                game_state.screen = Screen.VICTORY
            else:
                game_state.last_combat_result = "win"
                game_state.screen = Screen.COMBAT_RESULT
        elif not player.alive():
            game_state.screen = Screen.GAME_OVER

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

        if hovered_compartment and game_state.is_player_turn():
            hover_rect = compartment_screen_rect(enemy, hovered_compartment)
            pygame.draw.rect(screen, (255, 255, 255), hover_rect, 2)

        if game_state.selected_compartment and game_state.is_player_turn():
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
            and game_state.enemy_target is not None
            and game_state.enemy_target_acquired(current_time)
        ):
            enemy_target_rect = compartment_screen_rect(player, game_state.enemy_target)
            pygame.draw.rect(screen, (220, 60, 60), enemy_target_rect, 2)

        draw_fire_button(screen, game_state)
        draw_flee_button(screen, game_state)
        draw_combat_consumables(screen, game_state)
        if game_state.debug_mode:
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

        turn_text = "Your Turn" if game_state.is_player_turn() else "Enemy Turn"
        turn_surface = font.render(turn_text, True, (200, 200, 200))
        screen.blit(turn_surface, (WINDOW_WIDTH // 2 - turn_surface.get_width() // 2, 20))

    elif game_state.screen == Screen.COMBAT_RESULT:
        render_combat_result()

    elif game_state.screen == Screen.NON_COMBAT_ACTION:
        render_non_combat_action()

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
