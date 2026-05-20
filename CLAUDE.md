# didactic-happiness — Agent Guide

## Project

**didactic-happiness** is a Pygame-based tactical space combat game. The player commands a ship through a series of turn-based combat encounters, earning **Score** by winning fights. Score is both the win condition (reach 120) and the shop currency — spending it on upgrades or consumables makes you survive longer but delays victory.

**Run loop:** Combat → Combat Result → Non-Combat Action → (Shop every 5th combat) → New Enemy → repeat.

**Language:** Python 3.x  
**Entry point:** `python main.py`

---

## Run

```bash
# Install dependencies
uv sync

# Start the game
uv run main.py
```

**Project metadata:** dependencies live in `pyproject.toml`.

**Environment:** Standard Python. No special variables required.

---

## Structure

```
didactic-happiness/
  main.py                 # Entry point; pygame init, main game loop, screen dispatch
  src/
    entities.py           # Ship, Player, Enemy — HP, morale, accuracy stats
    combat.py             # CombatSystem: fire(), accuracy roll, damage, destroy chance
    compartments.py       # Compartment dataclass; 3x3 ship grid, per-type HP/effects
    game_state.py         # GameState: turn state, screen enum (added in M2), flee state
    intel.py              # Enemy HP fog-of-war; hidden until turn 5, precise from turn 10
    run_state.py          # RunState: Score, combat_count, upgrades, consumables (added in M1)
    non_combat.py         # NonCombatAction set — Patch Hull, Field Repair, Rally, Recon (M3)
    shop.py               # ShopItem catalogue and shop item effect hooks (M5/M6)
    enemies.py            # EnemyTemplate + spawn_enemy_for_combat() factory (M7)
  assets/                 # Sprites, images
  tests/                  # Unit tests
  pyproject.toml          # Project metadata and dependencies
```

_Files marked (M#) do not exist yet; they are created in the listed milestone._

---

## Conventions

- **Naming:** `snake_case` for functions and variables, `PascalCase` for classes
- **Classes:** One class per file if it will grow; keep small ones grouped
- **Pygame:** Use `pygame.sprite.Group` for entity management; event loop in `main.py`
- **Magic numbers:** Extract to named constants at file top
- **Commit hygiene:** See `WORKFLOW.md`

---

## References

- **Project design & decisions:** [README.md](README.md) — design decisions, behavior specs, and project-specific notes
- **Roadmap:** [ROADMAP.md](ROADMAP.md) — completed milestones and the next feature to build
- **How to ship:** [WORKFLOW.md](WORKFLOW.md) — commit, branching, and testing rules
- **Past work:** [DONE.md](DONE.md) — consult only when prior context is relevant
