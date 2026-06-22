---
phase: 02-persistence
plan: 01
subsystem: persistence
tags: [json, persistence, file-io, pytest]
requires: [Phase 1 — dict{name, done} 資料結構]
provides: [save_tasks, load_tasks, JSON round-trip]
affects: [app.py, test_app.py]
tech-stack:
  added: []
  patterns: [stdlib-only, UTF-8 with-open, 缺檔回空/嚴重錯誤外拋]
key-files:
  created: []
  modified: [app.py, test_app.py]
decisions:
  - "JSON 序列化用 ensure_ascii=False + indent=2（中文可讀、人類可讀）"
  - "缺檔 load_tasks 回 [] 而非崩潰；壞 JSON 讓 json.JSONDecodeError 外拋（不靜默吞）"
metrics:
  duration: "~5min"
  completed: "2026-06-22"
  tasks: 3
  files: 2
  tests_total: 19
---

# Phase 2 Plan 01: 存檔持久化 (Persistence) Summary

JSON 持久化：以標準庫 `json` 新增 `save_tasks` / `load_tasks` 兩個純函式，讓任務（含 Phase 1 的 `done` 狀態）能無損存讀，round-trip 完全一致，且不破壞既有 15 個測試。

## What Was Built

- **`save_tasks(tasks, path)`**（app.py，PERS-01）：`with open(path, "w", encoding="utf-8")` + `json.dump(..., ensure_ascii=False, indent=2)`；覆寫既有內容；空清單寫出 `[]`。
- **`load_tasks(path)`**（app.py，PERS-02）：缺檔（`os.path.exists` 預檢）回 `[]`；否則 UTF-8 讀取 `json.load`；壞 JSON 讓 `json.JSONDecodeError` 自然外拋。
- **`TestPersistence`**（test_app.py，PERS-03）：4 個測試（全用 `tmp_path` fixture）— round-trip 無損（含順序與 done 布林）、空清單 round-trip、缺檔回 []、壞 JSON `pytest.raises(json.JSONDecodeError)`。

## Verification

- `PYTHONUTF8=1 python -m pytest test_app.py -v` → **19 passed**（既有 15 維持全綠 + 新增 4）。
- save_tasks 自動驗證：檔案含 `買牛奶` 字面（非 \uXXXX）、indent=2、覆寫、空清單寫 `[]`。
- round-trip：`save_tasks → load_tasks == 原資料`（含 done 與順序）；缺檔 → `[]`；壞 JSON → `JSONDecodeError`。
- `requirements.txt` 維持只有 `pytest`（無新增依賴，純標準庫 json/os）。

## Deviations from Plan

None — 計畫按原樣執行。`load_tasks` 缺檔判斷採計畫允許的 `os.path.exists` 預檢方式。

## Commits

- `8dae636` feat(02): 新增 save_tasks / load_tasks（stdlib json 持久化）
- `748c668` test(02): 新增 TestPersistence（round-trip / 空清單 / 缺檔 / 壞 JSON）

## Self-Check: PASSED

- app.py `def save_tasks` / `def load_tasks` 存在 — FOUND
- test_app.py `TestPersistence` + `tmp_path` — FOUND
- 兩個 commit hash 皆在 git log — FOUND
