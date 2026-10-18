# NOTES — K28 第 14 章練習（快速 demo 模式）

## 做了什麼

### 練習 01：弱 vs 強 prompt（實跑 4 次 `claude -p --model haiku`）

- 寫好弱／強兩個 prompt（`ex01/prompts/`），以及共用驗收測試 `ex01/acceptance/test_acceptance.py`（11 個案例）。
- `ex01/run_sandbox.sh`：在系統暫存區建空沙盒、清掉所有 `CLAUDE*` 環境變數，再跑 `claude -p`，最後把產出複製回 `ex01/runs/`。
- 跑了 2 組 × 2 個 prompt：
  - 「載入全域設定」組（預設行為）
  - 「乾淨沙盒」組（`--setting-sources project,local`）
- 解答：`answer/ex01-answer.md`

### 練習 02：git bisect run 自動找兇手

- `ex02/build_repo.sh` 建出 10 個 commit 的購物車 repo，在 c6「重構」時把運費邊界 `>=` 改壞。
- `ex02/check_cart.py` 放在 repo 外，作為 `git bisect run` 的判定腳本。
- 自動二分找到兇手 c6，接著修復（c11）並加上回歸測試。
- 每步輸出存在 `ex02/build.log`、`bisect.log`、`fix.log`。
- 解答：`answer/ex02-answer.md`

## 驗證結果

| 項目 | 結果 |
| --- | --- |
| 弱 prompt × 全域設定 | 沒產出檔案（反問後停下），驗收 0/11 |
| 弱 prompt × 乾淨沙盒 | 214 秒；自帶測試 15 passed，**共用驗收 0/11**（介面不符、CLI 卡在互動選單） |
| 強 prompt × 全域設定 | > 600 秒；自帶 18 passed，共用驗收 **11/11** |
| 強 prompt × 乾淨沙盒 | 93 秒；自帶 32 passed，共用驗收 **11/11** |
| git bisect run | 3 次測試定位到 `d9eef37 c6 重構 shipping 判斷式寫法` |
| 修復後 | `check_cart.py` GOOD、`pytest` 4 passed、`main.py` 輸出 `NT$ 1,000` |

## 和題目要求的差異

1. **練習 01 任務縮小**：照本章補充，改成「CLI 登入模擬」（記憶體帳號表），沒有建 bcrypt＋JWT 服務；密碼改用標準庫 `pbkdf2_hmac`。
2. **任務 1「我寫過的弱 prompt」**：沒有歷史 prompt 可用，改用題目範例縮小後的版本「做一個 CLI 使用者登入系統」。
3. **多跑了一組隔離實驗**：發現 `claude -p` 在空沙盒仍會載入全域 `~/.claude/CLAUDE.md`，所以多跑一組 `--setting-sources project,local`。兩組結果都保留，正式比較以乾淨組為準。沒有修改任何全域檔案。
4. **驗收測試修過一次**：v1 的 CLI 案例太嚴（不允許 `quit` 印 `OK`），v2 放寬。兩版結果都留在 `ex01/acceptance-results-v1.txt` 和 `-v2.txt`。
5. **「強 × 全域設定」的耗時是推估**：執行途中我改了 `run_sandbox.sh`，bash 讀到改動後的腳本，在計時／複製那行出現語法錯誤。產出是事後手動從沙盒複製回來的；耗時只能確定超過 600 秒（第一次前景指令 600 秒逾時時它還在跑）。
6. **bisect 演練 repo 不入版控**：`ex02/bisect-demo/` 是巢狀 git repo，已加進 `.gitignore`，需要時用 `bash ex02/build_repo.sh` 重建。重建時 commit hash 會和紀錄中的不同。
7. **沒有用到外部帳號／付費服務**：`claude -p` 用 Max 訂閱（OAuth），沒有設定 `ANTHROPIC_API_KEY`。`--bare` 模式需要 API Key，所以沒用。
8. **快速模式**：未經 QA／code-reviewer 審查（專案 CLAUDE.md 已豁免）。

## 已知風險／沒處理的部分

- 強 prompt 沒規定 `quit` 要不要輸出，兩次實跑行為不一樣；下次要在 prompt 裡寫清楚。
- 每個組合只跑一次，LLM 輸出有隨機性，樣本數不足以下統計結論。
- 弱版 CLI 預設把資料寫到 `~/.login_cli_users.json`。驗收時它卡在選單、沒有註冊成功，已確認家目錄沒有產生這個檔案。
