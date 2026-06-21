# Done

Completed tasks. Archived for reference only; consult when prior work is specifically relevant to your current task.

## Post-Combat Actions

- [x] The action screen shows current hull, morale, and destroyed compartments
- [x] `Field Repair` and `Rally Crew` are disabled when they cannot change ship state
- [x] `Field Repair` opens a dedicated selection screen for destroyed compartments
- [x] The selected compartment is validated and restored to half HP
- [x] The repair selection can be cancelled without consuming the post-combat action

## Combat completion animation

- [x] Combat remains visible for a timed 1.2-second resolution phase after either ship is destroyed
- [x] Combat input and enemy turns are frozen while the resolution is active
- [x] A temporary pulsing victory or defeat overlay appears before the final result screen
- [x] The pending destination is stored in `GameState`, preventing repeated score awards

## Target Selection Visibility

- [x] Hidden enemy compartments now use `Targeting: Unknown compartment`
- [x] Target names are derived from the same effective visibility rule used to render compartments
- [x] Revealed compartments and global reveal effects show the real name immediately
- [x] Disabling a temporary global reveal hides names again unless the compartment was permanently revealed

## Title Screen and Run Reset

- [x] The game now opens on a title screen instead of starting combat immediately
- [x] The title screen provides `Start Game`, `Options`, and `Quit` actions
- [x] `Options` reports that configuration is not available yet
- [x] `Start Game` creates a clean player, enemy, run state, and combat state
- [x] `GAME_OVER` and `VICTORY` now return to the title screen
- [x] Added title-screen state coverage; suite now at 118 passing tests

## Milestone 7 — Enemy Progression

- [x] `src/enemies.py` added `EnemyTemplate` plus Scout, Frigate, and Cruiser tier definitions
- [x] `spawn_enemy_for_combat(combat_count)` now picks the next encounter's enemy tier from completed combats
- [x] `main.py` now spawns enemies through the factory instead of constructing a flat default enemy each time
- [x] Score rewards now come from `enemy.score_reward` instead of a hardcoded tier ladder in `RunState`
- [x] Added factory boundary coverage for combat 1, 5, and 10 tier transitions
- [x] Test suite now at 117 passing tests

## Milestone 6 — Upgrades and Consumables Effects

- [x] `Ship` / `Player` gained a persistent `destroy_chance_bonus` stat for upgrade-driven combat effects
- [x] `CombatSystem.fire()` now respects attacker destroy-chance bonuses while keeping the baseline chance for attackers without upgrades
- [x] `src/shop.py` applies real upgrade effects for Weapon Calibration, Reinforced Hull, and Targeting AI
- [x] Consumables are tracked in `RunState.consumables` and can be used during combat as free actions
- [x] `main.py` renders a compact combat consumables strip for owned Repair Kit, Morale Broadcast, and Sensor Ping
- [x] Sensor Ping reveals one hidden enemy compartment and safely no-ops when nothing remains hidden
- [x] 13 new tests landed across combat, health, and shop coverage; suite now at 115 passing tests

## Milestone 5 — Shop Every 5 Combats

- [x] `src/shop.py`: `ShopItem` dataclass plus fixed inventory of 6 items (3 upgrades, 3 consumables) with stubbed `apply()` hooks for M6
- [x] `Screen.SHOP` added to `src/game_state.py`
- [x] Shop routing added after NON_COMBAT_ACTION whenever `combat_count % 5 == 0`
- [x] `render_shop()` added in `main.py` with item cards, cost buttons, owned stack display, and "Leave Shop"
- [x] `buy_item()` deducts Score, enforces affordability and stack caps, and records owned upgrades / consumables in `RunState`
- [x] 7 unit tests in `tests/test_shop.py`; suite now at 102 passing tests

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

## Combat polish

- [x] Debug mode (F1) reveals precise HP, morale, accuracy modifiers, and all enemy compartments
- [x] Fire button also responds to mouse click (Space still works)
- [x] Per-ship base accuracy: Player 70, Enemy 40 (was shared 70)
- [x] Fire button moved to bottom-center (y = WINDOW_HEIGHT - 70)

