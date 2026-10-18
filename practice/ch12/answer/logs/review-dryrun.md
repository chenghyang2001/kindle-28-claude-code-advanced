## 摘要
這份 diff 把 API 金鑰直接寫死在原始碼裡，也拿掉了 `apply_discount` 原本的輸入檢查，另外新增兩個缺少錯誤處理的函式。目前不建議合併。

## 🔴 必改
1. **機密外洩：`demo/discount.py:4`**
   `COUPON_API_KEY = "sk-live-1234567890abcdef"` 是正式環境（live）金鑰，寫死在原始碼裡，commit 之後就會留在 git 歷史中。
   - 修正：改用環境變數讀取，例如 `COUPON_API_KEY = os.environ["COUPON_API_KEY"]`。
   - 這把金鑰已經出現在 diff 裡，應視為已外洩，請立刻到服務端作廢並換新。如果已經 push，還要清掉 git 歷史裡的這筆紀錄。
2. **金鑰放在 URL 查詢字串，且 `code` 沒有編碼：`demo/discount.py:17`**
   - 金鑰放在 query string，容易被寫進存取日誌、代理伺服器日誌和錯誤訊息。建議改放在 header，例如 `headers={"Authorization": f"Bearer {key}"}`。
   - `code` 直接用 f-string 接進 URL，遇到 `&`、`#` 這類字元時可以竄改參數（參數注入）。建議改成 `requests.get(url, params={"code": code}, headers=..., timeout=5)`。
3. **拿掉輸入檢查會造成錯誤結果：`demo/discount.py:7-9`**
   原本的 `0 <= percent <= 100` 檢查被刪掉了。現在 `percent=150` 會算出負價格，`percent=-50` 會讓價格變高。請把 `ValueError` 檢查加回去。
4. **除以零：`demo/discount.py:13`**
   `prices` 是空串列時，`average_price([])` 會丟出 `ZeroDivisionError`。建議加上 `if not prices: raise ValueError("prices 不可為空")`，或依需求回傳 `0.0`。
5. **網路請求沒有 timeout，也沒檢查狀態碼：`demo/discount.py:17-18`**
   - 沒有設 `timeout`，對方沒有回應時程式會一直卡住。
   - 沒有呼叫 `resp.raise_for_status()`，遇到 4xx/5xx 時會在 `.json()` 或 `["percent"]` 那裡丟出看不懂的錯誤。
   - 回傳的 `percent` 沒有驗證範圍，加上第 3 點拿掉了檢查，外部資料可以直接讓價格變成負數。

## 🟡 建議
- `demo/discount.py:12`、`demo/discount.py:16`：新函式缺少型別標註和 docstring，風格跟 `apply_discount` 不一致。建議補上 `prices: list[float] -> float`、`code: str -> float`，並寫繁體中文 docstring。
- `demo/discount.py:2`：引入了 `requests` 這個第三方依賴，請確認有加進 `requirements.txt` 或 `pyproject.toml`。
- `demo/discount.py:21` 附近：`__main__` 裡的自我測試沒有涵蓋新函式和邊界值（超出範圍的 percent、空串列）。建議補上測試，最好放到 pytest。
- 這個檔案原本的定位是「示範用：計算折扣」，加進網路呼叫會讓職責變得混雜。建議把 `fetch_coupon` 拆到獨立模組，方便 mock 和測試。

## 🟢 做得好的地方
- `.gitignore` 新增了 `.claude/session-state.md`，避免把個人工作階段狀態 commit 進去，這個做法正確。
- `apply_discount` 繼續用 `round(..., 2)` 處理金額精度，保留了原本的行為。
