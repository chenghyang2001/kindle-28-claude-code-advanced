# Codebase Concerns

**Analysis Date:** 2026-07-22

## Tech Debt

**No persistence layer:**

- Issue: `tasks` is a plain in-memory `list` created fresh in `main()` on every run (`app.py:67`). All tasks vanish when the CLI exits or crashes.
- Files: `app.py:65-67`
- Impact: Not usable as a real todo tool beyond a single session; any future feature (e.g. `complete_task`) has no durable state to persist status against.
- Fix approach: Introduce a storage boundary (JSON file, SQLite) behind the same `add_task`/`list_tasks`/`delete_task` function signatures so callers are unaffected; load/save at CLI start/stop.

**Tasks identified by name string, not by stable ID:**

- Issue: `add_task`, `delete_task`, and (planned) `complete_task` all operate by matching the raw `name` string in the list. There is no unique identifier per task.
- Files: `app.py:12-53`
- Impact: Duplicate task names are ambiguous — `delete_task` silently removes only the *first* occurrence (explicitly asserted by `test_delete_only_first_occurrence`, `test_app.py:63-66`), which means a caller cannot target "the second 買牛奶". Any future `complete_task(tasks, name)` implementation inherits the same ambiguity and could mark the wrong duplicate as done.
- Fix approach: Move to an indexed/dict-based structure (`{"id": int, "name": str, "done": bool}`) before adding `complete_task`, or explicitly document duplicate-name behavior as accepted product behavior if the GSD `discuss-phase` exercise decides to keep string-based tasks.

**Missing target feature (`complete_task`) — expected gap, not yet a defect:**

- Issue: `GSD-PRACTICE.md` documents `complete_task(name)` as the feature this repo exists to practice adding; it is intentionally absent from `app.py`.
- Files: `app.py` (function absent), `test_app.py` (no `TestCompleteTask` class), `GSD-PRACTICE.md:7,163`
- Impact: None yet — this is the deliberate brownfield starting point for the GSD workflow exercise. Listed here only so it is not mistaken for an overlooked bug during codebase mapping.
- Fix approach: N/A — to be implemented via `/gsd:plan-phase` + `/gsd:execute-phase` per the practice guide.

**Unpinned dependency version:**

- Issue: `requirements.txt` contains a single bare `pytest` with no version pin (`requirements.txt:1`).
- Files: `requirements.txt`
- Impact: Low risk at this scale (single test-only dependency), but a `pip install -r requirements.txt` run months apart could pick up a pytest major version with breaking CLI/API changes, silently changing test collection/output behavior.
- Fix approach: Pin with `pytest==8.4.2` (the version already present in `__pycache__/test_app.cpython-314-pytest-8.4.2.pyc`) or a compatible range like `pytest>=8.4,<9`.

## Known Bugs

**Duplicate task name deletes only the first match (by design, but undocumented in `app.py` docstring):**

- Symptoms: `delete_task(tasks, "任務A")` on `["任務A", "任務A"]` leaves one `"任務A"` behind instead of erroring or requiring disambiguation.
- Files: `app.py:39-53`, asserted in `test_app.py:63-66`
- Trigger: Add the same task name twice, then delete once.
- Workaround: None currently exposed to the CLI user — behavior is invisible unless the user inspects `list` output carefully.

## Security Considerations

**No input length/content limits on task names:**

- Risk: `add_task` only rejects empty/whitespace-only names (`app.py:22-23`); arbitrarily long strings, control characters, or ANSI escape sequences typed via the CLI `add <name>` command are stored and later echoed back via `print()` in `_print_task_list` (`app.py:56-62`).
- Files: `app.py:12-24, 56-62`
- Current mitigation: None.
- Recommendations: Low priority given this is an in-memory single-user local CLI with no network/DB exposure. If persistence or multi-user access is added later, add a max-length check and strip/escape control characters before storing or printing.

**Not applicable / out of scope:**

- No SQL, no external API calls, no secrets, no network I/O exist in this codebase, so SQL injection, credential leakage, and auth concerns from the standard checklist do not apply here.

## Performance Bottlenecks

**Not applicable at current scale:**

