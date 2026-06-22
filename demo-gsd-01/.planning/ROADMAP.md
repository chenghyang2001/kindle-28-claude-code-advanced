# Roadmap: Todo CLI（demo-gsd-01）

**Created:** 2026-06-22
**Granularity:** coarse
**Coverage:** 3/3 requirements mapped

## Phases

- [ ] **Phase 1: Task Completion** - 讓使用者能把任務標記為完成，並在列表中區分完成狀態

## Phase Details

### Phase 1: Task Completion

**Goal**: Users can mark tasks as complete and see completion status when listing tasks
**Mode:** mvp
**Depends on**: Nothing (brownfield extension of existing functions)
**Requirements**: COMP-01, COMP-02, COMP-03
**Success Criteria** (what must be TRUE):

  1. User can call `complete_task(tasks, name)` and the named task is marked as done in the list
  2. Calling `complete_task` with a name that does not exist returns a clear failure signal (False or equivalent) without raising an exception or crashing
  3. When tasks are listed, completed tasks are visually distinguishable from incomplete tasks (e.g. `[x]` vs `[ ]` prefix)
  4. All new tests (happy path, edge case, error case for `complete_task`) pass alongside the existing 12 tests — total test suite stays green
**Plans**: 1 plan

Plans:

- [ ] 01-task-completion-01-PLAN.md — dict-model migration + complete_task + [x]/[ ] display + green test suite

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Task Completion | 0/1 | Not started | - |
