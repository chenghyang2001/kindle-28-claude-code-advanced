# Research：legacy_order.calc 行為／相依地圖

> Researcher 產出，只讀分析。所有結論已用 `PYTHONUTF8=1 python` 實際呼叫 `legacy_order.calc` 驗證（未改任何檔）。
> 10 筆 `tests/cases.py` 案例對 `tests/snapshot.json` 全部一致（含各欄位型別）。

## 1. 分支 → spec 函式對照

| # | legacy 程式碼（calc 內） | 對應 spec 函式 | 說明 |
| --- | --- | --- | --- |
| 1 | `s = 0`；`for i in o["items"]` 累加 `price*qty` | `subtotal(items)` | 起始值是 **int 0**；空 list 回傳 int 0 |
| 2 | `if i["qty"] <= 0: raise ValueError("qty must be positive")` | `subtotal(items)` | 逐筆檢查，遇到就拋；訊息字串照抄 |
| 3 | `d = 0` | `discount(...)` | 預設折扣 int 0 |
| 4 | `if t == "VIP": d = s * 0.1` | `discount(subtotal, tier, coupon)` | float |
| 5 | `elif t == "SALE": if s >= 1000: d = 100` | `discount(...)` | int；未達門檻維持 int 0 |
| 6 | `if o.get("coupon") == "OFF50": if s - d >= 500: d = d + 50` | `discount(...)` | 門檻比對的是「小計 − 前述 tier 折扣」 |
| 7 | `s2 = s - d` | `calculate`（算 net） | net 在 calculate 裡算，傳給 shipping/tax |
| 8 | `if s2 >= 1500: sh = 0` | `shipping(net, region)` | 用 net（已扣 OFF50）判斷 |
| 9 | `elif o.get("region") == "remote": sh = 150` else `60` | `shipping(net, region)` | 回傳永遠 int |
| 10 | `tax = round(s2 * 0.05)` | `tax(net)` | `round()` 單參數 → int |
| 11 | `return {"subtotal": s, "discount": d, "shipping": sh, "tax": tax, "total": s2 + sh + tax}` | `calculate(order, tier)` | key 順序同舊版；total = net + 運費 + 稅 |

相依關係（資料流）：

```
items ──► subtotal ──► discount(subtotal, tier, order.get("coupon"))
                         │
              net = subtotal − discount
                 ├──► shipping(net, order.get("region"))
                 └──► tax(net)
total = net + shipping + tax
```

注意：`tier` 是 `calculate` 的第二個參數；`coupon`、`region` 來自 `order` dict（用 `.get`，缺 key 視為 None）。`items` 用 `order["items"]`（缺 key 會 KeyError，舊版行為）。

## 2. 魔術數字 → 建議常數名

| 值 | 出處 | 建議常數名 |
| --- | --- | --- |
| `0.1` | VIP 折扣率 | `VIP_DISCOUNT_RATE` |
| `"VIP"` | tier 名 | `TIER_VIP` |
| `"SALE"` | tier 名 | `TIER_SALE` |
| `1000` | SALE 門檻 | `SALE_THRESHOLD` |
| `100` | SALE 折扣額 | `SALE_DISCOUNT` |
| `"OFF50"` | 優惠券代碼 | `COUPON_OFF50` |
| `500` | OFF50 門檻 | `OFF50_THRESHOLD` |
| `50` | OFF50 折扣額 | `OFF50_DISCOUNT` |
| `1500` | 免運門檻 | `FREE_SHIPPING_THRESHOLD` |
| `0` | 免運運費 | `FREE_SHIPPING_FEE`（可選） |
| `"remote"` | 偏遠地區名 | `REGION_REMOTE` |
| `150` | 偏遠運費 | `REMOTE_SHIPPING_FEE` |
| `60` | 一般運費 | `STANDARD_SHIPPING_FEE` |
| `0.05` | 稅率 | `TAX_RATE` |

**常數必須保持與舊版相同的數值型別**：`SALE_DISCOUNT = 100`（int，不可寫 100.0）、`OFF50_DISCOUNT = 50`（int）、`VIP_DISCOUNT_RATE = 0.1`、`TAX_RATE = 0.05`。

