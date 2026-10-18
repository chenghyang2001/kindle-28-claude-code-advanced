# 合約：重構 legacy_order → pricing 模組

Status: APPROVED
Reviewed-by: 指揮者（主 Claude），2026-10-18

## 目標
把 `src/legacy_order.py` 的 `calc()`（單一長函式＋魔術數字）拆成 `src/pricing.py` 的小函式，
**對外行為完全不變**（以 `tests/snapshot.json` 為準）。

## 公開介面
### `subtotal(items: list[dict]) -> int | float`
### `discount(subtotal: int | float, tier: str | None, coupon: str | None) -> int | float`
### `shipping(net: float, region: str | None) -> int`
### `tax(net: float) -> int`
### `calculate(order: dict, tier: str | None = None) -> dict`

## 行為規則
1. 小計 = Σ price × qty；任一 qty ≤ 0 → `ValueError`。
2. 折扣：VIP 打 10%；SALE 在小計 ≥ 1000 時折 100；其他 0。
3. 優惠券 `OFF50`：（小計 − 前述折扣）≥ 500 時再折 50。
4. 運費：淨額（小計 − 折扣）≥ 1500 免運；否則 remote 150、其他 60。
5. 稅 = round(淨額 × 5%)（Python 內建 round，銀行家捨入）。
6. `calculate` 回傳 `{subtotal, discount, shipping, tax, total}`，total = 淨額 + 運費 + 稅。
7. 魔術數字改為模組層常數。

## 邊界條件
- 空 items → 小計 0、運費 60。
- 折扣型別：VIP 為 float（與舊版一致，不可改成 int）。
- 未知 tier / coupon 視為無折扣。

## Never modifies
- `tests/snapshot.json`、`tests/cases.py`（行為基準，任何 agent 不得改）。

## 指揮者裁決（回應 signals/DONE.md Open Questions）
1. gate 2 加型別比對：每個欄位的 `type()` 必須與 snapshot 舊版輸出一致（int 與 float 不可互換）。
2. OFF50 留在 `discount()` 內處理，不另拆函式，避免判斷基準跑掉。
3. 回傳型別註記改為 `int | float`，與舊版實際行為一致。
4. 缺 `items` / `price` 維持舊行為（拋 KeyError），不新增驗證。
