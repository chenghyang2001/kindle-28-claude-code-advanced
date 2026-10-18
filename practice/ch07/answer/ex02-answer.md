# 練習 02 解答：把臃腫 CLAUDE.md 模組化

## 1. 臃腫版
`answer/ex02-bloated-CLAUDE.md`（63 行）：5 段骨架之外，把程式碼風格、測試規則、Git 工作流、本專案例外全部塞在主檔。

## 2. 模組化後（任務 1：抽出 4 個主題）
```text
CLAUDE.md                       # 38 行：5 段骨架 + 4 行 @import
instructions/
├── code-style.md               # 命名、函式長度、編碼、MAX_FILE_BYTES、輸出欄位順序
├── testing.md                  # 3 類測試、data/extra/、覆蓋率 85%
├── git-workflow.md             # [notestat] 前綴、分支命名、tag 格式 ns-v*
└── project-exceptions.md       # 原有的「## 本專案例外」段落（原文保留）
```
主檔結尾：
```markdown
## 詳細規則（@import，依主題拆檔）
@instructions/code-style.md
@instructions/testing.md
@instructions/git-workflow.md
@instructions/project-exceptions.md
```
拆檔方式：用 awk 依 `## ` 標題把臃腫版各段原文切出（不重打，避免抄錯）。

## 3. 任務 2：怎麼確認規則沒漏、import 真的有載入

### (a) 靜態比對：沒漏任何一行
把臃腫版每一行非空、非標題的規則，逐行在「主檔＋4 個 import 檔」中做完整行比對（`grep -qxF`）→ **missing=0**。

### (b) 動態驗證：Claude 真的讀得到 import 檔內容
- 先清掉 `CLAUDE*` 環境變數，再 `claude -p --model haiku`
- 用 `--disallowedTools Read,Grep,Glob,Bash,...` 禁止讀檔，強迫 Claude 只能靠啟動時載入的 context 回答
- 問 4 個**只寫在 import 檔**、主檔沒有的細節

| 問題 | 出處 | 實驗組（本專案） | 對照組（空資料夾） |
| --- | --- | --- | --- |
| MAX_FILE_BYTES | code-style.md | 2 MB（2_097_152）✅ | 不知道 |
| commit 前綴 | git-workflow.md | `[notestat]` ✅ | 沒有專屬前綴 |
| tag 格式 | git-workflow.md | `ns-v<主>.<次>.<修>` ✅ | 不知道 |
| 新範例筆記位置 | testing.md | `data/extra/` ✅ | 不知道 |

原始輸出：`answer/ex02-verify-with-import.txt`、`answer/ex02-verify-control.txt`。
結論：4 題全對、對照組全答不出 → `@import` 在啟動時被展開載入，不是靠讀檔工具臨時查到的。

## 延伸思考：CLAUDE.md vs memory

| | CLAUDE.md（＋@import） | memory（持久記憶） |
| --- | --- | --- |
| 本質 | 專案的**規格與約定**，人寫、人審 | Claude 在工作中**學到的事實與偏好** |
| 版控 | 進 git，團隊共用、可 code review | 通常在個人目錄，不進 repo |
| 適合放 | 執行指令、架構、架構決策、程式風格、測試／git 規範 | 使用者偏好（例：回覆用繁中）、踩過的坑、跨專案的個人習慣、進行中工作的狀態 |
| 變動頻率 | 低，隨專案演進更新 | 高，隨對話累積 |
| 錯了會怎樣 | 全隊的 Claude 都照錯的做 → 要 review | 只影響自己 → 定期清理 |

界線：**「換一個人 clone 這個 repo 也應該知道」→ CLAUDE.md**；**「只有我、或只有這段時間才成立」→ memory**。
例：「commit 前綴 `[notestat]`」放 CLAUDE.md；「使用者偏好快速 demo 模式」放 memory。
