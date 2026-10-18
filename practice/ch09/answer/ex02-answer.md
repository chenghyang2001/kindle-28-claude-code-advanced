# 練習 02 解答：review → simplify 串成固定流程

## 任務 1：串接順序與通過條件

```text
[0] 寫碼 + commit
 │
[1] review（/pr-review-toolkit:review-pr code errors tests）
 │   產出：Critical / Important / Suggestions
 │
[2] 修正（人工或指定 Claude 修，只修 Critical 和會出錯的 Important）
 │   每個 bug 都要補一個回歸測試
 │   關卡 A：新測試在「修正前」的程式上必須 FAIL，在修正後必須 PASS
 │
[3] 複審（同一個指令再跑一次）
 │   關卡 B：CRITICAL_COUNT=0，Important 逐條處理（修掉，或寫明延後原因）
 │
[4] simplify（內建 /simplify：reuse / simplification / efficiency / altitude 四個 agent）
 │   在 simplify 之前先保存一份程式快照
 │
[5] 人工複檢
     關卡 C：pytest 全綠
             且 tests/compare_behavior.py 比對快照和新版，差異必須是 0
             且人工看過 diff，確認只動了「寫法」，沒有動「規則」
```

### 為什麼這樣排

- **先 review 再 simplify**：simplify 預設「目前的程式碼是對的」，它的任務是保留行為。如果把 bug 一起「保留」下來，之後就更難發現。例如 `coupons=[]` 被簡化成更漂亮的寫法，bug 還在。
- **關卡 A 要求「修正前會 FAIL」**：證明這個測試真的攔得住這個 bug，不是剛好會過的測試。
- **關卡 C 不能只靠單元測試**：理由見下面的實測。單元測試只驗「我想得到的案例」，simplify 改的通常是「沒人寫測試的語意細節」。

## 任務 2：在真實 diff 上跑完整流程

被審的程式碼是 `src/orders.py` 和 `tests/test_orders.py`，git 歷史如下：

| commit | 步驟 | 內容 |
|---|---|---|
| `ae31c30` | 0 | 新功能，內含預埋問題 |
| `0c32ac6` | 2 | 修 4 個 Critical，加 4 個回歸測試 |
| `04f6355` | 3 之後 | 修複審找到的 2 個 Important，加 3 個測試 |
| `78e896b` | 4–5 | simplify 重構 |

### 步驟 1：review 攔下什麼

細節見 `answer/ex01-answer.md` 與 `logs/ex01-review-pr.log`。

- 攔下 4 個 Critical：可變預設參數、1000 元邊界、裸 except、除以零。
- 另有 6 個 Important、4 個 Suggestions。

### 步驟 2：修正與關卡 A

- 只修 4 個 Critical。冗餘寫法（`== True`、`else: total = total` 等）**刻意不碰**，留給 simplify，讓兩步的職責分開。
- 新增 4 個回歸測試，對應優惠券累積、1000 元邊界、營收數值與失敗計數、空清單與全部失敗。
- **關卡 A 實測**：
  - 用 `git stash` 退回修正前的程式，結果是 `4 failed, 3 passed`，4 個新測試全部失敗。
  - 還原修正後，`7 passed`。✅ 通過

### 步驟 3：複審與關卡 B

完整輸出在 `logs/ex02-step1-rereview.log`。

- **結果 `CRITICAL_COUNT=0`**，4 個 Critical 都確認已修好。✅
- 複審**攔下了第一輪沒抓到的問題**：
  - Important 1：修正後反而產生新問題。`summarize([None])` 在 except 區塊裡呼叫 `o.get("id")`，又拋出 `AttributeError`，整個函式中斷。
  - Important 2：優惠券超過訂單金額時，回傳負數。
- 處理：Important 1 和 2 修掉並補測試（`04f6355`），變成 `10 passed`。Important 3（float 改 Decimal）屬於業務決策，延後處理。Important 4（`== True`）和其他 Suggestions 交給 simplify。

### 步驟 4：simplify 改善了什麼

simplify 的 4 個 agent 平行審查，輸入 diff 存在 `logs/ex02-simplify-input.diff`。我先去重，再決定哪些要套用。

