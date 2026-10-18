# 練習 02 解答 — 用 git bisect run 系統化定位 bug

## 演練環境

| 項目 | 內容 |
| --- | --- |
| 建 repo 腳本 | `ex02/build_repo.sh`（每次重跑都建出同樣 10 個 commit） |
| 演練 repo | `ex02/bisect-demo/`（巢狀 repo，已 gitignore，需要時用腳本重建） |
| 判定腳本 | `ex02/check_cart.py`（放在 repo 外，確保每個 commit 都用同一份測試） |
| 原始輸出 | `ex02/build.log`、`ex02/bisect.log`、`ex02/fix.log` |

repo 內容是購物車計價模組 `cart.py`，10 個 commit：

| commit | 訊息 | 備註 |
| --- | --- | --- |
| c1 e5ec83e | 新增購物車小計 subtotal | 已知 good |
| c2 11c3c84 | 新增 README | |
| c3 04d05e9 | 新增會員九折 | |
| c4 15e9204 | 新增運費規則 shipping（滿 1000 免運） | |
| c5 aa2eb54 | 新增總價 total | |
| **c6 d9eef37** | **重構 shipping 判斷式寫法** | **埋 bug 的地方** |
| c7 b675b3b | README 補充計價規則 | |
| c8 d2c8c5a | 新增金額格式化 | |
| c9 8641775 | 新增 main.py | |
| c10 9ce6c9b | 新增版本號 1.0.0 | HEAD，已知 bad |

> commit hash 是這次實跑產生的；重跑 `build_repo.sh` 時間戳不同，hash 也會不同。

## 任務 1：二分定位 bug（每步紀錄）

### 步驟 0：先寫假設，設計最小實驗

- **症狀**：`python main.py` 買 500×2 = 1000 元，畫面卻顯示 `NT$ 1,060`。
- **假設 H1**：運費邊界錯了（剛好 1000 元沒有免運）。
- **最小實驗**：`total([(500, 2)])` 應該是 1000；再補兩個對照組（未滿 1000、會員折後滿 1000），把它們寫成判定腳本 `check_cart.py`。exit 0 = good、1 = bad、125 = 無法測（跳過）。
- 還沒有 `total()` 的舊 commit（c1–c4）視為 good，因為被測的功能那時還不存在。

### 步驟 1：確認 HEAD 真的壞了

```text
$ python ../check_cart.py
BAD：total([(500, 2)], member=False) = 1060，預期 1000
exit=1
```

觀察結果符合 H1，假設保留。

### 步驟 2：標記好壞端點

```text
$ git bisect start
$ git bisect bad HEAD                 # c10
$ git bisect good e5ec83e             # c1
Bisecting: 4 revisions left to test after this (roughly 2 steps)
[aa2eb54] c5 新增總價 total
```

### 步驟 3：交給 `git bisect run` 自動二分

```text
$ git bisect run python ../check_cart.py
running 'python' '../check_cart.py'
GOOD：3 個案例全過                              ← c5：good
Bisecting: 2 revisions left to test after this (roughly 1 step)
[b675b3b] c7 README 補充計價規則
running 'python' '../check_cart.py'
BAD：total([(500, 2)], member=False) = 1060，預期 1000   ← c7：bad
Bisecting: 0 revisions left to test after this (roughly 0 steps)
[d9eef37] c6 重構 shipping 判斷式寫法
running 'python' '../check_cart.py'
BAD：total([(500, 2)], member=False) = 1060，預期 1000   ← c6：bad
d9eef376e62bed17a63d3526ff07b64cc19e874e is the first bad commit
    c6 重構 shipping 判斷式寫法
 cart.py | 2 +-
bisect found first bad commit
```

範圍變化：`c1..c10`（9 個候選）→ 測 c5 good → `c6..c10` → 測 c7 bad → `c6..c7` → 測 c6 bad → **兇手 c6**。
總共 **3 次測試**（⌈log₂ 9⌉ ≈ 3），手動一個一個試最壞要 9 次。

### 步驟 4：看兇手 diff、驗證假設、結束

```diff
 def shipping(amount):
     """滿 1000 免運，否則 60 元"""
-    return 0 if amount >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE
+    return SHIPPING_FEE if amount <= FREE_SHIPPING_THRESHOLD else 0
```

H1 確認成立。最後用 `git bisect reset` 回到 main（完整 `git bisect log` 存在 `ex02/bisect.log`）。

## 任務 2：根因與修法

### 為什麼會壞

c6 是一個「只改寫法、不改行為」的重構：把三元運算的兩邊對調。對調時比較運算子要從 `>=` 變成 `<`，作者卻寫成 `<=`。結果邊界值 `amount == 1000` 從「免運」變成「收 60 元」。這是典型的 off-by-one 邊界錯誤，而且：

1. commit 訊息寫「重構」，review 的人容易預設行為沒變。
2. c4 只有實作、沒有邊界測試，所以重構時沒有安全網。
3. 1000 剛好是最常見的湊單金額，影響面比看起來大。

### 怎麼改（c11，已實跑）

```diff
-    return SHIPPING_FEE if amount <= FREE_SHIPPING_THRESHOLD else 0
+    return 0 if amount >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE
```

驗證（`ex02/fix.log`）：

```text
$ python ../check_cart.py
GOOD：3 個案例全過
$ python -m pytest -q
4 passed in 0.01s
$ python main.py
NT$ 1,000
```

### 如何防再犯

| 措施 | 做法 |
| --- | --- |
| 邊界回歸測試 | 新增 `test_cart.py`，測 999 / 1000 / 1001 三點，以及 `total([(500,2)]) == 1000` |
| 重構前先有測試 | 規則：沒有測試的函式不准「重構」；先補 characterization test 再改 |
| CI 擋 | 每個 commit 跑 pytest，紅燈不能合併 |
| 判定腳本保留 | `check_cart.py` 可以重複拿來 `git bisect run`，下次找 bug 不用重寫 |
| 寫法 | 避免為了好看對調條件式；比較運算子盡量寫成和需求文字同方向（需求是「滿 1000」就寫 `>= 1000`） |

## 延伸思考：讓 AI 停工的「理由化行為」與 prompt 預防

| AI 的說法 | 真正的問題 | prompt 預防寫法 |
| --- | --- | --- |
| 「檔案太大，無法完整分析」 | 不想讀 | 「用 Read 分段讀，或先 grep 關鍵字縮小範圍；不要以檔案大小為由停止。」 |
| 「測試太複雜，先跳過」 | 不想修測試 | 「測試是驗收標準，必須全綠；測試壞了先修測試再改功能。」 |
| 「可能是很多原因造成的」 | 不想做二分 | 「用 git bisect run 或對半註解程式碼定位，每步貼輸出。」 |
| 「需要更多資訊才能繼續」 | 想把責任丟回來 | 「資訊不足時寫下你的假設並繼續，最後列出假設清單。」 |
| 「這要改動很多地方」 | 怕副作用 | 「做最小修改；副作用寫在回報裡，不要因此停工。」 |
| 「我已經修好了」（沒驗證） | 自證 | 「完成的定義＝貼出測試指令與輸出；沒有輸出就不算完成。」 |

通用預防句型：**「遇到困難時回報你已嘗試的步驟與具體阻礙（含錯誤訊息），不可只說很難。」** 再加上明確的停止條件（例如「bisect 找到 first bad commit 並且修復後 pytest 全綠才算完成」），AI 就沒有模糊空間可以提早收工。