## Milestone 4 — Flee Mechanic

- [x] Flee button to the left of Fire button, active from turn 2 (warm orange), dimmed before
- [x] `perform_flee()`: calls `run_state.register_flee()`, sets `last_combat_result = "flee"`, transitions to COMBAT_RESULT
- [x] `RunState.register_flee()`: combat_count++, pending_morale_penalty = 15, last_score_delta = 0
- [x] `RunState.consume_pending_morale_penalty()`: returns and clears the penalty
- [x] `start_next_combat()` applies pending morale penalty to player and resets `last_combat_result = "win"`
- [x] COMBAT_RESULT flee variant: "Combat N Abandoned / Fled — +0 Score / Morale −15 applied at next combat"
- [x] 5 new unit tests; 94 total passing

## Milestone 3 — Non-Combat Action Screen

- [x] `src/non_combat.py`: `NonCombatAction` dataclass with 4 instances — Patch Hull, Field Repair, Rally Crew, Recon Drone
- [x] `Screen.NON_COMBAT_ACTION` added to the enum in `src/game_state.py`
- [x] `action_button_rects()` helper and `render_non_combat_action()` screen in `main.py`
- [x] COMBAT_RESULT Continue button now routes to NON_COMBAT_ACTION instead of spawning directly
- [x] Action click applies effect then calls `start_next_combat()`
- [x] `start_next_combat()` honors `RunState.scan_next_enemy` (clears flag after use)
- [x] 7 unit tests in `tests/test_non_combat.py`; 89 total passing
- [x] MVP loop closed: combat → result → action → new enemy → repeat

## Milestone 2 — Screen State Machine & Combat Result Screen

- [x] `Screen` enum added to `src/game_state.py`: `COMBAT`, `COMBAT_RESULT`, `GAME_OVER`, `VICTORY`
- [x] `GameState` gains `screen`, `last_combat_result` fields and `reset_for_combat()` method
- [x] `RunState` gains `last_score_delta` field; `award_combat_score()` stores it for display
- [x] `main.py` main loop refactored to dispatch render/input by `game_state.screen`
- [x] `COMBAT_RESULT` screen: shows combat number, score delta (+N), running total, Continue button
- [x] `GAME_OVER` screen: final score, combats survived, Quit button
- [x] `VICTORY` screen: same layout in green, Quit button
- [x] `start_next_combat()`: swaps enemy sprite, calls `reset_for_combat()`, respects debug reveal
- [x] 6 new unit tests (4 GameState, 2 RunState); 81 total passing

## Debug Mode Accelerators

- [x] Instant enemy turn: in debug mode (F1) enemy fires on the next frame, no 2-second wait
- [x] Auto-Kill toggle (D key or button to the right of Fire): when ON, the normal Fire action always hits and always destroys the selected compartment; player still selects target and fires manually
- [x] Toggle renders gold ("Auto-Kill: ON") when active; resets to OFF when F1 exits debug mode

## Milestone 1 — Run State & Score Tracking

- [x] `src/run_state.py`: `RunState` dataclass with `combat_count`, `score`, `target_score=120`, `owned_upgrades`, `consumables`, `pending_morale_penalty`, `scan_next_enemy`
- [x] `RunState` instantiated in `main.py` startup alongside `GameState`
- [x] On enemy HP ≤ 0: `combat_count++`, award Score = `tier_base + floor(hp% × 10)` (T1: 12, T2: 18, T3: 25)
- [x] On player HP ≤ 0: game freezes with "GAME OVER" overlay
- [x] On Score ≥ 120: game freezes with "VICTORY!" overlay
- [x] "Combat N Complete" overlay shown when enemy dies but score < 120
- [x] All overlays freeze combat inputs; ESC exits
- [x] Debug HUD (F1) extended with Score and Combats counters
- [x] 15 unit tests in `tests/test_run_state.py` covering tier boundaries, score accumulation, and win condition
