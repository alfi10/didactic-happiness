# didactic-happiness

A top-down 2D tactical space combat game.

---

## Concept

**didactic-happiness** is a tactical RPG-lite space shooter where crew management and strategic positioning matter more than reflexes. You command a starship and must defeat enemy vessels by managing your crew's morale, upgrading your systems, and learning about your opponent through combat.

Each decision counts: where to position your ship, which systems to prioritize, whether to push the advantage or consolidate morale. Victory is won through tactics, not twitch reflexes.

---

## Core Gameplay Loop

1. **Prepare** — Position your ship on the tactical grid. Allocate crew to stations (weapons, shields, engines).
2. **Engage** — Choose your targets and fire. Attack specific compartments of the enemy ship.
3. **Respond** — The enemy attacks in turn. Accuracy and damage depend on crew morale, upgrades, and positioning.
4. **Learn** — As combat progresses, you discover details about the enemy ship — its hull layout, morale level, upgrade tier. Information is a weapon.
5. **Manage** — Between encounters (or during lulls), recover morale, purchase upgrades, and plan your next move.

---

## Key Systems

### Entities
**Player** and **Enemy** are sprite-based ships on a top-down grid. Each ship is divided into **compartments** — visual regions representing different systems:
- **Hull:** structural integrity, target zone
- **Crew Stations:** where crew assign morale and action
- **Weapons:** firing systems, accuracy multiplier

Compartments reflect game state visually: damage darkens them, morale glows, destroyed systems vanish.

### Combat
Shooting is **player-directed**, not automatic. You decide:
- **When** to fire (once per turn, or based on action points)
- **Where** to target (hull, weapons, crew station)
- **How much ammo/energy** to commit

**Accuracy** is computed per shot: base RNG roll + modifiers from crew morale, upgrades, and relative positioning. Miss or hit — both have narrative weight.

**Damage** applies to the target compartment and the entity's HP. Destroying a compartment disables its system before destroying the whole ship.

### Health
Each entity has **HP** (hit points). Damage reduces it. When HP reaches 0, the entity is destroyed.

**Compartments** also have individual HP pools. Disabling a compartment disables its system (e.g., destroying weapons prevents firing) without destroying the ship.

### Crew Morale
**Morale** is a 0–100 value representing your crew's state. It affects:
- **Accuracy:** higher morale = better hit chance
- **Fire rate:** higher morale = faster or more actions per turn
- **Action availability:** some actions are only available at high morale (risky maneuvers, overcharge)

**Events** change morale:
- Taking damage: morale drops
- Destroying enemy compartment: morale rises
- Crew loss: morale drops significantly
- Time spent idle: morale drifts toward 50 (neutral)

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
