# Roadmap

Long-term feature plan. Agents: consult this when BACKLOG is empty or when pulling the next feature into the workbench.

The goal of this roadmap is to **close the game loop**: combat → result → non-combat action → (shop every 5th) → new enemy → repeat until target Score or destruction. **Score is both the win condition and the shop currency.**

Design pillars (locked in):
- **Run length:** medium, ~9–12 combats, target Score **120**.
- **Non-combat actions:** free. The shop is the only Score sink.
- **Flee:** always succeeds, with morale penalty; still counts toward shop cadence.

Pull milestones in order — each one builds on the previous. MVP = M1 + M2 + M3 (closed loop, no shop yet).

Full design rationale lives in the approved plan at `~/.claude/plans/i-want-to-close-dreamy-puzzle.md`.

---

## Milestone 1 — Run State & Score Tracking

**Goal:** introduce `RunState`; track Score and combat_count; check win/loss.

- [x] Create `src/run_state.py` with `RunState` dataclass (`combat_count`, `score`, `target_score=120`, `owned_upgrades`, `consumables`, `pending_morale_penalty`, `scan_next_enemy`)
- [x] Instantiate `RunState` in `main.py` startup
- [x] On enemy HP ≤ 0: increment `combat_count`, award Score = `tier_base + hp_bonus`
  - Tier base: combats 1–4 = 12, 5–9 = 18, 10+ = 25
  - HP bonus: `floor(remaining_hp_pct * 10)` (max +10)
- [x] On player HP ≤ 0: freeze game and print "Game Over" placeholder
- [x] On Score ≥ target: freeze game and print "Victory" placeholder
- [x] Add `combat_count` and `score` to the debug HUD (F1)

**Accepts:** debug HUD shows the counters; reaching 120 prints victory; dying prints game over.

---

## Milestone 2 — Screen State Machine & Combat Result Screen

**Goal:** introduce a `Screen` enum and the post-combat transition.

- [x] Add `Screen` enum to `src/game_state.py`: `COMBAT`, `COMBAT_RESULT`, `GAME_OVER`, `VICTORY` (more added in later milestones)
- [x] Refactor `main.py` main loop to dispatch render/input by `game_state.screen`
- [x] Build `COMBAT_RESULT` screen: shows Win/Flee/Defeat, Score delta, `score / target`, "Continue" button
- [x] Build `GAME_OVER` and `VICTORY` screens with final stats + "Back to Menu" (menu can be a placeholder for now)
- [x] Combat end transitions to the correct screen based on win/loss/target

**Accepts:** game flows COMBAT → COMBAT_RESULT → (back to COMBAT with a fresh enemy) without crashes.

---

## Milestone 3 — Non-Combat Action Screen

**Goal:** insert mandatory non-combat action between combats. **(Closes the MVP loop.)**

- [x] Create `src/non_combat.py` with `NonCombatAction` dataclass and 4 instances:
  - **Patch Hull** — restore 30 HP (capped at max)
  - **Field Repair** — restore one destroyed compartment to half HP
  - **Rally Crew** — set morale to 70 (no-op if already ≥70)
  - **Recon Drone** — set `RunState.scan_next_enemy = True` (consumed at next combat spawn)
- [x] Add `NON_COMBAT_ACTION` to `Screen` enum
- [x] Render four buttons; on click apply effect and advance to next combat
- [x] Implement `spawn_next_enemy()` helper that resets turn counter and intel state; honors `scan_next_enemy` flag
- [x] Transition: COMBAT_RESULT → NON_COMBAT_ACTION → COMBAT

**Accepts:** after any victory the player chooses one of four actions, then a new enemy appears with the effect applied.

---

## Milestone 4 — Flee Mechanic

**Goal:** let the player exit combat early at a cost.

- [ ] Add "Flee" button to combat UI, active from turn 2 onward
- [ ] On flee: `combat_count++`, `pending_morale_penalty = 15`, transition to COMBAT_RESULT (flee variant — different copy, 0 Score)
- [ ] At next combat start, apply `pending_morale_penalty` to player morale and clear it
- [ ] Flee still routes through the non-combat action screen

**Accepts:** mid-fight flee returns player to result → action → fresh combat with morale −15 carried over.

---