| 建議 | 來源 agent | 處理 |
|---|---|---|
| `apply_discount` 改成呼叫 `is_vip()`，消除重複判斷，`is_vip` 也不再是死碼 | reuse / simplification / altitude | ✅ 套用 |
| 抽出 `BULK_DISCOUNT = 0.95` 常數 | reuse / simplification | ✅ 套用 |
| 刪掉 `else: total = total` 和多餘的 `pass`，`failed = failed + 1` 改成 `+=` | simplification / altitude | ✅ 套用 |
| 優惠券不再「複製 list 再 append」，改成直接迭代 `[*(coupons or []), order.get("coupon", 0)]` | 4 個 agent 都有提 | ✅ 套用。沒有採用 `sum()` 版本，因為浮點數相減的順序不同，最後一位可能不一樣 |
| log 改成 `%r` 印出整筆訂單，拿掉 `isinstance` 特例 | altitude | ✅ 套用（只改 log 文字，不影響回傳值） |
| 成功筆數在迴圈裡直接累計，不再用 `len()` 反推，也因此支援 generator 輸入 | altitude | ✅ 套用 |
| 測試檔的 import 移到檔頭；`test_summarize_runs` 改成斷言完整的三個回傳值 | reuse / simplification | ✅ 套用 |
| `is_vip` 改成 `bool(...)` | 第一輪 review 的建議 | ❌ 跳過，會改變行為（見下方實測） |
| `is_vip` 改成 `is True` | 複審與 altitude 的建議 | ❌ 跳過，會改變行為（見下方實測） |
| 入口統一驗證、改拋自訂的 `InvalidOrder` 例外 | altitude | ❌ 跳過，例外型別會改變，而且超出這次 diff 的範圍。記為後續工作 |
| `logger.exception` 改成 `warning` | efficiency | ❌ 跳過，目前沒有效能問題 |

結果：`src/orders.py` 加 14 行、刪 19 行；`tests/test_orders.py` 加 2 行、刪 6 行；合計淨減 9 行。efficiency agent 判定沒有實質問題。

### 步驟 5：人工複檢與關卡 C

- `pytest`：`10 passed` ✅
- `tests/compare_behavior.py`：用 11 筆輸入 × 3 種呼叫，再加 4 批 `summarize`，比對 simplify 前的快照（`logs/orders-before-simplify.py`）和新版。結果 **差異 0 處** ✅

**反例實驗**（`logs/ex02-step3-harmful-variants.log`）：把兩個審查「看似合理」的簡化建議實際套進去試。

| 改法 | 單元測試 | 行為比對 | 實際影響 |
|---|---|---|---|
| `bool(order.get("vip"))` | **10 passed（沒攔到）** | 4 處差異 ❌ | `vip: "yes"` 原本不算 VIP，改完後算，會多打 9 折 |
| `order.get("vip") is True` | **10 passed（沒攔到）** | 4 處差異 ❌ | `vip: 1` 原本算 VIP，改完後不算 |

這證明關卡 C 只靠單元測試不夠，必須另外做行為比對。

## 延伸思考

### 外掛何時幫倒忙

1. **把「看起來多餘」的語意當成冗餘刪掉**：本次實測的 `== True` 就是例子。lint 規則（E712）和兩個 reviewer 都想改它，但每一種改法都會改變業務規則。外掛不知道 `vip` 欄位實際會出現哪些值，這是資料契約的問題，不是寫法的問題。
2. **修 A 產生 B**：步驟 2 照建議加的 `o.get("id")` log 寫法，又引入一個新的當機點（Important 1）。如果沒有複審關卡，這個問題就會上線。
3. **建議之間互相矛盾**：同一行程式碼，第一輪建議改成 `bool()`，複審建議改成 `is True`，兩者的語意相反。照著做就是在兩次 commit 之間反覆改業務規則。
4. **推論代替驗證**：工具權限不足時，外掛只能「讀程式推論」。報告裡雖然有註明，但很容易被略過。
5. **成本**：小 diff 也會派出 3–4 個 agent，報告比程式碼還長；重疊的發現還要人工去重。

### 如何避免職責重疊

- **依「會不會改行為」劃分**：review 只負責「行為對不對」，可以改行為；simplify 只負責「寫法」，不准改行為。所以步驟 2 刻意不碰冗餘寫法，步驟 4 只要遇到會改語意的建議就一律跳過。
- **讓兩者看不同的 diff**：simplify 只看已經通過複審的版本，不會和 review 同時改同一段程式碼。
- **衝突交給一個裁決點處理**：兩個工具對同一行提出不同建議時，不要直接套用，改成問「這是不是業務規則」。如果是，就寫進 docstring 或測試鎖住。本例在 `is_vip` 的 docstring 寫明「1 算、"yes" 不算」，並保留 `# noqa: E712`，下次審查就不會再提。
- **同一個外掛裡也有重疊**：pr-review-toolkit 自己就有 code-simplifier。如果已經用內建的 `/simplify`，review 時就不要加 `simplify` 這個 aspect，避免兩個簡化器搶改同一段。
