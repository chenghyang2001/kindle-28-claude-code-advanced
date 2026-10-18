# BUILD_COMPLETE — Builder

## Deliverables

- `src/pricing.py`：實作 `subtotal` / `discount` / `shipping` / `tax` / `calculate`，保留骨架簽名與型別註記；14 個魔術數字改為模組層常數（型別與舊版相同：`SALE_DISCOUNT=100`、`OFF50_DISCOUNT=50` 為 int）；各函式附繁中 docstring；未 import `legacy_order`。OFF50 依裁決 2 留在 `discount()` 內。
- `tests/test_pricing.py`（25 個測試）：
  - 各小函式單元測試（含型別斷言：VIP→float、SALE 未達→int 0、shipping/tax→int、空 items→全 int）
  - qty ≤ 0（0 與負數）拋 `ValueError("qty must be positive")`，且逐筆檢查（第一筆就拋）
  - `tests/cases.py` 10 筆對 snapshot 比值，並逐筆對 `legacy_order.calc` 比「值＋key 順序＋每欄位 `type()`」
  - research.md §4 的 7 筆額外案例（OFF50+VIP 兩種、OFF50 觸發免運、小寫 vip、float price、REMOTE 大小寫、qty=0）
  - 缺 `items` 拋 KeyError（裁決 4）
- 測試結果摘要：
  - `PYTHONUTF8=1 python -m unittest discover tests -v` → `Ran 27 tests ... OK`（2 特徵測試＋25 pricing 測試）
  - `PYTHONUTF8=1 python scripts/check_gate.py 2`：
    - [FAIL] 三個信號檔存在且三段完整（等 Reviewer 的 REVIEW_COMPLETE.md，預期）
    - [FAIL] REVIEW_COMPLETE: MUST_FIX: 0（同上，預期）
    - [PASS] test_pricing.py 全綠
    - [PASS] pricing.calculate 與 snapshot 逐筆一致（含型別）
    - [PASS] pricing.py 無 NotImplementedError
  - `check_gate.py 1` → GATE 1: PASS
- 只修改 `src/pricing.py`、新增 `tests/test_pricing.py`、本檔；未 commit。

## Next Steps

（給 Reviewer）

1. 對照 `contracts/spec.md` 行為規則 1–7 與裁決 1–4 審 `src/pricing.py`。
2. 重點檢查型別漂移：常數是否誤寫成 float、`discount` 預設是否為 int 0、運算式是否保留 `subtotal * 0.1`、`net * 0.05`（research.md 陷阱 1、2、7）。
3. 確認 `shipping` / `tax` 吃的是 net（已扣 OFF50），不是 subtotal（陷阱 5）。
4. 跑 `PYTHONUTF8=1 python -m unittest discover tests -v` 與 `check_gate.py 2` 複驗；結果寫入 `reviews/REVIEW.md` 與 `signals/REVIEW_COMPLETE.md`（含 `MUST_FIX: <數字>`）。

## Open Questions

1. 骨架簽名 `discount(subtotal, tier, coupon)` 的參數名 `subtotal` 在函式內遮蔽了同模組的 `subtotal()` 函式。目前無功能影響（discount 內不呼叫 subtotal()），但未來若要在 discount 內呼叫會出錯。是否要在後續 phase 改名（例如 `amount`）？Builder 依「保留骨架簽名」未改。
2. `shipping(net: float, ...)` / `tax(net: float)` 的註記是 `float`，但全 int 訂單時實際傳入 int。與裁決 3 的精神不一致，是否統一改為 `int | float`？（需改合約，交指揮者裁決）
3. 輸入未驗證型別（例如 price 為字串、qty 為 None）時沿用舊行為（TypeError 等），spec 未定義，未新增驗證。
