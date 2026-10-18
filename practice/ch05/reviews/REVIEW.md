# REVIEW：src/pricing.py 與 tests/test_pricing.py

> Reviewer 產出（只讀審查，沒有修改 src/、tests/、contracts/）。審查基準：`contracts/spec.md`（含指揮者裁決 1–4）、`docs/research.md`、`src/legacy_order.py`。

## 結論

**MUST_FIX: 0**。`pricing.calculate` 跟 `legacy_order.calc` 在值、key 順序、每個欄位的 `type()`、例外型別與訊息上都一致；合約規則 1–7 和裁決 1–4 全部符合，Builder 也沒有越權。

## 逐條對照合約

| 項目 | 結果 | 依據 |
| --- | --- | --- |
| 規則 1 小計、qty ≤ 0 拋 ValueError | ✅ | 從 int 0 開始累加，逐筆檢查，訊息照抄舊版 |
| 規則 2 VIP 10%、SALE ≥1000 折 100 | ✅ | 保留 `subtotal * 0.1`，`SALE_DISCOUNT = 100` 是 int |
| 規則 3 OFF50 看「小計 − 前述折扣」 | ✅ | `subtotal - amount >= 500` |
| 規則 4 運費吃 net | ✅ | `shipping(net, ...)`，net 已扣 OFF50 |
| 規則 5 稅用內建 round | ✅ | `round(net * TAX_RATE)`，保留 `* 0.05` |
| 規則 6 回傳 dict、key 順序、total 公式 | ✅ | key 順序跟舊版相同 |
| 規則 7 常數放模組層 | ✅ | 14 個魔術數字都改成常數（另有 `NO_DISCOUNT`、`QTY_ERROR_MESSAGE`），數值型別跟舊版相同 |
| 邊界：空 items、VIP 是 float、未知 tier/coupon | ✅ | 已實測 |
| 裁決 1 型別逐欄比對 | ✅ | `test_matches_legacy_values_and_types`、gate 2 都 PASS |
| 裁決 2 OFF50 留在 discount() | ✅ | |
| 裁決 3 註記用 `int \| float` | ✅（subtotal/discount） | shipping/tax 的參數註記見 NICE_TO_HAVE 2 |
| 裁決 4 缺 items/price 拋 KeyError | ✅ | 已實測 |
| 不 import legacy_order | ✅ | pricing.py 沒有任何 import |

## MUST_FIX

（無）

## NICE_TO_HAVE

1. **參數名遮蔽函式名**：`discount(subtotal, ...)` 的參數 `subtotal` 遮蔽了模組裡的 `subtotal()` 函式。現在沒有功能影響，但之後在 discount 內呼叫 `subtotal()` 會出錯。建議下一個 phase 改名為 `amount`（要先改合約的公開介面）。
2. **shipping/tax 參數註記**：`net: float` 跟實際傳入的值（全 int 訂單時是 int）不一致，建議統一成 `int | float`，跟裁決 3 的精神一致（只改註記，不影響行為）。
3. **補隨機比對測試**：目前測試只有固定案例（10 筆 snapshot＋5 筆額外）。建議把下方「驗證 2」的隨機比對（固定 seed、幾百筆）寫成一個測試，日後改動時防止型別漂移。
4. **門檻邊界測試還可以補**：`SALE+OFF50`（例如 1049/1050 會跨過 OFF50 門檻）、`OFF50` 讓 net 從 1549 降到 1499 的「差一點免運」、`VIP` 加上免運門檻（1666/1667）。這些組合 Reviewer 已實測過一致，只是測試套件裡還沒有。
5. `test_matches_snapshot` 只比值；型別由 `test_matches_legacy_values_and_types` 涵蓋，功能上沒問題，可以考慮在 snapshot 那個測試裡也加 `types_of` 斷言，讓測試意圖更直接。

## 對 Builder Open Questions 的建議

1. **`subtotal` 參數遮蔽**：建議改名為 `amount`，但這屬於公開介面變更（呼叫端如果用 keyword 傳參會壞），要由指揮者先改合約再排進後續 phase；本輪維持現狀，不算 MUST_FIX。
2. **shipping/tax 註記改成 `int | float`**：建議同意。只改註記、不影響執行期行為，gate 1 的註記完整性檢查也不受影響。
3. **輸入型別驗證**：建議維持現狀，不新增驗證。目前跟舊版一樣拋相同的 TypeError/KeyError（見「驗證 3」），加驗證反而會改變對外行為、違反「行為不變」的目標。如果真的需要，應該另開一個需求。

## 執行過的驗證與結果

1. `PYTHONUTF8=1 python -m unittest discover tests -v` → **Ran 27 tests, OK**。
2. **隨機比對（seed=42，20,000 筆）**：items 0–4 筆，price 混合 int、float、小額，tier ∈ {None, VIP, SALE, vip, GOLD, ""}，coupon ∈ {None, OFF50, off50, X}，region ∈ {None, remote, REMOTE, city}，也包含 key 不存在的情況。逐筆比對值、key 順序、每欄位 `type()` → **mismatch 0**。
3. **門檻邊界窮舉**：price ∈ {499, 500, 549, 550, 999, 1000, 1049, 1050, 1499, 1500, 1549, 1550, 1551, 1666, 1667} × 全部 tier × coupon × region → **全部一致（含型別）**。
4. **例外一致性**：qty=0、第二筆 qty 為負數 → `ValueError('qty must be positive')`；`{}` → `KeyError('items')`；缺 price、缺 qty → KeyError；price 為字串、qty 為 None → TypeError，訊息跟舊版完全相同。
5. 其他：qty 為 `True`（bool）時結果一致；`calculate` 不會修改傳入的 order（deepcopy 比對）。
6. `PYTHONUTF8=1 python scripts/check_gate.py 2`：test_pricing 全綠、snapshot 逐筆一致、無 NotImplementedError 三項 **PASS**。兩項 FAIL 是因為本檔與 REVIEW_COMPLETE.md 還沒產出，屬於預期。
7. `bash scripts/check_boundaries.sh builder 0e5309f HEAD` → 變更只有 `signals/BUILD_COMPLETE.md`、`src/pricing.py`、`tests/test_pricing.py`，**邊界 OK**。`tests/snapshot.json`、`tests/cases.py`、`src/legacy_order.py` 從 8e6e24a 之後都沒有改動。
