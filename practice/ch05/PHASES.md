# PHASES — 重構 legacy_order 為 pricing 模組

每個 gate 都由 `python scripts/check_gate.py <N>` 客觀判定（exit 0 = 過關）。未過 gate 不得進下一階段。

## Phase 0 — 合約/規格
- 產出：`contracts/spec.md`、`tests/cases.py`、`tests/snapshot.json`、`tests/test_characterization.py`
- gate 0：
  1. spec.md 含 `## 公開介面`、`## 行為規則`、`## 邊界條件`、`## Never modifies` 四節
  2. spec.md 含 `Status: APPROVED`
  3. 公開介面至少列 1 個函式簽名
  4. 特徵測試對舊模組全綠（行為已鎖住）

## Phase 1 — 骨架
- 產出：`src/pricing.py`（簽名＋docstring＋`NotImplementedError`）、`contracts/CLAUDE.md`（agent 邊界）
- gate 1：
  1. `src/pricing.py` 可編譯、可 import
  2. spec 列出的每個函式都存在，參數與回傳值都有型別註記
  3. `contracts/CLAUDE.md` 存在且含 `Never modifies`
  4. Phase 0 的 gate 仍成立（不回退）

## Phase 2 — 實作（multi-agent，見 answer/ex02-answer.md）
- 產出：pricing 實作、`tests/test_pricing.py`、三個信號檔、審查報告
- gate 2：
  1. `signals/DONE.md`、`signals/BUILD_COMPLETE.md`、`signals/REVIEW_COMPLETE.md` 都存在，且各含 `## Deliverables`、`## Next Steps`、`## Open Questions`
  2. `REVIEW_COMPLETE.md` 寫明 `MUST_FIX: 0`
  3. `tests/test_pricing.py` 全綠，且 `pricing.calculate` 對全部 snapshot 案例逐筆一致
  4. `src/pricing.py` 內不再有 `NotImplementedError`

## Phase 3 — 整合/驗收
- 產出：`legacy_order.calc` 改為委派給 `pricing.calculate`、README 更新
- gate 3：
  1. `legacy_order.py` 呼叫 `pricing.calculate`，且不再含任何計價魔術數字
  2. 全部測試（`python -m unittest discover tests`）綠
  3. `README.md` 提到 `pricing` 模組
  4. gate 0–2 仍成立
