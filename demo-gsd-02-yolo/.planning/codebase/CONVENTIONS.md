# Coding Conventions

**Analysis Date:** 2026-06-22

## Naming Patterns

**Files:**

- `snake_case.py` — e.g., `app.py`, `test_app.py`
- Test files prefixed with `test_` to match pytest discovery rules

**Functions:**

- `snake_case` verb-noun pattern: `add_task`, `list_tasks`, `delete_task`, `main`

**Variables:**

- `snake_case` with descriptive names: `cleaned`, `current`, `command`
- Local loop variables: `index`, `task`
- Type-annotated where meaningful: `tasks: list = []`

**Types:**

- Built-in type annotations used directly: `list`, `str`, `bool`, `None`
- No custom type aliases or dataclasses — tasks are plain `str` in a `list`

## Code Style

**Formatting:**

- 4-space indentation throughout
- Ruff is present (`.ruff_cache/0.15.16/`) — no `pyproject.toml` or `ruff.toml` config file committed, so default Ruff rules apply
- No trailing whitespace observed

**Linting:**

- Ruff (version 0.15.16 cache present) — enforced during development, no config file in repo
- No `.flake8`, `.pylintrc`, or `setup.cfg` present

## Import Organization

**Order:**

1. Standard library (`sys`)
2. Third-party (`pytest` — test file only)
3. Local (`from app import add_task, delete_task, list_tasks`)

**Path Aliases:**

- None — flat single-module structure, direct imports

## Error Handling

**Patterns:**

- Functions raise typed exceptions (`ValueError`) for invalid input; callers catch and convert to user-visible messages
- `list.remove` `ValueError` is caught internally in `delete_task` and converted to a `bool` return value — no exception leaks to caller
- `main()` catches `EOFError` and `KeyboardInterrupt` from `input()` for graceful CLI exit
- Error messages printed to `sys.stderr` via `print(..., file=sys.stderr)`

**Anti-pattern to avoid:**

- Do not use bare `except:` — all caught exceptions are named specifically

## Logging

**Framework:** None — `print()` to stdout/stderr only

**Patterns:**

- Normal output → `print(...)` to stdout
- Error/warning output → `print(..., file=sys.stderr)`
- No `logging` module used (appropriate for a CLI demo of this scale)

## Comments

**When to Comment:**

- Comments explain *why*, not *what*: e.g., `# 先 strip 再判斷，避免「   」這類純空白被當成有效任務` (explains intent behind strip-before-check)
- Exception-handling branches include a one-line rationale comment: `# list.remove 找不到元素會拋 ValueError，這裡轉成 False 回報`
- `main()` catch block comment explains user-experience intent

**Docstrings:**

- Module-level docstring: present in both `app.py` and `test_app.py`
- Function-level Google-style docstrings: all public functions have `Args:` / `Returns:` / `Raises:` sections
- Language: Traditional Chinese (繁體中文) for all docstrings and inline comments
- Test class docstrings: one-line Chinese description of what is under test

## Function Design

**Size:** All functions are under 20 lines; `main()` is ~35 lines including blank lines

**Parameters:** Each function takes the shared `tasks` list as first argument (in-memory state passed explicitly — no global state)

**Return Values:**

- Mutating functions return `None` (`add_task`)
- Read-only functions return a new copy (`list_tasks`)
- Boolean success/failure pattern for destructive operations (`delete_task` returns `bool`)

## Module Design

**Exports:** No `__all__` defined; three public functions (`add_task`, `list_tasks`, `delete_task`) and `main()` are importable directly

**Barrel Files:** Not applicable — single-module project

**Entry Point:** `if __name__ == "__main__": main()` guard at bottom of `app.py`

---

*Convention analysis: 2026-06-22*
