# Codebase Structure

**Analysis Date:** 2026-07-22

## Directory Layout

```
demo-gsd-01-20260723/
├── app.py                 # Entire application: core functions + CLI loop + entry point
├── test_app.py             # Full pytest suite for app.py (12 tests)
├── requirements.txt         # Single dependency: pytest
├── GSD-PRACTICE.md          # Exercise instructions for the GSD workflow practice run
├── .planning/                # GSD workflow artifacts (codebase maps, plans, phase state)
│   └── codebase/              # Generated codebase analysis docs (this file lives here)
├── .pytest_cache/            # pytest's own cache (generated, not committed logic)
└── __pycache__/              # Python bytecode cache (generated)
```

This is a deliberately minimal, single-file "brownfield" teaching codebase — there is no `src/`, no package structure, and no subdirectories for logic. Everything application-related lives in `app.py` at the project root.

## Directory Purposes

**Project root (`.`):**

- Purpose: Holds the entire application — one script, one test file, one dependency manifest
- Contains: `app.py`, `test_app.py`, `requirements.txt`, `GSD-PRACTICE.md`
- Key files: `app.py` (all logic), `test_app.py` (all tests)

**`.planning/`:**

- Purpose: GSD (Get Shit Done) workflow state — codebase maps, phase plans, discussion notes produced by `/gsd:*` slash commands
- Contains: `codebase/` subfolder with generated Markdown analysis docs (STACK.md, ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md, INTEGRATIONS.md — populated incrementally as `/gsd:map-codebase` is run per focus area)
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md` (this document)

**`.pytest_cache/` and `__pycache__/`:**

- Purpose: Auto-generated caches from running pytest and importing `app.py`
- Generated: Yes — safe to delete, will be recreated on next test run
- Committed: Should not be committed (pytest_cache ships its own `.gitignore`)

## Key File Locations

**Entry Points:**

- `app.py:116-117`: `if __name__ == "__main__": main()` — run with `python app.py`

**Configuration:**

- `requirements.txt`: Declares `pytest` as the only dependency (no version pin)
- No `.env`, no config files, no CLI framework config — the app takes no command-line arguments and reads no environment variables

**Core Logic:**

- `app.py:12-24`: `add_task(tasks, name)`
- `app.py:27-36`: `list_tasks(tasks)`
- `app.py:39-53`: `delete_task(tasks, name)`
- `app.py:56-62`: `_print_task_list(tasks)` (private CLI-output helper)
- `app.py:65-113`: `main()` (CLI command dispatch loop)

**Testing:**

- `test_app.py`: All tests, organized into three `Test*` classes (`TestAddTask`, `TestListTasks`, `TestDeleteTask`) mirroring the three core functions in `app.py`
- Run via: `PYTHONUTF8=1 pytest test_app.py -v` (per `GSD-PRACTICE.md`, Windows environment requires `PYTHONUTF8=1` for correct CJK/emoji output)

**Documentation:**

- `GSD-PRACTICE.md`: Step-by-step guide for practicing the GSD workflow (`map-codebase` → `discuss-phase` → `plan-phase` → `execute-phase` → `verify-phase`) against this codebase, culminating in adding a `complete_task(name)` function

## Naming Conventions

**Files:**

- Application code: `app.py` (singular, lowercase, no package prefix)
- Test files: `test_<module>.py` (pytest auto-discovery convention — `test_app.py` mirrors `app.py`)
- Documentation: `UPPERCASE.md` for top-level guides (`GSD-PRACTICE.md`)

**Directories:**

- Hidden/tooling directories use a leading dot (`.planning/`, `.pytest_cache/`) to separate workflow/tooling artifacts from application code
- No naming convention needed for application-level subdirectories since none exist — the app is single-file by design

**In-code naming (observed in `app.py` / `test_app.py`):**

- Functions: `snake_case` (`add_task`, `list_tasks`, `delete_task`, `_print_task_list`) — leading underscore marks the function as a private/internal helper not meant to be imported by tests or other callers
- Test classes: `PascalCase` prefixed with `Test` (`TestAddTask`, `TestListTasks`, `TestDeleteTask`), grouping tests by the function under test
- Test methods: `test_<scenario>_<expected_outcome>` (e.g., `test_add_empty_name_raises_value_error`, `test_delete_only_first_occurrence`) — descriptive, states both the input scenario and the expected result

## Where to Add New Code

**New Feature (e.g., the `complete_task` function from `GSD-PRACTICE.md`):**

- Primary code: Add as a new top-level function in `app.py`, following the existing signature pattern `function_name(tasks: list, name: str) -> <return type>` — place it after `delete_task` (`app.py:53`) and before `_print_task_list` (`app.py:56`) to keep public core functions grouped together
- CLI wiring: Add a new `elif cmd == "complete":` branch in `main()`'s command dispatch (`app.py:85-113`), following the same pattern as the `delete` branch (parse args, call core function, print success/failure)
- Tests: Add a new `TestCompleteTask` class in `test_app.py`, following the existing class structure (happy path, edge case, error/no-op case) — see `TestDeleteTask` (`test_app.py:49-66`) as the closest template since `complete_task` will likely also return a boolean or be a no-op

**New Data Structure Decision (open per `GSD-PRACTICE.md`):**

- If task representation changes from `str` to `dict` (e.g., `{"name": ..., "done": False}`) to support "done" state, this change touches all three existing functions (`add_task`, `list_tasks`, `delete_task`) plus all their tests — this is the central design decision to resolve during the GSD `discuss-phase`/`plan-phase` steps, not something to decide ad hoc

**Utilities:**

- No shared utility module exists yet. If cross-cutting helpers are needed beyond `_print_task_list`, keep them as private (`_`-prefixed) functions in `app.py` rather than creating a new module, to preserve the single-file design intent of this teaching sample — unless a GSD phase explicitly decides to introduce module structure

## Special Directories

**`.planning/`:**

- Purpose: GSD workflow state (codebase maps, plans, verification notes) — not application runtime state
- Generated: Yes, by `/gsd:*` slash commands
- Committed: Typically yes for GSD practice repos (tracks the learning workflow), but confirm against project `.gitignore` before assuming

**`.pytest_cache/`:**

- Purpose: pytest's internal cache (last failed tests, etc.)
- Generated: Yes, automatically on every `pytest` run
- Committed: No — contains its own `.gitignore` (`.pytest_cache/.gitignore`) excluding itself

**`__pycache__/`:**

- Purpose: Compiled Python bytecode (`.pyc`) for `app.py` and `test_app.py`
- Generated: Yes, automatically on import/execution
- Committed: No — should be excluded via `.gitignore` (standard Python practice; verify a top-level `.gitignore` exists and includes `__pycache__/`)

---

*Structure analysis: 2026-07-22*
