---
phase: 01-task-completion
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - app.py
  - test_app.py
autonomous: true
requirements: [COMP-01, COMP-02, COMP-03]

must_haves:
  truths:
    - "complete_task(tasks, name) sets the named task's done flag to True and returns True (COMP-01)"
    - "complete_task with a name not present returns False and raises no exception (COMP-02)"
    - "complete_task on an already-done task is a no-op and returns True (idempotent, D-04)"
    - "Listing tasks renders completed tasks as '[x] name' and incomplete as '[ ] name' (COMP-03)"
    - "The full pytest suite (existing 12 refactored tests + new complete_task tests) passes green"
  artifacts:
    - path: "app.py"
      provides: "complete_task function + dict-model add_task/list_tasks/delete_task + [x]/[ ] display in _print_task_list"
      contains: "def complete_task"
    - path: "test_app.py"
      provides: "dict-model assertions across existing tests + TestCompleteTask class"
      contains: "class TestCompleteTask"
  key_links:
    - from: "app.py :: add_task"
      to: "tasks list"
      via: "appends {\"name\": str, \"done\": False}"
      pattern: "\\{.*name.*done.*\\}"
    - from: "app.py :: complete_task"
      to: "task dict"
      via: "in-place task[\"done\"] = True"
      pattern: "done.*=.*True"
    - from: "app.py :: _print_task_list"
      to: "task[\"done\"]"
      via: "marker selection [x]/[ ]"
      pattern: "\\[x\\]|\\[ \\]"
---

<objective>
Add task-completion to the existing in-memory Todo CLI by migrating the `tasks` data model from `list[str]` to `list[dict]` ({"name": str, "done": bool}), introducing a new `complete_task(tasks, name)` function, and rendering completion status in the display layer.

Purpose: Deliver COMP-01 (mark task complete by name), COMP-02 (clear failure signal for unknown name), and COMP-03 (visually distinguish completed vs incomplete tasks) per the locked decisions in 01-CONTEXT.md.

Output: Refactored `app.py` (dict model + `complete_task` + `[x]`/`[ ]` markers) and a fully green `test_app.py` (12 existing tests updated to the dict model + new `TestCompleteTask` cases).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/01-task-completion/01-CONTEXT.md
@.planning/phases/01-task-completion/01-PATTERNS.md
@.planning/codebase/CONVENTIONS.md
@.planning/codebase/TESTING.md
@app.py
@test_app.py

<interfaces>
<!-- Locked data model and function contracts (from 01-CONTEXT.md D-01..D-06). -->
<!-- Executor uses these directly — no codebase exploration needed. -->

Task record shape (D-01):
  {"name": str, "done": bool}   # done defaults to False on add_task

Function contracts:
  add_task(tasks: list, name: str) -> None
    appends {"name": name.strip(), "done": False}; keeps existing empty-name ValueError guard.
  list_tasks(tasks: list) -> list
    returns list(tasks) — shallow copy, unchanged logic.
  delete_task(tasks: list, name: str) -> bool
    linear scan: for task in tasks; if task["name"] == name -> tasks.remove(task); return True; else return False.
  complete_task(tasks: list, name: str) -> bool        # NEW
    linear scan: if task["name"] == name -> task["done"] = True; return True (also True if already done — idempotent).
    name not found -> return False (no raise).
  _print_task_list(tasks: list) -> None
    per item: marker = "[x]" if task["done"] else "[ ]"; print "  {idx}. {marker} {name}". Empty-list guard unchanged.

