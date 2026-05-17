# Roadmap

Long-term feature plan. Agents: consult this when BACKLOG is empty or when pulling the next feature into the workbench.

---

## Crew & Morale

- [ ] Add `morale` attribute (0–100) to Player entity (default 50)
- [ ] **Morale events:**
  - Taking damage: morale -= 10
  - Destroying enemy compartment: morale += 15
  - Crew compartment destroyed: morale -= 25
- [ ] **Morale effects on accuracy:** +2% per 10 morale above 50 baseline (and -2% per 10 below)
- [ ] Morale drift: +1 per turn while below 50, -1 per turn while above 50
- [ ] Visual feedback: render morale bar above player ship

---

## Upgrades

- [ ] Create `Upgrade` data structure: `name`, `upgrade_type` (crew / ship), `effect_key` (accuracy, fire_rate, hull_hp), `effect_value`, `cost`
- [ ] Create upgrade database: list of 3–4 crew upgrades and 3–4 ship upgrades
- [ ] **Upgrade application:** create `apply_upgrade(entity, upgrade)` function
  - Crew upgrades modify entity attributes (morale_recovery_rate, accuracy_bonus)
  - Ship upgrades modify entity attributes (max_hp, damage_output)
- [ ] Store applied upgrades on entity to prevent double-application
- [ ] UI: display available upgrades and current upgrades (text-based initially)

---

## Enemy Intelligence

- [ ] **Hidden state:** compartments start with `revealed=False`
- [ ] **Revelation triggers:**
  - On hit: reveal the compartment that was struck
  - Time in combat: reveal enemy morale and overall HP after 5 turns
  - Specific scan action: reveal all compartments (costs action point, high morale requirement)
- [ ] **Display:** render revealed compartments normally; hidden compartments as "???" or obscured
- [ ] Information persistence: keep revealed state across the entire encounter
