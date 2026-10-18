# 練習 01 解答：啟用官方外掛並實跑

## 任務 1：啟用外掛

### 安裝指令（專案層）

```bash
claude plugin install pr-review-toolkit@claude-plugins-official --scope project
# ✔ Successfully installed plugin: pr-review-toolkit@claude-plugins-official (scope: project)
```

安裝後 `./.claude/settings.json` 會多出：

```json
{ "enabledPlugins": { "pr-review-toolkit@claude-plugins-official": true } }
```

用 `claude plugin list` 確認：`Scope: project`、`Status: ✔ enabled`。

### 外掛內容與用途

`pr-review-toolkit` 提供一個指令 `/pr-review-toolkit:review-pr [aspects]`，底下有 6 個專職 agent：

| agent | 負責項目 | 何時派出 |
|---|---|---|
| code-reviewer | 一般 bug、CLAUDE.md 規範 | 每次都派 |
| silent-failure-hunter | 吞掉的例外、沒有 log 的失敗 | 有改到錯誤處理時 |
| pr-test-analyzer | 測試是否涵蓋行為與邊界 | 有改到測試時 |
| comment-analyzer | 註解是否跟程式碼一致、是否過期 | 有新增註解或文件時 |
| type-design-analyzer | 型別封裝與不變量 | 有新增型別時 |
| code-simplifier | 去掉冗餘、提高可讀性 | 審查通過之後 |

aspects 參數可以只挑部分 agent 來跑，例如 `code errors tests`。最後會彙整成 Critical / Important / Suggestions / Strengths 四類。

### 適用時機

- **適合**：commit 或發 PR 之前做自我審查；diff 同時改到邏輯、錯誤處理和測試時，多個 agent 各看一個面向，比單一 reviewer 看得完整。
- **不適合**：很小的改動（例如一行 typo），開好幾個 agent 很花 token；還在探索、程式碼每分鐘都在變的階段；純文件的 diff。
- **和內建 `/code-review` 的差別**：內建的版本專門抓正確性 bug，依 effort 等級決定要報多少項。這個外掛是多面向、按 aspect 拆開，而且會額外產出測試和錯誤處理的報告。

## 任務 2：對真實程式碼實跑

### 待審程式碼

先自己寫一段有問題的程式碼，並把問題記在 `answer/planted-bugs.md`。這份紀錄在審查前就移出了 diff，避免審查直接看到答案。

- 基準 commit `21ba6e5`：`src/orders.py` 只有 `load_orders`、`order_total`。
- 待審 commit `ae31c30`：新增 `apply_discount`、`summarize`、`is_vip`，裡面刻意埋了 6 類問題。
- 審查前先實際執行，確認 bug 存在：
  - 3 個測試**全部通過**。
  - 同一筆訂單算兩次，得到 `90` 和 `80`，表示優惠券在呼叫之間累積了。
  - 剛好 1000 元得到 `980`，沒有打 95 折，還被重複扣了優惠券。

### 執行方式

```bash
# 先 unset 所有 CLAUDE* 環境變數
claude -p --setting-sources project,local \
  --allowedTools "Bash(git *)" Read Grep Glob Task Agent \
  "/pr-review-toolkit:review-pr code errors tests -- 用 git diff HEAD~1 HEAD 當待審 diff，只審查不修改"
```

外掛平行派出 code-reviewer、silent-failure-hunter、pr-test-analyzer 3 個 agent。完整原始輸出在 `logs/ex01-review-pr.log`。

### 整理後的輸出（重新分類，不是原樣貼上）

分類規則：
- **必改**：會算錯錢、程式會當掉，或錯誤被吞掉。
- **建議**：不影響正確性，但影響可維護性或測試保護力。
- **備註**：純風格，或需要業務決策。

#### 🔴 必改（4）

| # | 位置 | 問題 | 修法 | 哪些 agent 報了 | 對應預埋 |
|---|---|---|---|---|---|
| 1 | orders.py:20,29 | `coupons=[]` 可變預設參數，優惠券跨呼叫累積 | 改成 `coupons=None`，在函式內複製 | code / errors / tests | P1 ✅ |
| 2 | orders.py:27 | docstring 寫「滿 1000（含）」，程式卻用 `>` | 改成 `>=` | code / tests | P2 ✅ |
| 3 | orders.py:42 | 裸 `except: pass` 吞掉所有例外 | 只捕捉特定例外，並用 `logger.exception` 記錄 | errors / code | P3 ✅ |
| 4 | orders.py:45 | 空清單或全部失敗時會除以零 | 分母為 0 時回傳 `None` | errors / code / tests | P4 ✅ |

#### 🟡 建議（5）

| # | 問題 | 對應預埋 |
|---|---|---|
| 5 | `test_summarize_runs` 只斷言 `failed == 0`，營收或平均算錯也不會失敗 | P6 ✅ |
| 6 | 缺少邊界測試：連續呼叫、剛好 1000、空清單、VIP 加滿額疊加 | P6 ✅ |
| 7 | 優惠券沒有驗證：字串會拋 `TypeError` 後被吞掉，負值會變成加價 | 預埋外的發現 |
| 8 | 折扣後總額沒有下限，負數會悄悄算進營收 | 預埋外的發現 |
| 9 | 失敗只計數、不記原因，事後無從追查 | 預埋外的發現 |

#### ⚪ 備註（4）：交給 simplify 處理

| # | 問題 | 對應預埋 |
|---|---|---|
| 10 | `== True`、`else: total = total`、多餘的 `pass` | P5 ✅ |
| 11 | `is_vip` 沒人呼叫，又跟 `apply_discount` 的判斷重複 | P5 ✅ |
| 12 | `0.95` 寫死在程式裡，應抽成常數 | 預埋外的發現 |
| 13 | 測試檔的 import 放在檔案中段（PEP 8 E402） | 預埋外的發現 |

### 命中率

- 預埋的 6 類問題 **6/6 全部命中**，另外多抓到 7 項預埋外的問題。
- 3 個 agent 互相重疊很多：「除以零」被 3 個 agent 各報一次。外掛最後有自己去重，所以重疊沒有在彙整裡造成重複。
- 外掛寫明「驗證指令被拒，所以都是讀程式推論的」。原因是我只開放了 `Bash(git *)`。下面這幾個 bug 我已經在審查前自己實際執行重現過，所以這份推論可以信任：
  - 優惠券累積：同一筆算兩次得到 `90` 和 `80`。
  - 1000 元邊界：剛好 1000 元得到 `980`，沒打 95 折。
  - 除以零：修正前跑新測試時實際出現 `ZeroDivisionError`。
