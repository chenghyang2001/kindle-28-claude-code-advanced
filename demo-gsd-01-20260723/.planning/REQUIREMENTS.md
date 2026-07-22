# Requirements — 待辦清單 CLI 完成任務功能

**Defined:** 2026-07-23
**Core Value:** 使用者能標記任務完成、並在清單上一眼看到哪些做完了（✓）

## v1 Requirements

### 完成任務（COMP）

- [ ] **COMP-01**: 使用者可用 `complete <名稱>` 把指定任務標記為已完成（介面風格與 delete 一致）
- [ ] **COMP-02**: 使用者對不存在的任務 complete 時，會看到「找不到任務」的清楚訊息（與 delete 的錯誤風格一致）
- [ ] **COMP-03**: 使用者對已完成的任務再次 complete 時，會看到「已經完成過」的友善訊息（不報錯、狀態不變、單向冪等）
- [ ] **COMP-04**: complete 的名稱比對規則（去頭尾空白、大小寫處理）與既有 delete 完全一致，同一個名稱兩個指令找到的是同一筆任務

### 清單顯示（DISP）

- [ ] **DISP-01**: 使用者執行 `list` 時，已完成任務帶 ✓ 標記、未完成任務不帶，一眼可辨識
- [ ] **DISP-02**: 已完成任務留在清單上（不從清單消失），完成與刪除語意嚴格區分

### 相容性（COMPAT）

- [ ] **COMPAT-01**: 既有 12 個測試全數維持綠燈（行為語意不變；斷言寫法允許隨資料結構調整）
- [ ] **COMPAT-02**: 使用者可用 delete 刪除已完成的任務，刪除行為不因完成狀態而不同
- [ ] **COMPAT-03**: complete 功能有對應的新測試，至少涵蓋：成功完成、找不到任務、重複 complete 三種情境

## v2 Requirements（deferred）

- **v2-01**: `uncomplete <名稱>` 取消完成（獨立指令，非 toggle）— 待 v1 驗證使用者真的需要復原
- **v2-02**: `list --pending` / `list --done` 過濾檢視 — 待清單長度造成視覺干擾時再評估

## Out of Scope

- **toggle 語意**（重複 complete = 取消完成）— 容易誤觸，使用者已明確否決
- **依編號操作**（complete 2）— 與既有「依名稱」定址模型衝突，不引入雙軌介面
- **完成時間戳記** — 額外欄位與格式化複雜度，無「檢視完成歷史」需求驅動
- **持久化**（存檔/資料庫）— 既有系統為 in-memory，屬不同架構量級
- **彩色終端輸出** — 需額外套件，違反 stdlib 極簡約束；純文字 ✓ 已足夠
- **修改 delete 既有行為** — delete_task 已存在且有測試，本次不動其對外語意

## Traceability

<!-- Filled by roadmap: REQ-ID → Phase mapping -->

| REQ-ID | Phase | Status |
| -------- | ------- | -------- |
| COMP-01 | — | Pending |
| COMP-02 | — | Pending |
| COMP-03 | — | Pending |
| COMP-04 | — | Pending |
| DISP-01 | — | Pending |
| DISP-02 | — | Pending |
| COMPAT-01 | — | Pending |
| COMPAT-02 | — | Pending |
| COMPAT-03 | — | Pending |

---
*Last updated: 2026-07-23 after requirements definition*
