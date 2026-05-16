# didactic-happiness — Agent Guide

## Project

**didactic-happiness** is a Pygame-based space shooter game. The player controls a ship and must defeat enemies through combat, managing crew morale and upgrades.

**Language:** Python 3.x  
**Entry point:** `python main.py`

---

## Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start the game
python main.py
```

**Requirements file** (`requirements.txt`): Add `pygame` and any other dependencies needed.

**Environment:** Standard Python. No special variables required.

---

## Structure

```
didactic-happiness/
  main.py                 # Entry point; initializes pygame, main game loop
  src/
    entities.py           # Player, Enemy classes
    combat.py             # Shooting, accuracy, damage
    health.py             # Health/HP system
    ...
  assets/                 # Sprites, images
  tests/                  # Unit tests (if applicable)
```

_Note: directories not yet created can be added as features are built._

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
- **Active workbench:** [WORKBENCH.md](WORKBENCH.md) — current task (Doing) and next tasks (Up next)
- **Long-term plan:** [ROADMAP.md](ROADMAP.md) — upcoming features; consult when pulling next work into WORKBENCH
- **How to ship:** [WORKFLOW.md](WORKFLOW.md) — commit, branching, and testing rules
- **Past work:** [DONE.md](DONE.md) — consult only when prior context is relevant