- `list_tasks` performs an O(n) full-list copy (`app.py:36`) and `delete_task`/`in` membership checks are O(n) (`app.py:50-52`). For a local single-user CLI with realistically small task counts, this is a non-issue.
- Files: `app.py:27-53`
- Improvement path: Only relevant if the app grows to store thousands of tasks or gains a persistence layer with repeated disk round-trips per operation — not a current concern.

## Fragile Areas

**`main()` CLI dispatch loop has zero test coverage:**

- Files: `app.py:65-113`
- Why fragile: All 12 existing tests in `test_app.py` exercise `add_task`/`list_tasks`/`delete_task` directly as functions; none exercise the `main()` REPL loop itself — command parsing (`raw.split(maxsplit=1)`, `app.py:82`), the `quit`/unknown-command branches, or the `EOFError`/`KeyboardInterrupt` handling (`app.py:73-77`). A future refactor of the dispatch logic (e.g. adding a `complete` command) could break the loop's parsing/branching with no test to catch it.
- Safe modification: Add `complete_task` at the function level first (matching existing test patterns), then wire it into `main()`'s `elif` chain last, manually smoke-testing the interactive loop since it has no automated coverage.
- Test coverage: 0% for `main()`; 100% behavioral coverage (happy path + edge cases) for `add_task`/`list_tasks`/`delete_task`.

**Windows console encoding not declared:**

- Files: `app.py` (no `encoding=` handling), `GSD-PRACTICE.md:24,137` (both invocations explicitly wrap with `PYTHONUTF8=1`)
- Why fragile: The script relies on the caller remembering to set `PYTHONUTF8=1` before running `pytest test_app.py` or `python app.py` on Windows (cp950 default). If run without it, Chinese task names/output (e.g. `買牛奶`, `任務A`) risk `UnicodeEncodeError` or mojibake when printed to a non-UTF-8 console.
- Safe modification: If this app is ever run outside the documented `PYTHONUTF8=1` invocation, add `# -*- coding: utf-8 -*-` is insufficient by itself — would need `sys.stdout.reconfigure(encoding="utf-8")` guarded by `try/except` at the top of `main()`.

## Scaling Limits

**Not applicable:**

- This is a single-process, in-memory, single-user teaching exercise with no server, no concurrent access, and no persistence. There is no meaningful "scaling limit" to document beyond noting the app cannot survive process restart (see Tech Debt: No persistence layer).

## Dependencies at Risk

**None identified:**

- The only dependency is `pytest` (test-only, not shipped with the app itself). No production/runtime third-party packages are used — `app.py` only imports `sys` from the standard library.

## Missing Critical Features

**No `complete_task` implementation:**

- Problem: The core feature this codebase exists to practice adding is not yet present (see Tech Debt section above — this is the intended exercise, not an oversight).
- Blocks: Cannot mark tasks as done; `list_tasks` has no concept of task status to display.

**No `.gitignore`:**

- Problem: The working directory has no `.gitignore` despite containing generated artifacts (`__pycache__/`, `.pytest_cache/`) that show up as untracked files in `git status`.
- Blocks: Risk of accidentally committing bytecode cache (`__pycache__/app.cpython-314.pyc`, `__pycache__/test_app.cpython-314-pytest-8.4.2.pyc`) and pytest cache (`.pytest_cache/`) files into version control on the first commit.

## Test Coverage Gaps

**`main()` CLI loop (see Fragile Areas above):**

- What's not tested: Command parsing, `quit`/unknown-command handling, `EOFError`/`KeyboardInterrupt` graceful exit, and the `add`/`list`/`delete` argument-count guard branches (`app.py:90-91, 103-104`).
- Files: `app.py:65-113`
- Risk: A change to the dispatch loop while adding `complete_task` could silently break `quit` or error-message formatting with no automated test to catch it.
- Priority: Medium — low complexity code, but currently the only untested path in the module.

**No test for `complete_task` (does not exist yet):**

- What's not tested: N/A — function not implemented. Flagged so the GSD practice flow (`/gsd:plan-phase`, `/gsd:execute-phase`) is expected to add both the function and its `TestCompleteTask` class together, following the existing `TestAddTask`/`TestDeleteTask` pattern in `test_app.py`.
- Files: `test_app.py` (class absent)
- Risk: None yet — expected outcome of the exercise per `GSD-PRACTICE.md:148-153` acceptance criteria.
- Priority: High (this is literally the deliverable of the practice exercise).

---

*Concerns audit: 2026-07-22*
