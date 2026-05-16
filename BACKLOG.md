# Backlog

Prioritized task list for **didactic-happiness**. Read the **Doing** section to see the current focus. The **Up next** section contains immediately actionable tasks. **Later** tasks are planned but not yet started.

---

## Doing

- [ ] Add movement input for Player (arrow keys or WASD)

---

## Up next — Entities (Movement)

- [ ] Implement Player movement with arrow keys (up/down/left/right, clamped to screen bounds)
- [ ] Test smooth movement (no stuttering, respects FPS cap)

---

## Later — Entities (Compartments)

- [ ] Design sprite partition scheme: 3×3 grid mapping to hull, crew, weapons regions
- [ ] Create compartment data structure: list of `Compartment(name, x, y, width, height, system_type)`
- [ ] Render compartments as visual overlays (colored rectangles or borders)
- [ ] Link compartments to Player and Enemy classes

---

## Later — Combat

- [ ] Implement `Projectile` class: position, velocity, collision detection
- [ ] Shooting: on player input, spawn projectile from player position toward target
- [ ] Hit detection: check projectile collision with enemy compartments
- [ ] **Accuracy system:** RNG roll (0–100) against accuracy threshold (modified by morale and upgrades)
- [ ] **Damage application:** on hit, reduce target compartment HP and entity HP
- [ ] Projectile cleanup: remove projectile on hit or off-screen

---

## Later — Health

- [ ] Add `hp` and `max_hp` attributes to Player and Enemy
- [ ] Add `health()` method to reduce HP (used by damage system)
- [ ] Destruction trigger: when `hp <= 0`, call `kill()` on entity
- [ ] **Compartment HP:** each compartment has its own `hp` and `max_hp`
- [ ] **System disabling:** when compartment HP reaches 0, disable its associated system (e.g., weapons system can't fire)
- [ ] Visual feedback: render HP bars for player and enemy

---

## Later — Crew & Morale

- [ ] Add `morale` attribute (0–100) to Player entity
- [ ] **Morale events:**
  - Taking damage: morale -= 10
  - Destroying enemy compartment: morale += 15
  - Crew death: morale -= 25
- [ ] **Morale effects:**
  - Accuracy modifier: +2% per 10 morale (50 morale = base, 100 morale = +10%)
  - Fire rate modifier: +1 action point per 25 morale (threshold-based: 25→+1, 50→+2, etc.)
  - Action gating: some actions only available if morale > threshold
- [ ] Morale drift: passive recovery toward 50 over time (1 point per 10 seconds)
- [ ] Visual feedback: render morale bar

---

## Later — Upgrades

- [ ] Create `Upgrade` data structure: `name`, `upgrade_type` (crew / ship), `effect_key` (accuracy, fire_rate, hull_hp), `effect_value`, `cost`
- [ ] Create upgrade database: list of 3–4 crew upgrades and 3–4 ship upgrades
- [ ] **Upgrade application:** create `apply_upgrade(entity, upgrade)` function
  - Crew upgrades modify entity attributes (morale_recovery_rate, accuracy_bonus)
  - Ship upgrades modify entity attributes (max_hp, damage_output)
- [ ] Store applied upgrades on entity to prevent double-application
- [ ] UI: display available upgrades and current upgrades (text-based initially)

---

## Later — Enemy Intelligence

- [ ] **Hidden state:** compartments start with `revealed=False`
- [ ] **Revelation triggers:**
  - On hit: reveal the compartment that was struck
  - Time in combat: reveal enemy morale and overall HP after 5 turns
  - Specific scan action: reveal all compartments (costs action point, high morale requirement)
- [ ] **Display:** render revealed compartments normally; hidden compartments as "???" or obscured
- [ ] Information persistence: keep revealed state across the entire encounter

---

## Reference

See [DONE.md](DONE.md) for completed tasks. Consult it only when prior work is specifically relevant to your current task.

See [README.md](README.md) for project concept, design decisions, and system specifications.
