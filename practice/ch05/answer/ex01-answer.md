# 練習 01 解答 — 把長型專案拆成 GSD 階段

## 選定專案
重構 `src/legacy_order.py`：一個 30 行、包辦小計/折扣/運費/稅且滿是魔術數字的 `calc()`，
目標是拆成 `src/pricing.py` 的五個小函式，**對外行為（含 int/float 型別）完全不變**。
完整定義見專案根目錄 `PHASES.md`。

## 任務 1：Phases 與產出

| Phase | 名稱 | 可驗收產出 |
| --- | --- | --- |
| 0 | 合約/規格 | `contracts/spec.md`、`tests/cases.py`（10 筆案例）、`tests/snapshot.json`（舊行為快照）、`tests/test_characterization.py` |
| 1 | 骨架 | `src/pricing.py`（簽名＋型別＋`NotImplementedError`）、`contracts/CLAUDE.md`（agent 邊界） |
| 2 | 實作（多代理） | pricing 實作、`tests/test_pricing.py`、`docs/research.md`、`reviews/REVIEW.md`、三個信號檔 |
| 3 | 整合/驗收 | `legacy_order.calc` 改為委派、`README.md` |

## 任務 2：Gate 條件（全部由 `scripts/check_gate.py <N>` 判定，exit 0 才放行）

| Gate | 客觀條件 |
| --- | --- |
| 0 | spec 含「公開介面／行為規則／邊界條件／Never modifies」四節；含 `Status: APPROVED`；至少 1 個函式簽名；特徵測試對舊模組全綠 |
| 1 | `pricing.py` 可 `py_compile` 且可 import；spec 列的每個函式都存在且參數/回傳都有型別註記（`inspect.signature` 檢查）；`contracts/CLAUDE.md` 含 Never modifies；gate 0 不回退 |
| 2 | 三個信號檔存在且各含 Deliverables/Next Steps/Open Questions；`MUST_FIX: 0`；`test_pricing.py` 全綠；`pricing.calculate` 對 snapshot 逐筆值與**型別**都相同；無 `NotImplementedError` |
| 3 | legacy 呼叫 `pricing.calculate` 且無計價魔術數字（regex）；`unittest discover` 全綠；README 提到 pricing；gate 0–2 不回退 |

每個條件都是「檔案存在 / 字串出現 / 測試 exit code / 值相等」，沒有「感覺差不多」。

## 實際執行結果
- Phase 0 完成後：gate 0 PASS、gate 1 FAIL（pricing.py 還不存在）→ 證明 gate 能擋人。
- 反向測試：把 spec 的 `Status: APPROVED` 改成 `DRAFT` → gate 0 FAIL，還原後 PASS。
- Phase 1 完成後：gate 1 PASS，gate 2 五項全 FAIL（尚未實作）。紀錄：`logs/gates-after-phase1.txt`。
- 最後 gate 0–3 全 PASS，紀錄：`logs/gates-final.txt`。

## 驗收標準
- [x] 至少 3 個階段，每階段有可驗收產出（4 個）
- [x] 每個 gate 客觀可判定（腳本自動判定，並做過反向測試）
