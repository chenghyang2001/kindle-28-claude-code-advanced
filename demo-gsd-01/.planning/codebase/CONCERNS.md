# Codebase Concerns

**Analysis Date:** 2026-06-22

## Tech Debt

**Loose type hints on `tasks` parameter:**

- Issue: All three public functions declare `tasks: list` without element type. Python 3.9+ supports `list[str]` directly; no `List[str]` import needed.
- Files: `app.py` lines 12, 29, 42
- Impact: Static analysis tools (mypy, pyright) cannot catch callers passing wrong element types. Low impact now; becomes a real issue if the data model evolves to `list[dict]` for the planned `complete_task` feature.
- Fix approach: Change signatures to `tasks: list[str]` and add a `-> None` / `-> list[str]` / `-> bool` return type annotation where missing.

**`requirements.txt` has no pinned versions:**

- Issue: `requirements.txt` contains only `pytest` with no version pin.
- Files: `requirements.txt` line 1
- Impact: A future `pip install` in a new environment could pull a breaking major version of pytest (e.g., pytest 10.x). Currently pytest-9.0.2 is installed; no lockfile exists.
- Fix approach: Pin to `pytest>=9.0,<10` or generate a `requirements-lock.txt` / use `pip freeze > requirements.txt` after each known-good install.

**Hardcoded absolute path in practice guide:**

- Issue: `GSD-PRACTICE.md` lines 20–21 contain `cd C:/Users/B00332/workspace/...` — an explicit hardcoded Windows user path, violating the project's no-hardcoded-paths rule.
- Files: `GSD-PRACTICE.md` lines 20–21
- Impact: The guide will silently fail for any user whose username is not `B00332` or who places the repo in a different directory.
- Fix approach: Replace with `cd %USERPROFILE%\workspace\kindle-28-claude-code-advanced\demo-gsd-01` (Batch-style) or instruct the reader to `cd` to their own project root.

## Known Bugs

**`delete_task` silently drops duplicate entries:**

- Symptoms: If `tasks = ["A", "A"]` and `delete_task(tasks, "A")` is called, only the first occurrence is removed. The second remains. The function returns `True`, giving the caller no indication that duplicates existed.
- Files: `app.py` lines 52–58
- Trigger: `add_task` does not prevent duplicate names, so duplicates are reachable in normal use.
- Workaround: Call `delete_task` in a loop until it returns `False`.

**`add_task` allows duplicate task names:**

- Symptoms: Calling `add_task(tasks, "A")` twice results in `["A", "A"]`. There is no deduplication guard.
- Files: `app.py` line 26
- Trigger: Any caller that adds the same name twice.
- Workaround: Caller must check `list_tasks()` before calling `add_task`.

## Security Considerations

**No input sanitisation beyond whitespace strip:**

- Risk: `add_task` trims whitespace but performs no length cap or character validation on `name`. A caller could store an arbitrarily long string, exhausting memory in a long-running process.
- Files: `app.py` lines 23–26
- Current mitigation: This is a CLI demo with in-memory state; no network exposure.
- Recommendations: Add a maximum name length check (e.g., 256 chars) in `add_task` if the function is ever reused in a web or persistent context.

## Performance Bottlenecks

**`delete_task` uses linear scan (`list.remove`):**

- Problem: `list.remove` scans the list from the front; O(n) per call.
- Files: `app.py` line 54
- Cause: Standard Python `list` has no O(1) removal by value.
- Improvement path: For the current CLI demo scale (< 100 items), this is irrelevant. If the task store ever grows large, replacing `list` with a `dict` keyed on task name would give O(1) lookup and removal and simultaneously solve the duplicate-name problem.

## Fragile Areas

**`main()` CLI loop is entirely untested:**

- Files: `app.py` lines 71–125
- Why fragile: The interactive loop handles `EOFError`, `KeyboardInterrupt`, command parsing, and all user-facing formatting. None of this is covered by `test_app.py`. Any refactor of `main()` could silently break CLI behaviour.
- Safe modification: Extract command dispatch into a separate `handle_command(tasks, raw)` function that accepts a string and returns a string; this makes it testable without mocking `input()`.
- Test coverage: 0% for `main()` and `_print_task_list()`.

**`_print_task_list` is untested:**

- Files: `app.py` lines 61–68
- Why fragile: Output formatting (numbering, empty-list message) can silently regress.
- Safe modification: Refactor to return a formatted string rather than printing directly; test via assertion on the return value.

## Scaling Limits

**In-memory task store with no persistence:**

- Current capacity: Unlimited (RAM-bound), but all data is lost when the process exits.
- Limit: No persistence layer exists; `tasks` is a plain `list` local to `main()`.
- Scaling path: Replace `tasks: list` with a JSON file backend or SQLite to survive process restarts.

## Missing Critical Features

**`complete_task` not yet implemented:**

- Problem: `GSD-PRACTICE.md` identifies `complete_task(tasks, name)` as the intended new feature (Phase 4 of GSD practice). The function does not exist in `app.py`.
- Blocks: The GSD practice exercise cannot be completed; the verify-phase acceptance criteria (all tests green including `complete_task` tests) cannot be met.

**No `.gitignore`:**

- Problem: The project root has no `.gitignore`. `__pycache__/`, `.pytest_cache/`, and `.planning/` directories are untracked and will be committed in full if `git add` is run.
- Files: Project root (missing file)
- Risk: Compiled `.pyc` bytecode and pytest cache will pollute the repository history.

**No pytest configuration (`pytest.ini` / `pyproject.toml` / `setup.cfg`):**

- Problem: Running `pytest` without configuration relies on pytest's default test discovery. There is no explicit `testpaths` declaration, so pytest will search the entire directory tree.
- Files: Project root (missing configuration)
- Risk: If the repo is extended with subdirectories containing non-test Python files named `test_*.py`, they will be accidentally collected.

## Test Coverage Gaps

**`main()` function:**

- What's not tested: Interactive input loop, command dispatch (`add`/`list`/`delete`/`quit`/unknown), error output to stderr, `EOFError`/`KeyboardInterrupt` handling.
- Files: `app.py` lines 71–125
- Risk: Any change to CLI behaviour goes undetected.
- Priority: Medium (demo project, but the pattern matters for future brownfield work).

**`_print_task_list()` helper:**

- What's not tested: Numbered formatting, empty-list message, order correctness.
- Files: `app.py` lines 61–68
- Risk: Output formatting regressions.
- Priority: Low.

---

*Concerns audit: 2026-06-22*
