# Phase 2: 存檔持久化 (Persistence) - Context

**Gathered:** 2026-06-22
**Status:** Ready for planning
**Mode:** Smart discuss (YOLO — recommended answers auto-accepted)

<domain>
## Phase Boundary

讓任務（含 Phase 1 建立的 `done` 完成狀態）能存成 JSON 檔並讀回，達成「重開程式仍保留」。
範圍限定在 `app.py` 新增 `save_tasks` / `load_tasks` 兩個函式 + pytest；本階段不接 CLI 啟動載入/
退出儲存（屬 v2）。直接建立在 Phase 1 的 `dict{name, done}` 結構上。

</domain>

<decisions>
## Implementation Decisions

### JSON 格式

- 直接序列化整個 tasks（`list[dict{name, done}]`）為 JSON 陣列
- 用 `json.dump`，`ensure_ascii=False`（中文任務名可讀）、`indent=2`（人類可讀）
- 一律 UTF-8 編碼（`encoding="utf-8"`，符合 cp950 防禦規則）

### save_tasks 行為

- `save_tasks(tasks, path)`：把目前 tasks 寫入 `path`，覆寫既有內容
- 空清單也正常寫出 `[]`
- 用 `with open(..., "w", encoding="utf-8")` 確保關檔；寫入後不回傳值（或回 None）

### load_tasks 行為

- `load_tasks(path)`：讀回 `list[dict{name, done}]`
- **檔案不存在 → 回 `[]`**（優雅處理，呼應 Phase 1「找不到不拋例外」的一致風格）
- 檔案存在但 JSON 格式損壞 → 讓 `json.JSONDecodeError` 自然往外拋（error case，不靜默吞掉）
- 讀回後結構與存檔前一致（name 與 done 完全還原）

### Round-trip

- `save_tasks` → `load_tasks` 後資料完全一致（含 done 布林、順序）

### Claude's Discretion

- 函式內部寫法、docstring、測試案例命名由實作者決定（與既有 app.py / Phase 1 風格一致）
- 是否回傳 None 或無回傳由實作者決定（不影響行為）

</decisions>

<code_context>

## Existing Code Insights

### Reusable Assets

- Phase 1 已將 task 改為 `dict{name, done}`（見 .planning/phases/01-status/01-01-SUMMARY.md）— `save_tasks` 可直接序列化
- `app.py`：add/list/delete + complete_task / list_pending（Phase 1 完成）
- `test_app.py`：目前 15 個測試全綠（必須維持）

### Established Patterns

- 純函式、標準庫、UTF-8；錯誤處理用例外（嚴重）或布林/空回傳（可預期的「沒有」）
- 檔案 I/O 用 `with` 確保關閉；中文一律 UTF-8

### Integration Points

- `json`（標準庫）；不新增依賴（requirements.txt 維持只有 pytest）
- 測試會用臨時檔路徑（pytest `tmp_path` fixture）做 round-trip 與「檔案不存在」案例

</code_context>

<specifics>
## Specific Ideas

- 必須維持既有 15 個測試全綠（PERS round-trip 不可破壞 Phase 1 行為）
- 測試需含 happy（round-trip 一致）、edge（空清單）、error/edge（檔案不存在 → []）

</specifics>

<deferred>
## Deferred Ideas

- CLI 啟動自動 load、退出自動 save → v2
- 自訂多份清單檔 / 指定預設路徑 → v2

</deferred>
