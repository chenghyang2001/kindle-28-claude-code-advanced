# NOTES：第 9 章練習（官方外掛：review → simplify）

## 做了什麼

1. **安裝外掛（專案層）**
   - 指令：`claude plugin install pr-review-toolkit@claude-plugins-official --scope project`，安裝成功。
   - `claude plugin list` 顯示 `Scope: project` / `✔ enabled`。
2. **製造真實 diff**
   - 先 commit 基準版 `src/orders.py`（`21ba6e5`）。
   - 再 commit 一個刻意埋了 6 類問題的功能（`ae31c30`）。
   - 預埋清單放在 `answer/planted-bugs.md`。審查時這份清單已移出 diff，避免審查直接看到答案。
3. **練習 01**：用 `claude -p` 實跑 `/pr-review-toolkit:review-pr code errors tests`，並把輸出重新分類成必改／建議／備註。
4. **練習 02**：照 review → 修正（關卡 A）→ 複審（關卡 B）→ simplify → 人工複檢（關卡 C）跑完整條流程。
   - simplify 使用 Skill 工具執行內建 `/simplify`：4 個 agent 平行審查，再由我去重並套用。
   - 另外寫了行為比對腳本 `tests/compare_behavior.py`。
5. **移除外掛**：`claude plugin uninstall pr-review-toolkit@claude-plugins-official --scope project`。

## 驗證結果

| 項目 | 結果 |
|---|---|
| 外掛審查命中率 | 預埋 6/6 命中，另多抓 7 項預埋外的問題 |
| 關卡 A（回歸測試真的攔得住） | 修正前的程式 `4 failed, 3 passed`，修正後 `7 passed` |
| 關卡 B（複審） | `CRITICAL_COUNT=0`；另攔下 2 個修正時新引入或漏掉的 Important，已修掉，`10 passed` |
| simplify | 套用 7 項、跳過 4 項；程式淨減 9 行 |
| 關卡 C（行為不變） | `pytest` 10 passed；行為比對差異 0 處 |
| 反例實驗 | 兩個「看似合理」的 `is_vip` 簡化，單元測試都照樣 10 passed，但行為比對各抓到 4 處差異 |

原始輸出都保存在 `logs/`：
- `ex01-review-pr.log`：第一輪審查
- `ex02-step1-rereview.log`：複審
- `ex02-simplify-input.diff`：simplify 的輸入 diff
- `ex02-step2-simplify.diff`：simplify 套用後的 diff
- `ex02-step3-harmful-variants.log`：反例實驗
- `plugin-uninstall.log`：外掛移除紀錄

## 外掛移除結果

- `claude plugin uninstall ... --scope project` 顯示 `✔ Successfully uninstalled plugin: pr-review-toolkit (scope: project)`。
- **有殘留**：卸載後 `.claude/settings.json` 還剩 `{"enabledPlugins": {}}`，也就是一個空的鍵。
  - 處理：這個檔案是安裝外掛時才產生的，裡面沒有其他設定，所以直接 `git rm` 刪掉。現在 `.claude/` 目錄已不存在。
  - 確認：`grep -rn enabledPlugins .claude` 沒有結果；`claude plugin list` 已經沒有這個外掛的 project scope 項目。
- 外掛快取 `~/.claude/plugins/cache/claude-plugins-official/pr-review-toolkit/` 是 CLI 安裝時自己寫入的。依限制不手動修改全域目錄下的檔案，所以沒有清除它。

## 和題目要求的差異

- 題目的 `/plugin` 互動式管理介面，改用非互動的 CLI `claude plugin install/list/uninstall`，原因是全自動執行。
- 練習 02 的 `/code-review` 使用外掛的 `/pr-review-toolkit:review-pr`，沒有用內建的 `/code-review`。`/simplify` 用的是內建技能。
- 外掛的 `claude -p` 審查只開放 `Bash(git *)` 等唯讀工具，所以報告內容是「讀程式推論」。關鍵 bug 我已經在審查前自己實際執行重現過，詳見 ex01 解答。
- `.claude/settings.json`（含 `enabledPlugins`）曾在基準 commit `21ba6e5` 一併 commit 進 git 歷史，最後一個 commit 刪除它。
- 額外做了題目沒要求的「行為比對腳本」和「反例實驗」，用來證明關卡 C 光靠單元測試不夠。
- 沒有建立 GitHub repo、沒有 push、沒有修改 `~/.claude/` 底下的設定檔。
