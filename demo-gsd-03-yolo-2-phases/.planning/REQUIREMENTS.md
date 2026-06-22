# REQUIREMENTS — 待辦清單 CLI 擴充（v1）

> 來源：PROJECT.md。兩個有先後關係的能力群：任務完成狀態（先）→ 存檔持久化（後）。
> 持久化依賴完成狀態的資料結構，故拆為循序兩階段。

## v1 Requirements

### 任務完成狀態（Status）

- [x] **STAT-01**: task 以 `dict{name, done}` 儲存（取代純字串），既有 add/list/delete 行為不變
- [x] **STAT-02**: 使用者可用 `complete_task(tasks, name)` 把指定任務標記為已完成（done=True）
- [x] **STAT-03**: 使用者可用 `list_pending(tasks)` 只取得尚未完成（done=False）的任務
- [x] **STAT-04**: 既有 6 個測試維持全綠；新增 Status 相關 pytest 測試（含 happy/edge/error）

### 存檔持久化（Persistence）

- [x] **PERS-01**: 使用者可用 `save_tasks(tasks, path)` 將任務（含 done 狀態）寫成 JSON 檔
- [x] **PERS-02**: 使用者可用 `load_tasks(path)` 從 JSON 檔讀回任務，還原 name 與 done
- [x] **PERS-03**: 存檔→讀回 round-trip 後資料一致；新增 Persistence 相關 pytest 測試（含 happy/edge/error）

## v2 Requirements（deferred）

- CLI 指令接上新函式（`complete` / `pending` / 啟動載入、退出儲存）— 本里程碑聚焦函式層
- 自訂存檔路徑 / 多份清單檔

## Out of Scope

- 資料庫儲存 — JSON 已足夠，避免過度工程
- 多使用者 / 認證 — 單機單人工具
- Web / GUI — 維持 CLI

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| STAT-01 | Phase 1 | Complete |
| STAT-02 | Phase 1 | Complete |
| STAT-03 | Phase 1 | Complete |
| STAT-04 | Phase 1 | Complete |
| PERS-01 | Phase 2 | Complete |
| PERS-02 | Phase 2 | Complete |
| PERS-03 | Phase 2 | Complete |
