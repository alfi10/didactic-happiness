# Done

Completed tasks. Archived for reference only; consult when prior work is specifically relevant to your current task.

## Entities — Compartments

- [x] Design sprite partition scheme: 3×3 grid mapping to hull, crew, weapons regions
- [x] Create compartment data structure: list of `Compartment(name, x, y, width, height, system_type)`
- [x] Render compartments as visual overlays (colored rectangles or borders)
- [x] Link compartments to Player and Enemy classes

## Combat

- [x] Player selects target compartment on enemy ship (mouse click)
- [x] Player fires: accuracy roll (0–100 vs threshold) resolves immediately (hit or miss)
- [x] On hit: damage applied to selected compartment and enemy HP
- [x] Visual feedback: brief flash on hit compartment
- [x] Enemy turn: enemy selects random player compartment and fires back
- [x] Accuracy system: RNG roll (0–100) against threshold

## Health

- [x] Add `hp` and `max_hp` attributes to Player and Enemy (ship-level HP)
- [x] Add `take_damage(amount)` method on Ship that reduces HP
- [x] Destruction trigger: when ship `hp <= 0`, call `kill()` on entity
- [x] System disabling: when compartment HP reaches 0, set `active=False`
- [x] Visual feedback: render HP bars above each ship
- [x] Wire combat damage into ship HP

## Combat balancing + destruction visuals

- [x] Base damage raised to 10
- [x] 33% chance hit instantly destroys compartment
- [x] Destruction adds +10 bonus damage to ship HP
- [x] Hits on destroyed compartments deal 5 damage to ship only
- [x] Destroyed compartments render in dimmed color (30% intensity)
- [x] Ship.refresh() re-renders compartments after state changes

## Crew & Morale

- [x] Morale attribute (0–100, default 50) on Ship
- [x] Morale events: -10 on hit taken, -25 extra on own crew compartment destroyed, +15 for attacker destroying enemy compartment
- [x] Accuracy modifier: +2% per 10 morale above 50 baseline (and inverse below)
- [x] Morale drift: +1/turn below 50, -1/turn above 50, triggered after each full exchange
- [x] Morale bar rendered above player ship

## Per-compartment-type destruction effects

- [x] Per-type destruction bonus damage dict: HULL 10, CREW 10, CORE 20, WEAPONS 5
- [x] Destroyed weapons compartments apply -15% accuracy penalty (stacking)

## Enemy Intelligence

- [x] Compartments have `revealed` flag (default True, Enemy overrides to False)
- [x] Unrevealed compartments render in gray
- [x] Hits reveal the struck compartment
- [x] Enemy HP hidden before turn 5
- [x] Enemy HP shown bracketed (rounded up to nearest 20) on turns 5–9
- [x] Enemy HP shown precisely from turn 10 onward
- [x] Turn count tracked in GameState

## Combat UX

- [x] "Fire (space)" button rendered at screen center: bright red with target, dim gray without, invisible during enemy turn
- [x] Enemy turn paced over 2 seconds: 1s acquiring (no indicator), 1s target locked (red border), then fire
- [x] CombatSystem.pick_enemy_target split from enemy_attack for staged resolution
