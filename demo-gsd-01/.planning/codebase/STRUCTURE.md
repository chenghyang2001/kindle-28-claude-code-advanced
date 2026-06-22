# Codebase Structure

**Analysis Date:** 2026-06-22

## Directory Layout

```
demo-gsd-01/
├── app.py              # Core business logic + interactive CLI entry point
├── test_app.py         # pytest test suite for all core functions
├── requirements.txt    # Single dependency: pytest
├── GSD-PRACTICE.md     # Practice guide — GSD workflow walkthrough
├── .planning/          # GSD planning artifacts (generated, not hand-edited)
│   └── codebase/       # Codebase map documents (written by /gsd:map-codebase)
├── .pytest_cache/      # pytest internal cache (auto-generated, do not edit)
└── __pycache__/        # Python bytecode cache (auto-generated, do not edit)
```

## Directory Purposes

**Root (`demo-gsd-01/`):**

- Purpose: Contains the entire application — this is a deliberately minimal brownfield project
- Contains: Two source files, one test file, one requirements file, one practice guide
- Key files: `app.py`, `test_app.py`

**`.planning/`:**

- Purpose: GSD workflow artifacts; created and read by `/gsd:map-codebase`, `/gsd:plan-phase`, `/gsd:execute-phase`
- Contains: `codebase/` subdirectory for codebase map documents; future phases will add `PLAN.md` here
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`

**`.planning/codebase/`:**

- Purpose: Codebase map documents consumed by GSD planner and executor agents
- Contains: ARCHITECTURE.md, STRUCTURE.md (and after other map passes: STACK.md, CONVENTIONS.md, etc.)
- Generated: Yes (by `/gsd:map-codebase`)
- Committed: Yes (checked into git so maps persist across sessions)

**`.pytest_cache/`:**

- Purpose: pytest stores test node IDs and run-result cache here
- Generated: Yes (auto-created on first `pytest` run)
- Committed: No (should be in `.gitignore`)

**`__pycache__/`:**

- Purpose: Python bytecode compiled from `app.py` and `test_app.py`
- Generated: Yes (auto-created on first `python` or `pytest` run)
- Committed: No (should be in `.gitignore`)

## Key File Locations

**Entry Points:**

- `app.py:124`: `if __name__ == "__main__": main()` — run with `python app.py`
- `test_app.py:1`: pytest discovery root — run with `pytest test_app.py -v`

**Core Business Logic:**

- `app.py:12–58`: `add_task`, `list_tasks`, `delete_task` — all task operations

**CLI Presentation:**

- `app.py:61–125`: `_print_task_list`, `main` — user-facing I/O

**Tests:**

- `test_app.py:18`: `TestAddTask` — 5 test cases
- `test_app.py:57`: `TestListTasks` — 3 test cases
- `test_app.py:81`: `TestDeleteTask` — 4 test cases

**Dependencies:**

- `requirements.txt`: Only `pytest` declared

**GSD Planning:**

- `.planning/codebase/`: Codebase map documents for GSD agents

## Naming Conventions

**Files:**

- Lowercase with underscores: `app.py`, `test_app.py`
- Test files prefixed with `test_`: `test_app.py` (pytest auto-discovery convention)
- Practice/doc files in SCREAMING-KEBAB: `GSD-PRACTICE.md`

**Directories:**

- GSD artifacts use dotfile prefix: `.planning/`
- Tool caches use dotfile prefix: `.pytest_cache/`
- Python bytecode uses double-underscore: `__pycache__/`

**Functions:**

- Snake_case verbs: `add_task`, `list_tasks`, `delete_task`
- Private helpers prefixed with underscore: `_print_task_list`
- Test methods use descriptive names ending in intent: `test_add_empty_name_raises_value_error`

**Test Classes:**

- PascalCase prefixed with `Test`: `TestAddTask`, `TestListTasks`, `TestDeleteTask`

## Where to Add New Code

**New core function (e.g. `complete_task`):**

- Implementation: `app.py` — add after line 58, before `_print_task_list`
- Follow the same signature pattern: `def complete_task(tasks: list, name: str) -> ...:`
- Tests: `test_app.py` — add a new `TestCompleteTask` class after `TestDeleteTask`

**New CLI command (wiring an existing core function):**

- Location: `app.py:main()` — add a new `elif cmd == "<command>":` branch in the dispatch chain (around line 107–118)
- Print help text: update the `print("指令：...")` line in `main()` to include the new command

**New utility / helper:**

- Shared helpers with no CLI dependency: add to `app.py` with `_` prefix if internal
- If the helper grows large, extract to a new `utils.py` module and import from `app.py`

**New test file:**

- Naming: `test_<module>.py` at project root (pytest discovers `test_*.py` automatically)
- Pattern: mirror the existing class-per-function structure from `test_app.py`

## Special Directories

**`.planning/`:**

- Purpose: GSD workflow artifacts (codebase maps, phase plans)
- Generated: Partially — directory created by GSD commands; documents written by map/plan agents
- Committed: Yes — maps and plans should be committed so they persist between Claude sessions

**`.pytest_cache/`:**

- Purpose: pytest run-result cache; speeds up `--last-failed` reruns
- Generated: Yes
- Committed: No — add to `.gitignore` if not already present

**`__pycache__/`:**

- Purpose: CPython bytecode cache
- Generated: Yes
- Committed: No — add to `.gitignore` if not already present

---

*Structure analysis: 2026-06-22*
