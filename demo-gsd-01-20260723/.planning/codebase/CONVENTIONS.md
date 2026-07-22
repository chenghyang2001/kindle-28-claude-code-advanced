# Coding Conventions

**Analysis Date:** 2026-07-22

## Naming Patterns

**Files:**

- Single-word, lowercase module names: `app.py` (implementation), `test_app.py` (tests — `test_` prefix + module name, flat layout, not nested in a `tests/` directory).

**Functions:**

- `snake_case` for all functions: `add_task`, `list_tasks`, `delete_task`, `main` (`app.py:12,27,39,65`).
- Private/internal helper functions prefixed with a single leading underscore: `_print_task_list` (`app.py:56`). Use this prefix for any new helper not part of the public module API.
- Function names are verbs describing the action performed on `tasks`: `add_task`, `delete_task`, `list_tasks`. A new `complete_task(tasks, name)` function should follow the same `<verb>_task(tasks, name)` signature shape.

**Variables:**

- `snake_case` throughout: `tasks`, `name`, `raw`, `parts`, `cmd`, `found`, `idx`, `task`.
- Loop unpacking uses descriptive names, not single letters: `for idx, task in enumerate(tasks, start=1)` (`app.py:61`).
- Exception variables are named `exc` (`app.py:96`), not `e`.

**Types:**

- No custom classes or dataclasses exist yet. Domain data is represented as a plain `list` of `str` (each task is just a name string). Any change to a richer task representation (e.g. dict with `done` flag) is a structural decision to be made explicitly during `/gsd:discuss-phase` / `/gsd:plan-phase`, not assumed.
- Type hints are used on all function signatures using built-in generics: `tasks: list`, `name: str`, `-> None`, `-> list`, `-> bool` (`app.py:12,27,39`). No `typing.List`/`Optional` imports are used — prefer bare `list`/built-ins consistent with the existing style (this codebase targets Python 3.14, per `python --version` in the dev environment).

## Code Style

**Formatting:**

- No formatter config file present (no `pyproject.toml`, `.ruff.toml`, `black` config). Existing code is hand-formatted but consistent: 4-space indentation, blank line between top-level functions, no trailing whitespace.
- Line length is kept short and readable; no long lines observed (max ~90 chars in docstrings).

**Linting:**

- No `.flake8`, `ruff.toml`, or lint config present in this practice repo. (Note: the parent project `CLAUDE.md` mentions a PostToolUse hook that runs `ruff check --fix + format` on `.py` edits when `ruff` is installed locally — this may apply at the editor/session level even though no config file lives in this repo.)
- If adding lint config for new code, match project-wide conventions: 4-space indent, snake_case, docstrings on every public function.

## Import Organization

**Order:**

1. Standard library only so far: `import sys` (`app.py:9`), `import pytest` (`test_app.py:2`).
2. Local imports follow stdlib/third-party: `from app import add_task, list_tasks, delete_task` (`test_app.py:3`) — explicit named imports, not `import app` or wildcard imports.

**Path Aliases:**

- None. This is a single flat-file module with no package structure or path aliasing.

## Error Handling

**Patterns:**

- Domain validation errors raise built-in exceptions with a descriptive, formatted message: `raise ValueError(f"任務名稱不可為空字串：{name!r}")` (`app.py:23`). Use `!r` repr formatting when embedding the offending value in the message.
- Library/pure functions (`add_task`, `list_tasks`, `delete_task`) raise exceptions rather than printing — they are silent about I/O and only communicate failure via return value (`delete_task` returns `bool`) or exception (`add_task` raises `ValueError`).
- The CLI layer (`main()`) is the only place that catches exceptions and prints user-facing errors: `except ValueError as exc: print(f"錯誤：{exc}", file=sys.stderr)` (`app.py:96-97`). Errors are printed to `stderr`, not `stdout`.
- Keyboard/EOF interrupts are caught explicitly at the input loop boundary: `except (EOFError, KeyboardInterrupt):` (`app.py:75`) — always tuple multiple exception types together when they share the same handling.
- No bare `except:` clauses anywhere in the codebase — always catch specific exception types (this matches the global `code-quality.md` instruction to never use bare `except`).

**New function guidance:**

- When adding `complete_task(tasks, name)`, follow existing conventions: return `bool` (True if found/marked, False if not found) to mirror `delete_task`, OR raise a specific exception only if the operation is genuinely invalid (not merely "not found" — "not found" should be a return value, as in `delete_task`).

## Logging

**Framework:** None — uses `print()` for all user-facing output (this is a CLI teaching demo, not a service).

**Patterns:**

- Success/info messages print to `stdout` via plain `print()`.
- Error messages print to `stderr` via `print(..., file=sys.stderr)` (`app.py:97`).
- User-facing strings are all in Traditional Chinese (繁體中文), per project-wide convention. Any new user-facing string must also be in Traditional Chinese, matching e.g. `"已新增：{...}"`, `"錯誤：{...}"`, `"找不到任務：{...}"`.

## Comments

**When to Comment:**

- Every function has a full docstring, even trivial ones. New functions must include a docstring with `Args:` and `Returns:`/`Raises:` sections following the existing Google-style format (see below).
- Inline comments are sparse and only used for a single "helper function" clarifier (`app.py:57`); logic is otherwise considered self-explanatory through naming.

**JSDoc/TSDoc:**

- N/A (Python project). Docstring style is Google-style with Traditional Chinese prose:

```python
def delete_task(tasks: list, name: str) -> bool:
    """從清單中刪除指定名稱的任務。

    Args:
        tasks: 現有的任務清單（就地修改）。
        name:  要刪除的任務名稱。

    Returns:
        True  — 成功刪除。
        False — 清單中不存在此名稱。
    """
```

- Module-level docstring at the top of `app.py` explains the module's purpose and its role as a "brownfield" learning base (`app.py:1-7`). Keep this pattern when the module's purpose changes (e.g. note when `complete_task` is added).

## Function Design

**Size:** All functions are small (5-15 lines of logic, excluding docstring). Keep new functions under ~20 lines; extract a private `_helper` function (leading underscore) if logic grows, matching the `_print_task_list` pattern.

**Parameters:** Mutating functions take the collection first, then the value: `add_task(tasks, name)`, `delete_task(tasks, name)`. Follow this parameter order for `complete_task(tasks, name)`.

**Return Values:**

- Mutating functions that report success/failure return `bool` (`delete_task` → `True`/`False`), not `None` and not exceptions, when "not found" is an expected, non-exceptional outcome.
- Functions that must reject invalid input outright (e.g., empty name) raise `ValueError` instead of returning a sentinel.
- Functions returning collections return **copies**, not references, to avoid callers mutating internal state accidentally: `list_tasks` returns `list(tasks)` (`app.py:36`), a shallow copy.

## Module Design

**Exports:** No `__all__` defined; all top-level functions are implicitly public except those prefixed with `_` (private convention, e.g. `_print_task_list`).

**Barrel Files:** N/A — single-file flat module, no package `__init__.py` re-exports.

**CLI entry point pattern:** `main()` function contains the interactive loop; guarded by `if __name__ == "__main__": main()` (`app.py:116-117`). Business logic (`add_task`/`list_tasks`/`delete_task`) is kept separate from the CLI/I/O loop so it can be unit-tested without stdin/stdout mocking — preserve this separation when adding `complete_task`.

---

*Convention analysis: 2026-07-22*
