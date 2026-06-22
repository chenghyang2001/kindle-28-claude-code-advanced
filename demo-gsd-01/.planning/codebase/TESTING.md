# Testing Patterns

**Analysis Date:** 2026-06-22

## Test Framework

**Runner:**

- pytest 9.0.2
- Config: no `pytest.ini` / `pyproject.toml` — uses pytest defaults with `rootdir` auto-detected

**Assertion Library:**

- pytest built-in `assert` statements
- `pytest.raises` for exception assertions

**Run Commands:**

```bash
PYTHONUTF8=1 pytest test_app.py -v    # Run all tests with verbose output
PYTHONUTF8=1 pytest test_app.py       # Run silently
PYTHONUTF8=1 pytest test_app.py -k "TestAddTask"  # Run one class
```

Note: `PYTHONUTF8=1` is required on Windows (cp950 default encoding) for Traditional Chinese strings in test output.

## Test File Organization

**Location:**

- Co-located with source in project root: `test_app.py` alongside `app.py`

**Naming:**

- File: `test_<module>.py`
- Classes: `Test<FunctionName>` — one class per public function under test
- Methods: `test_<function>_<scenario>` or `test_<function>_<scenario>_<expectation>`

**Structure:**

```
demo-gsd-01/
├── app.py           # Source module
└── test_app.py      # All tests (co-located, single file)
```

## Test Structure

**Suite Organization:**

```python
class TestAddTask:
    """測試 add_task 函式。"""

    def test_add_single_task_happy_path(self):
        """正常新增一筆任務後，清單長度應為 1 且名稱正確。"""
        tasks = []
        add_task(tasks, "買牛奶")
        assert tasks == ["買牛奶"]
```

**Patterns:**

- Each test method sets up its own fresh state (`tasks = []`) — no shared fixtures
- Setup is inline, not in `setUp` or `@pytest.fixture`
- Single logical assertion per test (or a small cluster that proves one behaviour)
- Test docstrings explain the behaviour being verified in Traditional Chinese

**Section separators** delimit test classes visually:

```python
# ---------------------------------------------------------------------------
# add_task 測試
# ---------------------------------------------------------------------------
```

## Mocking

**Framework:** Not used — no `unittest.mock`, no `pytest-mock`

**Patterns:** Not applicable for this codebase — all functions operate on plain Python lists with no external I/O, network calls, or filesystem access to mock.

**What to Mock (when extending):**

- If `main()` CLI is tested, mock `input()` for stdin simulation
- If file persistence is added, mock `open()` / `Path.read_text()`

**What NOT to Mock:**

- The `tasks` list itself — pass a real list to each function

## Fixtures and Factories

**Test Data:**

- Inline literal lists constructed per test — no shared factory or fixture:

```python
tasks = []                          # Empty — for add/delete tests
tasks = ["任務X"]                   # Single item — for list/delete tests
tasks = ["報告", "開會"]            # Multiple items — for order/deletion tests
tasks = ["重複", "重複"]            # Duplicate items — for first-occurrence tests
```

**Location:**

- No separate fixtures file — all setup is inside individual test methods

## Coverage

**Requirements:** Not enforced — no `.coveragerc`, no `--cov` flag in any config

**View Coverage:**

```bash
PYTHONUTF8=1 pytest test_app.py --cov=app --cov-report=term-missing
```

**Current state:** 12 tests covering all 3 public functions (`add_task`, `list_tasks`, `delete_task`). The `_print_task_list` helper and `main` CLI loop are not covered by automated tests.

## Test Types

**Unit Tests:**

- All 12 tests are unit tests — each tests one function in isolation
- State is explicit (passed in), not global

**Integration Tests:**

- None — the CLI `main()` function is not tested end-to-end

**E2E Tests:**

- Not used

## Common Patterns

**Happy Path Testing:**

```python
def test_add_single_task_happy_path(self):
    tasks = []
    add_task(tasks, "買牛奶")
    assert tasks == ["買牛奶"]
```

**Exception Testing:**

```python
def test_add_empty_name_raises_value_error(self):
    tasks = []
    with pytest.raises(ValueError):
        add_task(tasks, "")
```

**Return Value + Side Effect Testing:**

```python
def test_delete_existing_task_returns_true(self):
    tasks = ["報告", "開會"]
    result = delete_task(tasks, "報告")
    assert result is True          # return value
    assert tasks == ["開會"]       # side effect (mutation)
```

**Immutability Testing:**

```python
def test_list_tasks_returns_copy(self):
    tasks = ["任務X"]
    result = list_tasks(tasks)
    result.append("不該出現")
    assert tasks == ["任務X"], "原始清單不應被修改"
```

## Adding New Tests (Guidance)

When adding a new function (e.g., `complete_task`), follow this pattern:

1. Add a new class `TestCompleteTask` in `test_app.py` with a section separator comment
2. Cover at minimum: happy path, not-found case (returns False/no-op), empty list edge case
3. Each test method: inline `tasks = [...]`, call function, assert return value AND list state
4. Docstring in Traditional Chinese describing the behaviour verified

```python
# ---------------------------------------------------------------------------
# complete_task 測試
# ---------------------------------------------------------------------------

class TestCompleteTask:
    """測試 complete_task 函式。"""

    def test_complete_existing_task_returns_true(self):
        """完成存在的任務應回傳 True。"""
        tasks = [...]
        result = complete_task(tasks, "任務名")
        assert result is True
        # assert expected state change
```

---

*Testing analysis: 2026-06-22*
