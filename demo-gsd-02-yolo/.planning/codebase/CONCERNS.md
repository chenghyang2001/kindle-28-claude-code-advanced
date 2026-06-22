# Codebase Concerns

**Analysis Date:** 2026-06-22

> Context: This is an intentionally minimal brownfield learning demo, not a production system.
> Concerns are framed honestly — "by design" items are still listed because YOLO mode may add on top of them.

---

## Tech Debt

**Bare `list` type hint instead of `list[str]`:**

- Issue: All three core functions declare `tasks: list` without the element type.
- Files: `app.py:12`, `app.py:29`, `app.py:43`
- Impact: Mypy / Pyright cannot catch accidental insertion of non-string values. Low risk while the app is tiny; becomes a real gap once YOLO adds `complete_task` which needs richer task objects.
- Fix approach: Change signature to `tasks: list[str]` (or define a `Task` dataclass if the data model is extended).

**Duplicate task names allowed silently:**

- Issue: `add_task` does not check for duplicates. Adding `"買牛奶"` twice produces two entries; `delete_task` removes only the first silently.
- Files: `app.py:22–26`, `app.py:43–58`
- Impact: Confusing UX; if `complete_task` is added later without dedup logic, marking "done" will be ambiguous.
- Fix approach: Either reject duplicates in `add_task` with a `ValueError`, or switch tasks from `list[str]` to a dict/dataclass keyed by unique ID.

**`requirements.txt` has no version pin:**

- Issue: `requirements.txt` contains only `pytest` with no version constraint (`==`, `>=`).
- Files: `requirements.txt:1`
- Impact: `pip install pytest` silently upgrades to the latest major, which could break test discovery in a CI environment that caches dependencies.
- Fix approach: Pin to a minimum version, e.g., `pytest>=8.0`.

---

## Known Bugs

**Secondary `input()` calls unprotected against EOF / Ctrl+C:**

- Symptoms: If the user presses Ctrl+C or Ctrl+D at the "任務名稱：" or "要刪除的任務名稱：" prompt, Python raises `KeyboardInterrupt` / `EOFError` and prints a raw traceback instead of exiting gracefully.
- Files: `app.py:76` (`input("任務名稱：")`), `app.py:90` (`input("要刪除的任務名稱：").strip()`)
- Trigger: Press Ctrl+C *after* typing `add` or `delete` and being prompted for a name.
- Workaround: The outer loop at `app.py:68` catches these exceptions, but it only wraps the *first* `input()` (the command prompt), not the nested sub-prompts.

---

## Security Considerations

Not applicable at the scope of this demo (no network, no auth, no persistent storage, no external dependencies beyond pytest).

---

## Performance Bottlenecks

**Linear scan on every `delete_task` and (future) `complete_task`:**

- Problem: `list.remove()` does O(n) scan. Acceptable for a demo with tens of tasks.
- Files: `app.py:54`
- Cause: Plain `list[str]` has no index by name.
- Improvement path: Switch to `dict[str, Task]` or add a name-to-index map if the list grows large. Not needed until YOLO adds `complete_task` that also needs to look up tasks.

---

## Fragile Areas

**`main()` is entirely untested:**

- Files: `app.py:61–100`
- Why fragile: The REPL loop logic (command dispatch, stdout formatting, error routing to stderr, EOF handling) has zero test coverage. Any YOLO-generated change to `main()` cannot be verified automatically.
- Safe modification: Keep business logic in the three core functions and keep `main()` as a thin dispatcher. New features should live in new functions, not inline in `main()`.
- Test coverage: 0% — only `add_task`, `list_tasks`, `delete_task` are exercised by `test_app.py`.

**`delete_task` requires exact case-sensitive name match:**

- Files: `app.py:54`
- Why fragile: A user who typed `"買牛奶"` and tries to delete `"買牛奶 "` (trailing space) will get `False`. The add path strips whitespace, but the delete path does not.
- Safe modification: Strip `name` before calling `delete_task`, or strip inside `delete_task` itself (note: `app.py:90` does strip the delete prompt input, so this is only a risk for callers that skip the strip).

---

## Scaling Limits

**In-memory state lost on every exit (by design):**

- Current capacity: Unlimited tasks per session (Python list).
- Limit: All data disappears when the process exits.
- Scaling path: This is the intentional starting point for the YOLO exercise. Adding a JSON flat-file or SQLite store would be the natural next step after `complete_task` / `list_pending` are added.

---

## Dependencies at Risk

No third-party runtime dependencies. `pytest` is a dev/test dependency only.

---

## Missing Critical Features

**`complete_task(tasks, name)` and `list_pending(tasks)` not implemented:**

- Problem: These are the two functions that the YOLO exercise is designed to add. Their absence is intentional but represents the single largest functional gap.
- Files: `app.py` (not yet present)
- Blocks: The full YOLO practice workflow (`YOLO-PRACTICE.md:163–164`) cannot be verified until both functions exist with passing tests.

---

## Test Coverage Gaps

**`main()` REPL loop — untested:**

- What's not tested: Command dispatch (`add` / `list` / `delete` / `quit` / unknown), stdout/stderr output formatting, graceful EOF / Ctrl+C exit, the unprotected secondary `input()` calls.
- Files: `app.py:61–100`
- Risk: A refactor of `main()` by YOLO could silently break the CLI UX without any test failure.
- Priority: Low for the demo; Medium if this becomes a teaching example for CLI testing patterns.

**No test for duplicate add followed by delete:**

- What's not tested: Adding the same task name twice and deleting once — verifying only the first occurrence is removed and the second remains.
- Files: `test_app.py` (missing test case)
- Risk: If `complete_task` is implemented and marks by name match, the first-occurrence-only behavior could produce surprising results.
- Priority: Low.

**No test for `main()` EOF / Ctrl+C on nested prompts:**

- What's not tested: The unprotected `input("任務名稱：")` at `app.py:76` raising `KeyboardInterrupt`.
- Files: `test_app.py` (missing integration test)
- Risk: Regression if YOLO refactors the REPL without adding exception guards.
- Priority: Low.

---

## Other Concerns

**Hardcoded absolute path in `YOLO-PRACTICE.md`:**

- Issue: `YOLO-PRACTICE.md:42–43` contains `C:/Users/B00332/workspace/...`, violating the project-wide no-hardcoded-paths rule.
- Files: `YOLO-PRACTICE.md:42`, `YOLO-PRACTICE.md:48`, `YOLO-PRACTICE.md:63`, `YOLO-PRACTICE.md:115`
- Impact: The guide fails on any machine with a different username or drive. This is a documentation file, so runtime impact is zero; the risk is misleading copy-paste instructions.
- Fix approach: Replace with `cd <project-root>` or a relative path instruction.

**No `.gitignore`:**

- Issue: There is no `.gitignore` in this directory. The `__pycache__/`, `.pytest_cache/`, and `.ruff_cache/` directories are present and would be committed unintentionally.
- Files: Project root (missing `.gitignore`)
- Impact: Pollutes git history with generated cache files; differs across Python versions.
- Fix approach: Add a `.gitignore` with at minimum `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `*.pyc`.

---

*Concerns audit: 2026-06-22*