## Milestone 5 — Shop Every 5 Combats

**Goal:** shop appears at combats 5, 10, 15… with fixed inventory and Score deduction.

- [ ] Create `src/shop.py` with `ShopItem` dataclass (`name`, `kind`, `cost`, `max_stacks`, `apply`) and a fixed inventory of 6 items (3 upgrades, 3 consumables — effects stubbed for M6)
- [ ] Add `SHOP` to `Screen` enum
- [ ] After NON_COMBAT_ACTION, if `combat_count % 5 == 0`, route to SHOP before next COMBAT
- [ ] Render 6 items in a grid: name, cost, effect, current stack, Buy button + a "Leave Shop" button (always available)
- [ ] Buy deducts Score; disable button when unaffordable or stack maxed

**Accepts:** after the 5th combat (and every 5 thereafter) the shop opens; Score deducts on buy; leaving advances to next combat.

---

## Milestone 6 — Upgrades and Consumables Effects

**Goal:** wire up shop items so purchases actually change combat.

**Upgrades (permanent, stackable):**

| Name | Cost | Effect | Max Stacks |
|------|------|--------|------------|
| Weapon Calibration | 12 | +5 base_accuracy | 3 |
| Reinforced Hull | 18 | +20 max_hp (and +20 current_hp) | 3 |
| Targeting AI | 25 | +0.08 destroy_chance | 2 |

**Consumables (one-shot):**

| Name | Cost | Effect |
|------|------|--------|
| Emergency Repair Kit | 8 | Restore 25 HP, usable during combat |
| Morale Broadcast | 6 | Set morale to 80, usable during combat |
| Sensor Ping | 5 | Reveal one random hidden enemy compartment |

- [ ] Implement each `apply()` in `src/shop.py`
- [ ] Upgrades modify `Player` stats directly (`base_accuracy`, `max_hp`); destroy-chance modifier threaded through `CombatSystem.fire()`
- [ ] Consumables stored in `RunState.consumables`; add in-combat UI buttons for Repair Kit and Morale Broadcast
- [ ] Sensor Ping usable from shop screen or in combat

**Accepts:** buying Weapon Calibration ×2 measurably raises hit rate; Reinforced Hull bumps the HP bar; consumables fire mid-combat.

---

## Milestone 7 — Enemy Progression

**Goal:** enemies scale by `combat_count`.

- [ ] Create `src/enemies.py` with `EnemyTemplate` dataclass and three templates:
  - T1 Scout (combats 1–4): HP 60, base_accuracy 35, baseline_morale 40, score_reward 12
  - T2 Frigate (combats 5–9): HP 90, base_accuracy 45, baseline_morale 50, score_reward 18
  - T3 Cruiser (combats 10+): HP 130, base_accuracy 55, baseline_morale 60, score_reward 25
- [ ] Implement `spawn_enemy_for_combat(combat_count)` factory; replace inline enemy construction
- [ ] Score reward pulls `tier_base` from template rather than from a hardcoded ladder

**Accepts:** T2 spawns at combat 5 with visibly higher HP/accuracy; T3 at combat 10.

---

## Milestone 8 — Polish & Feedback

**Goal:** make the loop feel finished.

- [ ] `MAIN_MENU` screen with "Start Run" / "Quit"; boot into it instead of straight to combat
- [ ] Victory / Game Over screens show full stats (combat_count, final Score, upgrades owned)
- [ ] Sound effects (optional, low priority)
- [ ] Balance pass: play 3 full runs end-to-end; tune tier rewards, shop prices, or target Score if pacing is off
- [ ] Update [DONE.md](DONE.md) as each milestone lands; clear [WORKBENCH.md](WORKBENCH.md) when M8 ships

**Accepts:** a tester can launch from menu, complete a full win-condition run, and see closing stats.

---

## Out of Scope (deferred)

- Procedural map / node-based progression / sector layouts
- Crew simulation beyond the existing morale value
- Random or rotating shop inventory
- Bosses, elites, multi-stage encounters
- Multiple sectors / acts / difficulty levels beyond T1–T3
- Narrative or branching choices, event cards
- Save / load, run replays, meta-progression between runs
- Complex economy (rarity tiers, item synergies, set bonuses)
- New combat mechanics (shields, energy, multiple weapon types)
