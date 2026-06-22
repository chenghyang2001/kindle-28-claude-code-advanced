# Testing Patterns

**Analysis Date:** 2026-06-22

## Test Framework

**Runner:**

- pytest (version pinned via `requirements.txt`: `pytest`)
- Runtime cache: `.pytest_cache/` (pytest 9.0.2 observed from `__pycache__` filenames)
- No `pytest.ini`, `pyproject.toml`, or `setup.cfg` — pytest runs with default discovery settings

**Assertion Library:**

- pytest built-in `assert` statements
- `pytest.raises` for exception assertions

**Run Commands:**

```bash
pytest                  # Run all tests
pytest -v               # Verbose output (shows test names)
pytest --tb=short       # Shorter traceback on failure
```

## Test File Organization

**Location:**

- Co-located with source: `test_app.py` sits alongside `app.py` in the project root

**Naming:**

- Test file: `test_<module>.py` — matches pytest default discovery (`test_app.py`)
- Test classes: `Test<FunctionName>` — e.g., `TestAddTask`, `TestListTasks`, `TestDeleteTask`
- Test methods: `test_<scenario>` — e.g., `test_add_happy_path`, `test_delete_non_existent_returns_false`

**Structure:**

```
demo-gsd-02-yolo/
├── app.py
├── test_app.py       # all tests co-located
└── requirements.txt
```

## Test Structure

**Suite Organization:**

```python
class TestAddTask:
    """add_task 的行為測試。"""

    def test_add_happy_path(self):
        """正常新增：任務應出現在清單中，且前後空白被 strip。"""
        tasks: list = []
        add_task(tasks, "  買牛奶  ")
        assert tasks == ["買牛奶"]

    def test_add_empty_name_raises(self):
        """空白名稱應拋出 ValueError 且不汙染清單。"""
        tasks: list = []
        with pytest.raises(ValueError):
            add_task(tasks, "   ")
        assert tasks == []
```

**Patterns:**

- Setup: inline — each test method creates its own fresh `tasks: list = []` (no shared fixtures or `setUp`)
- Teardown: none required — in-memory state, no I/O side effects
- Assertion pattern: `assert <result> == <expected>` or `assert <result> is True/False`
- Each test method has a Traditional-Chinese docstring describing the scenario

## Mocking

**Framework:** None used

**Patterns:**

- No mocking needed — all three functions operate on a plain in-memory `list` with no external I/O, file access, or network calls
- `main()` is not tested (it wraps `input()` / `print()` I/O; testing it would require mocking stdin/stdout)

**What to Mock (if extending):**

- `builtins.input` — if adding tests for `main()`'s interactive loop
- `sys.stdout` / `sys.stderr` — to assert CLI output messages

**What NOT to Mock:**

- The `tasks` list itself — pass a real `list` instance to each function under test

## Fixtures and Factories

**Test Data:**

```python
# Inline construction — each test owns its data
tasks: list = []
tasks = ["a", "b"]
```

**Location:**

- No `conftest.py` or shared fixture file — all test data is inline per method
- No factory functions or faker libraries

## Coverage

**Requirements:** None enforced (no `pytest-cov` in `requirements.txt`, no coverage config)

**View Coverage (if desired):**

```bash
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

## Test Types

**Unit Tests:**

- All 6 tests are pure unit tests: one function, one scenario, isolated in-memory state
- Located in `test_app.py`

**Integration Tests:**

- None present — not needed at current scope (no DB, no external API, no file I/O)

**E2E Tests:**

- Not used

## Common Patterns

**Happy Path:**

```python
def test_add_happy_path(self):
    tasks: list = []
    add_task(tasks, "  買牛奶  ")
    assert tasks == ["買牛奶"]
```

**Exception Testing:**

```python
def test_add_empty_name_raises(self):
    tasks: list = []
    with pytest.raises(ValueError):
        add_task(tasks, "   ")
    assert tasks == []   # side-effect guard: list must stay clean
```

**Return Value + Side Effect:**

```python
def test_delete_happy_path(self):
    tasks = ["a", "b"]
    assert delete_task(tasks, "a") is True
    assert tasks == ["b"]
```

**Isolation Guard (copy test):**

```python
def test_list_returns_copy(self):
    tasks = ["a"]
    returned = list_tasks(tasks)
    returned.append("b")
    assert tasks == ["a"]   # mutation of copy must not affect source
```

---

*Testing analysis: 2026-06-22*
