# Roadmap

Long-term feature plan. Agents: consult this when BACKLOG is empty or when pulling the next feature into the workbench.

---

## Combat polish (from playtest feedback)

- [ ] **Debug mode toggle:** dedicated key (e.g. `F1` or backtick) to reveal all gameplay data — both ships' precise HP, morale, accuracy modifier, all compartments revealed. Toggleable on/off. Useful for development and balance tuning.
- [ ] **Fire button accepts mouse click:** clicking the on-screen "Fire (space)" button should fire just like pressing Space. Hit-test the button rect on `MOUSEBUTTONDOWN` and trigger the same path. Keep Space working.
- [ ] **Lower enemy base accuracy:** player and enemy currently share `CombatSystem.BASE_ACCURACY = 70` (in [src/combat.py](src/combat.py)). Split into per-ship base accuracy so enemy can be tuned independently — target value for enemy: **TODO (fill in)**.
- [ ] **Reposition fire button:** currently centered horizontally and vertically at `(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)`. Move to lower part of the screen (horizontally centered, e.g. `y = WINDOW_HEIGHT - 70`).

---

## Upgrades

**Note:** Upgrades is on hold until the game supports non-combat screens (shop, between-encounter view). Re-evaluate when the project gains a screen state machine — without somewhere to spend currency, upgrades have no place to live.

- [ ] Create `Upgrade` data structure: `name`, `upgrade_type` (crew / ship), `effect_key` (accuracy, fire_rate, hull_hp), `effect_value`, `cost`
- [ ] Create upgrade database: list of 3–4 crew upgrades and 3–4 ship upgrades
- [ ] **Upgrade application:** create `apply_upgrade(entity, upgrade)` function
  - Crew upgrades modify entity attributes (morale_recovery_rate, accuracy_bonus)
  - Ship upgrades modify entity attributes (max_hp, damage_output)
- [ ] Store applied upgrades on entity to prevent double-application
- [ ] UI: display available upgrades and current upgrades (text-based initially)