Run command (Windows cp950 — UTF-8 flag required):
  PYTHONUTF8=1 pytest test_app.py -v
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Migrate app.py to dict model and add complete_task</name>
  <files>app.py</files>
  <read_first>
    - app.py (the file being modified — current str-model implementation)
    - .planning/phases/01-task-completion/01-PATTERNS.md (exact before/after excerpts for every function)
    - .planning/phases/01-task-completion/01-CONTEXT.md (locked decisions D-01..D-06)
  </read_first>
  <behavior>
    - complete_task(tasks, "報告") on tasks=[{"name":"報告","done":False}] → returns True, tasks[0]["done"] is True (COMP-01)
    - complete_task(tasks, "不存在") → returns False, no exception, list unchanged (COMP-02)
    - complete_task(tasks, "報告") called twice → second call returns True, still done=True (idempotent, D-04)
    - add_task(tasks, "買牛奶") → tasks == [{"name":"買牛奶","done":False}]
    - _print_task_list prints "[x] name" for done tasks, "[ ] name" for incomplete (COMP-03)
  </behavior>
  <action>
    Apply the dict-model migration across all four existing functions and add the new function, following 01-PATTERNS.md verbatim:
    1. add_task — change only the append line to `tasks.append({"name": name.strip(), "done": False})` per D-01 (done defaults False). Keep the empty-name `ValueError` guard clause exactly as-is.
    2. list_tasks — no logic change; keep `return list(tasks)` (shallow copy per D-05).
    3. delete_task — replace the `if name in tasks` membership test with a linear scan over `tasks`, comparing `task["name"] == name`, then `tasks.remove(task)` on match and `return True`; `return False` after the loop. Keep the "靜默回傳 False" why-comment.
    4. Add `complete_task(tasks: list, name: str) -> bool` immediately after delete_task (before _print_task_list). Linear scan comparing `task["name"] == name`; on match set `task["done"] = True` in place and `return True`; `return False` after the loop (D-03, no raise). Already-done tasks still return True (D-04 idempotent no-op). Use a Google-style Traditional-Chinese docstring with Args:/Returns: and a two-line Returns block (True — 已標記完成（含原本就完成）; False — 找不到該名稱). Add a why-comment explaining idempotent no-op.
    5. _print_task_list — inside the loop compute `marker = "[x]" if task["done"] else "[ ]"` and print `f"  {idx}. {marker} {task['name']}"` per D-06. Keep the empty-list guard ("（目前沒有任何待辦任務）") unchanged.
    Do NOT add a `complete` CLI command to main() — CLI dispatch is out of scope for this phase (01-CONTEXT.md Integration Points). main()'s add/list/delete branches keep working against the new dict model unchanged because they only call the refactored functions.
  </action>
  <verify>
    <automated>PYTHONUTF8=1 python -c "from app import add_task, complete_task, delete_task; t=[]; add_task(t,'報告'); assert t==[{'name':'報告','done':False}]; assert complete_task(t,'報告') is True and t[0]['done'] is True; assert complete_task(t,'報告') is True; assert complete_task(t,'x') is False; assert delete_task(t,'報告') is True and t==[]"</automated>
  </verify>
  <acceptance_criteria>
    - `app.py` imports cleanly and the inline complete_task/add_task/delete_task behavior assertion above exits 0
    - `def complete_task(tasks: list, name: str) -> bool` exists with a Traditional-Chinese Args:/Returns: docstring
    - add_task appends a dict with keys "name" and "done" (done False); no other add_task logic changed
    - delete_task uses a name-keyed linear scan, not `name in tasks`
    - _print_task_list emits the `[x]` / `[ ]` prefix derived from task["done"]
    - main() contains NO new `complete` command branch
  </acceptance_criteria>
  <done>complete_task is implemented with the bool contract (True found/idempotent, False not-found, no raise); all four legacy functions operate on the dict model; display renders completion markers; main() unchanged except via the refactored helpers.</done>
</task>

