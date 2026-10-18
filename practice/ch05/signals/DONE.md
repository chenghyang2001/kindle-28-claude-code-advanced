# DONE — Researcher

## Deliverables
- `docs/research.md`：legacy_order.calc 逐分支 → spec 函式對照、資料流、14 個魔術數字與建議常數名、14 條陷阱（皆實測）、7 筆額外驗證案例。
- 驗證：10 筆 snapshot 案例對舊函式全一致（含型別）。未修改 src/、tests/、contracts/。

## Next Steps
（給 Builder）
1. 在 `src/pricing.py` 模組層定義常數（見 research.md §2），保持 int/float 型別與舊版相同。
2. `subtotal`：從 int 0 起算，逐筆檢查 `qty <= 0` → `ValueError("qty must be positive")`。
3. `discount`：預設 int 0；VIP `subtotal * VIP_DISCOUNT_RATE`；SALE `>= 1000` 才 100；OFF50 判斷 `subtotal - 前述折扣 >= 500`。
4. `shipping(net, region)` 與 `tax(net)` 都吃 net；稅用 `round(net * TAX_RATE)`，不用 Decimal。
5. `calculate`：coupon/region 用 `order.get(...)`，回傳 key 順序 subtotal→discount→shipping→tax→total。
6. `tests/test_pricing.py`：逐筆比 snapshot ＋ **另外斷言型別**（VIP→float、SALE 未達→int、空 items total→int），並加入 research.md §4 案例。
7. 不可動 `tests/snapshot.json`、`tests/cases.py`、`src/legacy_order.py`、`contracts/`。

## Open Questions
1. 特徵測試用 `assertEqual`，`120 == 120.0` 會通過，型別漂移偵測不到。是否要求 gate 2 增加型別比對？（Researcher 不改合約，交指揮者裁決）
2. spec 的 `discount` 簽名把 coupon 獨立成參數、但 SALE/OFF50 都依賴同一個 subtotal——目前簽名足夠，無衝突；只提醒 Builder 不要把 OFF50 拆成另一個函式而改變判斷基準。
3. spec 標註 `subtotal -> float`、`shipping/tax -> int`，但舊版 subtotal 在全 int 價格時回傳 int。型別註記僅為提示，實作應保留舊型別；是否需修正註記為 `int | float`？
4. 缺 `items` key 時舊版拋 KeyError、缺 `price` 也是 KeyError——spec 未定義，建議維持舊行為。
