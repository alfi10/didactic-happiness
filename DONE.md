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
