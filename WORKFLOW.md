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

**Manual:** Run `python main.py` and test the feature in the game window. Check the golden path and edge cases.

**Automated tests:** Not yet in place. When they exist, run `pytest` or the project's test runner before committing.

---

## Shipping

- **Commit only when the feature works.** Don't commit half-finished code.
- **No force-push to `main`.** Rebase locally before pushing if needed, but never `--force` to the shared branch.
- **Review before merge:** If applicable, have another pair of eyes check the changes before merging to `main`.

---

## Git status check

Before shipping, verify:

```bash
git status          # Should be clean or show only expected changes
git log -3          # Last 3 commits should follow the [ADD]/[FIX]/[DEL] format
```
