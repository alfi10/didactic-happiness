# Workflow

Process and shipping rules for this project.

---

## Branching

- Branch from `main`
- Use prefixes: `feat/`, `fix/`, `refactor/` — e.g. `feat/player-movement`
- Delete branch after merge

---

## Commits

**Prefix:** Choose one: `[ADD]`, `[FIX]`, or `[DEL]`

- `[ADD]` — new feature or file
- `[FIX]` — bug fix or correction
- `[DEL]` — removal (code, file, or feature)

**Message format:**

```
[ADD] Brief one-line summary

Optional: one additional sentence for context.
```

- Summary line (after prefix) should be concise and clear
- Keep the total message to **no more than 2 sentences** (summary + optional context line)
- No multi-paragraph explanations

**Example:**

```
[ADD] Player movement with arrow keys.

Movement is smooth with 5px per frame and stays within screen bounds.
```

---

## Testing

### Automated tests (pytest)

Run the full test suite before committing:

```bash
uv run pytest
```

**Test location:** `tests/` directory at repo root. One test file per source module: `test_combat.py` ↔ `src/combat.py`, etc.

**What to test:**
- **Pure logic modules** (combat, game_state, compartments): full coverage — these are easy to test and the highest-value safety net
- **Pygame-heavy code** (rendering, mouse handling in main.py): skip — manual verification is more practical

**Conventions:**
- Test files named `test_*.py`, functions named `test_*`
- Use `monkeypatch` to control randomness (e.g. `monkeypatch.setattr(random, "randint", lambda a, b: 0)`)
- One assertion per test when possible; descriptive function names over docstrings

**When to add tests:**
- Every new pure-logic function/class in `src/` gets at least one test
- Bug fixes: add a regression test that fails on the broken code before fixing

### Manual testing

Always also run `uv run main.py` and verify the feature behaves correctly in the game window. Automated tests cover logic; manual tests cover feel.

---

## Shipping

- **Commit only when the feature works.** Don't commit half-finished code.
- **No force-push to `main`.** Rebase locally before pushing if needed, but never `--force` to the shared branch.
- **Review before merge:** If applicable, have another pair of eyes check the changes before merging to `main`.

---

## Git status check

Before shipping, verify:

```bash
uv run pytest       # All tests pass
git status          # Should be clean or show only expected changes
git log -3          # Last 3 commits should follow the [ADD]/[FIX]/[DEL] format
```
