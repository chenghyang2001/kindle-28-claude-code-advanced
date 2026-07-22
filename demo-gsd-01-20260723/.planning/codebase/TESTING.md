# Testing Patterns

**Analysis Date:** 2026-07-22

## Test Framework

**Runner:**

- pytest 8.4.2 (verified via `python -m pytest --version` in this environment; Python 3.14.3)
- Config: no `pytest.ini` / `pyproject.toml` / `setup.cfg` present — pytest runs with default discovery and default settings. `.pytest_cache/` exists from prior runs but contains no custom config.
- Declared dependency: `requirements.txt` lists only `pytest` (`requirements.txt:1`) — no `pytest-cov`, `pytest-mock`, or other plugins installed/declared.

**Assertion Library:**

- Plain `assert` statements (pytest's built-in assertion rewriting). No `unittest.TestCase` assertions, no third-party assertion libraries (e.g. no `hamcrest`, no `assertpy`).
- `pytest.raises(...)` context manager used for exception-based tests (`test_app.py:20,25`).

**Run Commands:**

```bash
PYTHONUTF8=1 pytest test_app.py -v     # Run all tests, verbose (project standard — see GSD-PRACTICE.md)
PYTHONUTF8=1 pytest test_app.py        # Run all tests, quiet
pytest test_app.py -k TestAddTask      # Run a single test class
```

No coverage command is defined (no `pytest-cov` present). No watch-mode command is defined (no `pytest-watch`/`ptw`).

**Windows encoding note:** Always prefix pytest invocations with `PYTHONUTF8=1` per the project's Windows/cp950 convention (test data contains Traditional Chinese strings like `"買牛奶"`, `"任務A"`); this matches the global `code-quality.md` instruction ("執行 Python 腳本務必加 `PYTHONUTF8=1`") and is explicitly documented in `GSD-PRACTICE.md:24`.

## Test File Organization

**Location:**

- Flat, co-located with the module under test: `test_app.py` sits next to `app.py` in the repo root. There is no `tests/` subdirectory.

**Naming:**

- Test file: `test_<module>.py` (pytest default discovery pattern).
- Test classes: `Test<FunctionUnderTest>` grouping by the function being tested — `TestAddTask`, `TestListTasks`, `TestDeleteTask` (`test_app.py:6,34,49`). When adding tests for a new function, create a new `Test<FunctionName>` class (e.g. `TestCompleteTask`) rather than adding loose top-level test functions.
- Test methods: `test_<scenario>_<expected_outcome>` — descriptive, full-sentence-like names, e.g. `test_add_empty_name_raises_value_error`, `test_delete_nonexistent_task_returns_false`, `test_list_tasks_returns_copy` (`test_app.py:18,55,35`). Name format is `test_<action/setup>_<expected_result>`.

**Structure:**

```
test_app.py
├── TestAddTask
│   ├── test_add_single_task_happy_path
│   ├── test_add_multiple_tasks_preserves_order
│   ├── test_add_empty_name_raises_value_error
│   ├── test_add_whitespace_only_raises_value_error
│   └── test_add_task_strips_whitespace
├── TestListTasks
│   ├── test_list_tasks_returns_copy
│   ├── test_list_tasks_empty_list
│   └── test_list_tasks_returns_same_items
└── TestDeleteTask
    ├── test_delete_existing_task_returns_true
    ├── test_delete_nonexistent_task_returns_false
    ├── test_delete_from_empty_list_returns_false
    └── test_delete_only_first_occurrence
```

Total: 12 tests across 3 classes, 100% passing baseline (per `GSD-PRACTICE.md:25`).

## Test Structure

**Suite Organization:**

```python
class TestAddTask:
    def test_add_single_task_happy_path(self):
        tasks = []
        add_task(tasks, "買牛奶")
        assert tasks == ["買牛奶"]
```

(`test_app.py:6-10`)

**Patterns:**

- **Setup:** No shared `pytest.fixture` or `setUp` method exists. Each test method creates its own fresh local state inline at the top of the test body (e.g. `tasks = []` or `tasks = ["任務A"]`). This keeps tests fully independent with zero shared mutable state — follow this pattern for new tests rather than introducing fixtures unless test count grows significantly.
- **Teardown:** None needed — all state is local Python objects (in-memory `list`), no filesystem, network, or DB resources to clean up.
- **Assertion:** Single, direct `assert` per test in most cases, comparing either:
  - the resulting `tasks` list to an expected literal list (`assert tasks == ["買牛奶"]`), or
  - a function's return value to an expected literal (`assert delete_task(tasks, "任務A") is True`) — note use of `is True`/`is False` for boolean returns rather than truthy `assert result`, which is more precise and should be followed for `complete_task`'s return value if it returns bool.
  - Some tests combine two assertions (return value + side-effect on the list), e.g. `test_delete_existing_task_returns_true` checks both the return value and the resulting list state (`test_app.py:50-53`).

## Mocking

**Framework:** None used and none needed — the module under test (`app.py`) has no external dependencies (no I/O, no network, no database, no file access) in its core functions (`add_task`, `list_tasks`, `delete_task`). `pytest-mock`/`unittest.mock` are not imported anywhere.

**Patterns:** N/A — no mocking patterns exist in this codebase.

**What to Mock:**

- Currently nothing requires mocking. If a future function needs to interact with `stdin`/`stdout` (e.g. testing `main()`'s CLI loop), use `monkeypatch` (pytest's built-in, no extra dependency) to patch `builtins.input` and capture `capsys` for stdout — this is the natural next step given zero external dependencies exist yet.

**What NOT to Mock:**

- Do not mock the plain `list` data structure — it is not an external dependency; test it directly with real list operations, as done throughout the existing suite.

## Fixtures and Factories

**Test Data:**

- No `conftest.py`, no `@pytest.fixture`, no factory functions/libraries (e.g. `factory_boy`) exist.
- Test data is inlined directly in each test as small literal Python lists/strings, e.g. `tasks = ["任務A", "任務B"]` (`test_app.py:45`). Task names use realistic Traditional Chinese sample data (`"買牛奶"`, `"任務A"`, `"任務B"`) — follow this style (short, realistic-sounding CJK strings, or generic `任務A`/`任務B` placeholders) for new test data rather than switching to Latin placeholder strings like `"foo"`/`"bar"`.

**Location:**

- Inline within each test method — no separate fixtures file. If shared setup becomes necessary when adding `complete_task` tests, prefer a simple local helper function or a `pytest.fixture` in a new `conftest.py`, but only if duplication becomes a real problem (currently duplication is minimal and inlining keeps each test fully self-contained/readable).

## Coverage

**Requirements:** No coverage tool installed (`pytest-cov` absent from `requirements.txt`) and no coverage threshold enforced anywhere (no CI config, no `pyproject.toml` `[tool.coverage]` section).

**View Coverage:**

```bash
# Not currently available — pytest-cov is not installed.
# To add: pip install pytest-cov && pytest --cov=app test_app.py
```

## Test Types

**Unit Tests:**

- 100% of the existing suite is unit tests — pure function calls against in-memory data structures, no I/O boundary crossed. This is the only test type present and should remain the primary type for `complete_task` as well (unit tests calling the function directly with plain lists).

**Integration Tests:**

- None present. There is no database, external API, or filesystem interaction in this module to integration-test.

**E2E Tests:**

- Not used. The `main()` CLI loop (`app.py:65-113`) is entirely untested — there is a test coverage gap here (no test exercises the `input()`-driven interactive loop, command parsing, or `quit`/unknown-command branches). Any new CLI-level test would need `monkeypatch` for `input()` and `capsys` for output capture (see Mocking section above).

## Common Patterns

**Async Testing:**

- Not applicable — no async code exists in this codebase.

**Error Testing:**

```python
def test_add_empty_name_raises_value_error(self):
    tasks = []
    with pytest.raises(ValueError):
        add_task(tasks, "")
```

(`test_app.py:18-21`) — use `pytest.raises(<ExceptionType>)` as a context manager wrapping only the call under test; no message-matching (`match=...`) is used anywhere, so plain exception-type checking is the established convention.

**Test case shape used for new functions (recommended, matching existing `TestDeleteTask` pattern):**
For `complete_task(tasks, name)`, mirror the three-tier pattern already used for `delete_task`:

1. Happy path — completing an existing task succeeds (`test_complete_existing_task_returns_true` or equivalent, matching whatever return/marking behavior is decided in `/gsd:discuss-phase`).
2. Not-found case — completing a nonexistent task (mirrors `test_delete_nonexistent_task_returns_false`).
3. Empty-list case — completing on an empty list (mirrors `test_delete_from_empty_list_returns_false`).
4. Idempotency/duplicate case — completing an already-completed task (mirrors `test_delete_only_first_occurrence`'s spirit of testing an edge case around repeated operations), especially since `GSD-PRACTICE.md:75` specifies "重複完成視為 no-op（不報錯）" as the expected behavior discussed during the practice's Discuss phase.

---

*Testing analysis: 2026-07-22*
