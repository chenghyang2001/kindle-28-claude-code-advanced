# 練習 02 解答 — 設計 permissions 策略

> 規則只寫在本專案 `.claude/settings.json`（未動全域 `~/.claude/`）。
> 實測腳本：`scripts/ex02-permission-test.sh`，用 `claude -p --model haiku --output-format json --setting-sources project,local`，
> **預設權限模式、沒加任何 bypass 參數**，並清掉 `CLAUDE*` 環境變數。原始 JSON 在 `results/ex02/`。

## 實際使用的設定（`.claude/settings.json`）

```json
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Read(./data/**)",
      "Bash(python scripts/ex01-cost-table.py)"
    ],
    "ask": [
      "Bash(git push:*)",
      "Bash(rm:*)",
      "Write(./scripts/**)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Bash(cat .env*)",
      "Bash(curl:*)"
    ]
  }
}
```

## 任務 1 + 2：規則與風險權衡

| # | 規則 | 類別 | 風險權衡 |
| --- | --- | --- | --- |
| 1 | `Bash(git status)`、`Bash(git diff:*)`、`Bash(git log:*)` | allow | 唯讀、每輪都會用到。攔下來只會讓人一直按「是」，養成不看就按的壞習慣，反而降低安全性。 |
| 2 | `Read(./data/**)` | allow | 範例資料、不含機密，高頻讀取。用路徑限定範圍，而不是放行整個 `Read`。 |
| 3 | `Bash(python scripts/ex01-cost-table.py)` | allow | 只放行**一條完整指令**而不是 `python:*`。`python -c "..."` 可以做任何事，放行 `python:*` 等於放行全部。 |
| 4 | `Bash(git push:*)` | ask | 推上遠端會影響別人、難以撤回（force push 更嚴重）。頻率低，確認一次的成本很小。 |
| 5 | `Bash(rm:*)` | ask | 刪檔不可逆，但偶爾確實需要（清暫存檔），所以用 ask 而不是 deny。 |
| 6 | `Write(./scripts/**)` | ask | 腳本是會被執行的程式碼，改了會影響下一次執行結果，值得人看一眼。 |
| 7 | `Read(./.env)`、`Bash(cat .env*)` | deny | 機密不該進對話 context（會被送到 API、可能寫進 log）。只擋 `Read` 不夠，要連 `cat` 這條旁路一起擋。 |
| 8 | `Bash(curl:*)` | deny | 防資料外洩（把檔案 POST 出去）與下載執行未知腳本。需要抓網頁時用 WebFetch，可以另外控管網域。 |

判斷原則：**可逆 + 唯讀 + 高頻 → allow；不可逆或影響他人 + 低頻 → ask；碰機密或對外送資料 → deny。**

## 實測結果

| 案例 | 預期 | 實際 | 證據（`results/ex02/*.json`） |
| --- | --- | --- | --- |
| `allow-git-status`：執行 `git status` | 放行 | ✅ 放行，回傳 `On branch master / No commits yet` | `permission_denials: []` |
| `allow-read-data`：讀 `data/sales.csv` | 放行 | ✅ 放行，正確回報 6 列資料 | `permission_denials: []` |
| `deny-read-env`：讀 `.env` | 擋下 | ✅ 擋下，工具回傳 *"File is in a directory that is denied by your permission settings."* | `permission_denials` 有 1 筆 `Read` |
| `deny-curl`：`curl -s https://example.com` | 擋下 | ✅ 擋下 | `permission_denials` 有 1 筆 `Bash` |
| `ask-rm`：`rm data/tmp-delete-me.txt` | `-p` 沒有互動確認 → 變成拒絕 | ✅ 被拒絕，**檔案仍存在**（事後 `ls data/` 確認） | `permission_denials` 有 1 筆 `Bash` |

觀察：

- `-p` 模式下 **ask 和 deny 的結果一樣都是拒絕**，JSON 裡兩者都出現在 `permission_denials`，看不出差別。
  差別只在互動模式：ask 會跳確認框，deny 連問都不問。所以要在 CI／排程跑 `-p` 時，
  需要自動執行的操作必須明確寫進 allow（或用 `--allowedTools`），不能依賴 ask。
- `--setting-sources project,local` 很重要：不加的話會一併載入全域使用者設定，那裡的 allow 規則可能讓測試結果失真。
- 每個案例都用 Haiku，單次約 0.0026～0.0031 美元。

## 延伸思考：prompt cache 對成本的影響

練習 01 的 JSON 剛好就是證據：一個只有一句話的 prompt，實際送出約 2.8 萬 token，
其中 1.6～1.9 萬是 `cache_read_input_tokens`（快取命中，約原價 1/10），約 1 萬是 `cache_creation_input_tokens`（寫入快取，比原價貴）。

**快取是「前綴比對」**：從頭開始比，第一個不一樣的地方之後全部要重算。順序大致是
工具定義 → 系統提示（含 CLAUDE.md、settings 推導出的內容）→ 對話歷史。所以會打破 cache 的操作有：

| 操作 | 為什麼打破 cache |
| --- | --- |
| 對話中途切換 model（`/model`） | 快取是每個 model 各自一份，換 model 等於從零開始 |
| 新增 / 移除 MCP server、改變可用工具 | 工具定義在最前面，一改全部前綴失效 |
| 修改 CLAUDE.md 或 settings 中會進系統提示的內容 | 系統提示在對話之前，改了之後整段對話都要重算 |
| `/compact` 或 `/clear` | 對話歷史被重寫，舊前綴作廢（但之後的對話會比較短） |
| 閒置超過快取有效期（5 分鐘或 1 小時） | 快取過期，下一輪重新寫入 |
| 在系統提示裡放時間戳等每次都變的內容 | 每次請求的前綴都不同，永遠命中不了 |

省錢做法：同一個工作階段固定 model 與工具組合；CLAUDE.md 開工前改好、不要邊做邊改；
長時間離開前先收尾，不要讓快取過期後又接著問大問題。