<task type="auto">
  <name>Task 2: Update test suite to dict model and add TestCompleteTask</name>
  <files>test_app.py</files>
  <read_first>
    - test_app.py (the existing 12 tests being refactored)
    - app.py (the now-dict-model implementation from Task 1 — source of truth for assertions)
    - .planning/phases/01-task-completion/01-PATTERNS.md (test refactor + TestCompleteTask shape)
    - .planning/codebase/TESTING.md (class-per-function, inline state, `assert ... is True/False`, section-separator conventions)
  </read_first>
  <action>
    1. Update the module docstring (line ~4) to mention four functions including complete_task, and update the import to `from app import add_task, complete_task, delete_task, list_tasks` (alphabetical).
    2. Refactor every existing assertion from the str model to the dict model using direct dict comparison, e.g. `assert tasks == [{"name": "買牛奶", "done": False}]` and for ordered/multi cases the matching list of dicts. Apply to TestAddTask (single, multiple-order, strip-whitespace), TestListTasks (returns-copy, empty, same-items), and TestDeleteTask (existing-true, nonexistent-false, empty-false, only-first-occurrence — duplicate-name case becomes two dicts with the same name). The two ValueError tests in TestAddTask stay unchanged (empty / whitespace still raise).
    3. Add a `# ---`-delimited section separator and a new `class TestCompleteTask` after TestDeleteTask covering at minimum: happy path (complete existing → returns True and that task's done is True — COMP-01); not-found (complete missing name → returns False, list unchanged, no raise — COMP-02); idempotent no-op (complete an already-done task → returns True, still done True — D-04); empty-list edge (complete on [] → returns False). Use inline `tasks = [{"name": ..., "done": ...}]` setup, `assert result is True` / `is False` (use `is`, not `==`), after-state assertions on the dict, and Traditional-Chinese method docstrings — mirroring TestDeleteTask structure.
    4. Add a `# ---`-delimited section separator and a new `class TestPrintTaskList` covering COMP-03's display contract using pytest's `capsys` fixture: given `tasks=[{"name":"報告","done":True},{"name":"買菜","done":False}]`, call `_print_task_list(tasks)`, capture `capsys.readouterr().out`, and assert the output contains `"[x] 報告"` and `"[ ] 買菜"`. Import `_print_task_list` from app (it is a module-level helper). This makes COMP-03 (success criterion #3) verifiable by a runnable test, not code inspection only — closes the plan-checker warning.
  </action>
  <verify>
    <automated>PYTHONUTF8=1 pytest test_app.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `PYTHONUTF8=1 pytest test_app.py -v` exits 0 with all tests passing
    - Test count is >= 15 (12 refactored existing + at least 3 new complete_task tests)
    - `class TestCompleteTask` exists and includes happy-path, not-found (False), and idempotent (True) cases
    - `class TestPrintTaskList` exists with a capsys test asserting `[x] ` for a done task and `[ ] ` for an incomplete task (COMP-03 runnable verification — closes plan-checker warning)
    - All existing-test assertions compare against dicts ({"name":..., "done":...}), no remaining bare-string list assertions like `== ["買牛奶"]`
    - The two TestAddTask ValueError tests still pass unchanged
  </acceptance_criteria>
  <done>The complete suite is green under PYTHONUTF8=1; the 12 legacy tests assert the dict model and TestCompleteTask proves the COMP-01/COMP-02/idempotent behaviors.</done>
</task>

</tasks>

<threat_model>

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| CLI stdin → in-memory `tasks` list | User-typed task-name strings enter the process via `input()` in main(); the only untrusted input. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-01-01 | Tampering | task-name string into add/complete/delete | accept | In-memory only, no persistence/DB/eval — a malformed name is just data in a list; empty/whitespace names already rejected by add_task's ValueError guard. No injection sink exists. |
| T-01-02 | Denial of Service | unbounded `tasks` list growth | accept | Single-user local CLI, process-lifetime memory only; out of scope per REQUIREMENTS.md (no persistence). Low severity. |
| T-01-SC | Tampering | dependency / package installs | mitigate | None — no new packages; pure Python standard library (`sys`) + existing pytest. No supply-chain surface introduced this phase. |

Note: No network, no filesystem I/O, no authentication, no serialization, and no untrusted code execution in this phase. Information-disclosure, Repudiation, Spoofing, and Elevation-of-Privilege STRIDE categories are not applicable to an in-process function library.
</threat_model>

<verification>
## Multi-Source Coverage Audit

| Source | Item | Covered By |
|--------|------|------------|
| GOAL (ROADMAP) | Mark tasks complete + see completion status | Task 1 (complete_task + markers), Task 2 (tests) |
| GOAL success #1 | complete_task marks named task done | Task 1, verified Task 2 happy path |
| GOAL success #2 | unknown name → False, no crash | Task 1, verified Task 2 not-found |
| GOAL success #3 | listed tasks visually distinguish done | Task 1 _print_task_list markers |
| GOAL success #4 | new tests pass alongside existing 12 (green) | Task 2 full suite |
| REQ COMP-01 | mark task complete by name | Task 1 complete_task |
| REQ COMP-02 | clear failure signal, no crash | Task 1 (return False / no raise) |
| REQ COMP-03 | distinguish completed tasks | Task 1 [x]/[ ] display |
| RESEARCH | (none — research not run for this phase) | N/A |
| CONTEXT D-01 | str→dict {"name","done"} | Task 1 (all fns) + Task 2 (assertions) |
| CONTEXT D-02 | refactor existing fns + 12 tests stay green | Task 1 + Task 2 |
| CONTEXT D-03 | not-found → False | Task 1 |
| CONTEXT D-04 | already-done → no-op True (idempotent) | Task 1 + Task 2 idempotent test |
| CONTEXT D-05 | list_tasks returns copy | Task 1 (unchanged) + Task 2 copy test |
| CONTEXT D-06 | _print_task_list renders [x]/[ ] | Task 1 |

All GOAL / REQ / CONTEXT items COVERED. Deferred (excluded, not gaps): COMP-04 uncomplete, persistence, priority, `complete` CLI command.

## Phase Checks

- `PYTHONUTF8=1 pytest test_app.py -v` exits 0 (all green)
- Total test count >= 15
- `app.py` has `def complete_task` with bool return; main() has no `complete` branch
</verification>

<success_criteria>

- complete_task(tasks, name) marks the named task done and returns True (COMP-01)
- complete_task with a missing name returns False and raises nothing (COMP-02)
- complete_task on an already-done task returns True without error (D-04 idempotent)
- Listing shows `[x]` for done and `[ ]` for incomplete tasks (COMP-03)
- Existing 12 tests refactored to the dict model + new TestCompleteTask all pass — suite green
</success_criteria>

<output>
Create `.planning/phases/01-task-completion/01-task-completion-01-SUMMARY.md` when done.
</output>
