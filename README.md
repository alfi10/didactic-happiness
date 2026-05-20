# didactic-happiness

A top-down 2D tactical space combat game.

---

## Concept

**didactic-happiness** is a tactical turn-based space combat game inspired by FTL. You command a starship through a series of enemy encounters, earning **Score** by winning fights. Score is both the win condition — reach 120 to escape — and your shop currency. Spending it on upgrades or consumables makes you more likely to survive, but delays the finish line, creating a constant tradeoff: push forward or invest to live longer?

Each encounter plays out on a shared grid: your ship on the left, the enemy on the right. You fire at compartments, manage crew morale, and slowly learn the enemy's hidden layout. Victory is won through tactics, not reflexes.

---

## Gameplay Loops

### Per Turn (in combat)

1. **Your Turn** — Select a target compartment on the enemy ship and fire.
2. **Fire & Resolve** — Accuracy rolls; on hit, damage applies to the compartment and enemy HP. 33% chance of instant destruction.
3. **Enemy Turn** — The enemy fires back; their accuracy is modified by morale and the intel fog lifts as turns pass.
4. **Learn** — Enemy HP stays hidden until turn 5; precise readings from turn 10. Information is a weapon.
5. **Flee (optional)** — Available from turn 3 onward. Always succeeds; costs 15 morale carried into the next fight and earns 0 Score.

### Between Combats (run loop)

```
Combat → Combat Result → Non-Combat Action → [Shop every 5th] → New Enemy → repeat
```

6. **Combat Result** — Win earns Score (`tier_base + HP bonus`). Defeat ends the run.
7. **Non-Combat Action** — Pick one free action: Patch Hull (+30 HP), Field Repair (restore a compartment), Rally Crew (morale → 70), or Recon Drone (reveal next enemy layout).
8. **Shop** — Appears after combats 5, 10, 15… Spend Score on permanent upgrades or single-use consumables.
9. **New Enemy** — A fresh enemy ship spawns for the next combat. Tiered enemy progression is planned for a later milestone.
10. **Win** — Reach Score 120 before your ship is destroyed.

---

## Key Systems

### Entities
**Player** and **Enemy** are sprite-based ships on a top-down grid. Each ship is divided into **compartments** — visual regions representing different systems:
- **Hull:** structural integrity, target zone
- **Crew Stations:** where crew assign morale and action
- **Weapons:** firing systems, accuracy multiplier

Compartments reflect game state visually: damage darkens them, morale glows, destroyed systems vanish.

### Combat
Combat is **turn-based and tactical**. Each turn:
- **You act first:** select a target compartment on the enemy ship
- **Accuracy** is computed: base RNG roll (0–100) vs. accuracy threshold, modified by your morale and upgrades
- **On hit:** damage applies to the target compartment and enemy HP
- **Visual feedback:** target compartment briefly highlights to show damage
- **Enemy responds:** they select a random or scripted compartment on your ship and fire
- **Accuracy calculation:** enemy accuracy is modified by their morale and upgrades

### Health
Each entity has **HP** (hit points). Damage reduces it. When HP reaches 0, the entity is destroyed.

**Compartments** also have individual HP pools. Disabling a compartment disables its system (e.g., destroying weapons prevents firing) without destroying the ship.

### Crew Morale
**Morale** is a 0–100 value representing your crew's state. It affects:
- **Accuracy:** higher morale = better hit chance
- **Damage:** higher morale = higher damage output
- **Special actions:** some actions are only available at high morale (risky maneuvers, focus fire)

**Events** change morale:
- Taking damage: morale -= 10
- Destroying enemy compartment: morale += 15
- Crew loss: morale -= 25
- Turn passage: morale drifts passively (+1 per turn if below 50, -1 per turn if above 50)

### Score

Score is earned by winning combats and spent at the shop. It is the win condition (target: 120) and the only currency — both roles exist simultaneously.

- **Win reward:** `tier_base + floor(remaining_hp% × 10)`. Tier bases: T1 = 12, T2 = 18, T3 = 25.
- **Flee reward:** 0.
- **Spending:** shop only. Non-combat actions are free.

### Shop & Upgrades

The shop opens every 5th combat. The current build includes the full shop screen, fixed inventory, Score spending, stack limits, and persistent purchase tracking in `RunState`. Item combat effects are the next milestone, so purchases are currently recorded but still use stubbed `apply()` functions.

**Upgrades (stackable):**

| Name | Cost | Effect | Max |
|------|------|--------|-----|
| Weapon Calibration | 12 | +5 base accuracy | ×3 |
| Reinforced Hull | 18 | +20 max HP | ×3 |
| Targeting AI | 25 | +8% destroy chance | ×2 |

**Consumables:**

| Name | Cost | Effect |
|------|------|--------|
| Repair Kit | 8 | +25 HP, usable in combat |
| Morale Broadcast | 6 | Morale → 80, usable in combat |
| Sensor Ping | 5 | Reveal one hidden enemy compartment |

### Enemy Intelligence
The enemy ship starts mostly **hidden**. As you fight:
- **Direct hits** reveal the compartment you struck
- **Time in combat** reveals enemy morale level and overall HP
- **Specific actions** (scanning, targeting) can reveal specific systems

Information discovered persists — you learn the enemy's composition, strengths, and weaknesses over the encounter.

---

## Tech Stack

- **Language:** Python 3.x
- **Engine:** Pygame
- **Package metadata:** `pyproject.toml`
- **Entry point:** `python main.py`

---

## How to Run

```bash
# Install dependencies
uv sync

# Start the game
uv run main.py
```

If you prefer plain `pip`, install `pygame` manually and run `python main.py`.

---

## Current Status

Milestones 1-5 are implemented: score tracking, post-combat flow, non-combat actions, fleeing, and the shop shell. Milestone 6 is next, which will make upgrades and consumables affect combat directly.

---

## References

- **Agent guide:** [AGENTS.md](AGENTS.md) and [CLAUDE.md](CLAUDE.md) — conventions, structure, and execution notes
- **Active task:** [WORKBENCH.md](WORKBENCH.md) — what's being built right now
- **Feature roadmap:** [ROADMAP.md](ROADMAP.md) — upcoming milestones in order
- **Workflow:** [WORKFLOW.md](WORKFLOW.md) — branching, commits, and shipping rules
- **Completed work:** [DONE.md](DONE.md) — archive of finished tasks