## 3. 陷阱清單（實測證據）

1. **VIP 折扣是 float**：`1200 * 0.1 → 120.0`、total `1194.0`。不可 `int()`、不可改 `s // 10` 或 `round`。
2. **SALE 未達門檻是 int 0**：`999, SALE → discount 0`（int），total `1109`（int）。不可預設成 `0.0`。
3. **型別會傳染到 total**：discount 為 float → net、total 都是 float；否則全 int。
4. **OFF50 門檻看「小計 − 前述折扣」**：
   - `540, VIP, OFF50`：540 − 54.0 = 486 < 500 → 不折 → discount `54.0`
   - `1000, VIP, OFF50`：900 ≥ 500 → discount `150.0`（float + int = float）
   - `1100, SALE, OFF50`：1000 ≥ 500 → discount `150`（int）
5. **OFF50 會影響免運判斷**：`1550, OFF50` → net 1500 → 運費 0、稅 75、total 1575。shipping 必須吃 net，不是 subtotal。
6. **稅用內建 round（銀行家捨入）**：`round(50*0.05)=round(2.5)=2`、`1050*0.05=52.5 → 52`、`1350*0.05=67.5 → 68`。不可用 `Decimal`、`math.floor(x+0.5)`、`int()`。
7. **浮點運算式要逐字保留**：VIP 用 `subtotal * 0.1`、稅用 `net * 0.05`；改成 `/ 10`、`/ 20` 在部分浮點值會造成 round 結果不同的風險。
8. **空 items**：`{"items": []}` → `{"subtotal": 0, "discount": 0, "shipping": 60, "tax": 0, "total": 60}`，全部 int（total 是 int 60，不是 60.0）。
9. **比較運算子是 `>=`**（SALE 1000、OFF50 500、免運 1500 都是「達到即適用」）；`1000, SALE` → 折 100。
10. **大小寫敏感**：`"vip"`、`"REMOTE"` 都不生效（視為無折扣／一般運費）。未知 tier/coupon 一律無折扣。
11. **price 為 float 時 subtotal 跟著變 float**：`10.5 × 1 → 10.5`、total `71.5`。不要強制轉型。
12. **qty 檢查是逐筆**：第一筆 qty ≤ 0 就拋 `ValueError("qty must be positive")`，不會先讀後面的項目。
13. **⚠️ 特徵測試抓不到型別漂移**：`assertEqual` 中 `120 == 120.0` 為 True，snapshot 比對即使把 VIP 改成 int 也會「綠」。Builder 必須在 `tests/test_pricing.py` 另外斷言 `type(...)`。
14. `round()` 回傳 int，因此 `tax` 欄位永遠 int；`shipping` 永遠 int。

## 4. 已驗證的額外案例（可直接抄進 test_pricing.py）

| 輸入 | tier | 期望輸出 |
| --- | --- | --- |
| `{"items":[{"price":1000,"qty":1}],"coupon":"OFF50"}` | VIP | `{subtotal:1000, discount:150.0, shipping:60, tax:42, total:952.0}` |
| `{"items":[{"price":540,"qty":1}],"coupon":"OFF50"}` | VIP | `{subtotal:540, discount:54.0, shipping:60, tax:24, total:570.0}` |
| `{"items":[{"price":1550,"qty":1}],"coupon":"OFF50"}` | None | `{subtotal:1550, discount:50, shipping:0, tax:75, total:1575}` |
| `{"items":[{"price":1000,"qty":1}]}` | `"vip"` | `{subtotal:1000, discount:0, shipping:60, tax:50, total:1110}` |
| `{"items":[{"price":10.5,"qty":1}]}` | None | `{subtotal:10.5, discount:0, shipping:60, tax:1, total:71.5}` |
| `{"items":[{"price":1,"qty":1}],"region":"REMOTE"}` | None | `shipping:60` |
| `{"items":[{"price":1,"qty":0}]}` | None | `ValueError` |
