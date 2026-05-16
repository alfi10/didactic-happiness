# didactic-happiness

A top-down 2D tactical space combat game.

---

## Concept

**didactic-happiness** is a tactical turn-based space combat game inspired by FTL. You command a starship and must defeat enemy vessels by managing your crew's morale, upgrading your systems, and learning about your opponent through combat. Your ship is fixed on the left side of the screen; the enemy is displayed on the right. Each decision counts: which systems to prioritize, whether to target compartments or push for total destruction, how to manage crew morale. Victory is won through tactics, not reflexes.

---

## Core Gameplay Loop (Per Turn)

1. **Your Turn** — Select a target compartment on the enemy ship. Choose an action (fire at that compartment).
2. **Fire & Resolve** — Your attack rolls for accuracy. On hit, damage applies to the target compartment and enemy HP.
3. **Enemy Turn** — The enemy selects a target compartment on your ship and fires. Accuracy and damage apply based on their morale and upgrades.
4. **Learn** — As combat progresses, you discover details about the enemy ship — its hull layout, morale level, upgrade tier. Information is a weapon.
5. **Manage** — Each turn, crew morale drifts slightly (toward 50). Between encounters, purchase upgrades and plan your strategy.

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

### Upgrades
Two upgrade tracks:

**Crew Upgrades:**
- Morale recovery rate (passive regeneration)
- Accuracy bonuses
- Fire rate bonuses
- Action point increases

**Ship Upgrades:**
- Hull HP (more health)
- Weapon damage (hit harder)
- Compartment shielding (localized protection)
- System redundancy (disabled systems don't fully disable)

Upgrades are earned between encounters or purchased with in-game currency.

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
- **Entry point:** `python main.py`

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start the game
python main.py
```

---

## References

- **Agent guide:** [CLAUDE.md](CLAUDE.md) — conventions, structure, how to run this project
- **Task backlog:** [BACKLOG.md](BACKLOG.md) — what to build next
- **Workflow:** [WORKFLOW.md](WORKFLOW.md) — branching, commits, and shipping rules
- **Completed work:** [DONE.md](DONE.md) — archive of finished tasks
