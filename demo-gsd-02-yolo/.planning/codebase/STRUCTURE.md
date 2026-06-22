# Codebase Structure

**Analysis Date:** 2026-06-22

## Directory Layout

```
demo-gsd-02-yolo/           # Project root
├── app.py                  # All production code (3 functions + main REPL)
├── test_app.py             # pytest test suite
├── requirements.txt        # Runtime/dev dependencies (pytest only)
├── YOLO-PRACTICE.md        # GSD practice notes
├── .planning/
│   └── codebase/           # GSD codebase map documents (this file)
├── .pytest_cache/          # pytest cache (generated, not committed)
├── .ruff_cache/            # ruff linter cache (generated, not committed)
└── __pycache__/            # Python bytecode cache (generated, not committed)
```

## Directory Purposes

**Project root:**

- Purpose: Flat layout — all source and test files live directly here; no sub-packages
- Key files: `app.py`, `test_app.py`, `requirements.txt`

**`.planning/codebase/`:**

- Purpose: GSD codebase map documents written by `/gsd:map-codebase`
- Generated: Yes (by GSD tooling)
- Committed: Yes

**`.pytest_cache/`:**

- Purpose: pytest run cache and node IDs
- Generated: Yes
- Committed: No (`.gitignore` present inside)

**`.ruff_cache/`:**

- Purpose: ruff linter cache
- Generated: Yes
- Committed: No (`.gitignore` present inside)

**`__pycache__/`:**

- Purpose: Python compiled bytecode for `app.py` and `test_app.py`
- Generated: Yes
- Committed: No

## Key File Locations

**Entry Points:**

- `app.py:99`: `if __name__ == "__main__": main()` — CLI entry point

**Core Logic:**

- `app.py:12`: `add_task(tasks, name)` — append with validation
- `app.py:29`: `list_tasks(tasks)` — returns shallow copy
- `app.py:43`: `delete_task(tasks, name)` — remove with bool result
- `app.py:61`: `main()` — REPL loop

**Testing:**

- `test_app.py` — all tests; three `class Test*` groups, one per function

**Configuration:**

- `requirements.txt` — single dependency: `pytest`

## Naming Conventions

**Files:**

- Production module: `app.py` (flat noun, no prefix)
- Test file: `test_app.py` (mirrors the module it tests with `test_` prefix — pytest discovery convention)

**Functions:**

- `snake_case` verb phrases: `add_task`, `list_tasks`, `delete_task`, `main`

**Test classes:**

- `PascalCase` with `Test` prefix: `TestAddTask`, `TestListTasks`, `TestDeleteTask`

**Test methods:**

- `snake_case` with `test_` prefix: `test_add_happy_path`, `test_delete_non_existent_returns_false`

**Variables:**

- Descriptive `snake_case`: `tasks`, `name`, `cleaned`, `current`, `command`

## Where to Add New Code

**New task operation (e.g., `complete_task`, `edit_task`):**

- Implementation: add a new `def <verb>_task(tasks, ...)` function in `app.py` before `main()`
- Wire it up: add an `elif command == "<verb>"` branch inside `main()` (`app.py:73–96`)
- Tests: add a new `class Test<VerbTask>:` block in `test_app.py`

**New CLI command that is not a task operation:**

- Same pattern — function in `app.py`, `elif` branch in `main()`, test class in `test_app.py`

**New dependency:**

- Add to `requirements.txt` (one package per line)

**Persistence layer (future):**

- If adding file or DB storage, create a new module (e.g., `storage.py`) at the project root
- `app.py` functions should remain pure (accept/return the list); call storage in `main()` around the REPL

## Special Directories

**`.planning/`:**

- Purpose: GSD planning artifacts (codebase maps, phase plans)
- Generated: Partially (map documents are generated; phase docs may be hand-edited)
- Committed: Yes

---

*Structure analysis: 2026-06-22*
