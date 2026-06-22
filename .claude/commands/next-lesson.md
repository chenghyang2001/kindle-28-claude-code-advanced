---
description: 完成第 N 課後，carry 到 N+1 並進入互動教學模式
argument-hint: <剛完成的課號 N，如 9>
---

# /next-lesson — 換到下一課

剛完成的課號：`$ARGUMENTS`（記為 N）

## 1. carry

執行 study-scaffold 的 carry，把 `[N]/answer/` 複製到 `[N+1]/starter/`：

- 用 Skill 觸發 `study-scaffold`，args 帶 `carry N`。
- carry 失敗（例如 N 是最後一課 17）→ 回報並停。

## 2. 定位下一課

- 在 `demo/` 找 `[N+1-課名]` 目錄（章號補零或原格式皆比對）。
- 開該課 `STEP_LOG.md`；不存在就依該課既有 demo 慣例建立空骨架（標題 + 課程目標 + 練習區）。

## 3. 進互動教學模式（遵守本專案 CLAUDE.md）

- **一次只丟一個問題**，丟完停下等使用者回答。
- 使用者答 → 給回饋；答不出或說「你回答」→ 才給答案 + 對職場新鮮人式解析。
- **未經同意不可執行任何指令**：所有 Bash/git/python/寫檔先「貼出來」等使用者說「執行」。
- 每次回答前照 CLAUDE.md 的語音播報流程（Write `_answer.txt` → taskkill say_ui → start say_ui --autoplay；此三步已長期授權）。

## 4. 先問第一題

進入後，先用一句話摘要「上一課（N）學到什麼 + 這一課（N+1）要學什麼」，然後**只問第一題**，停。
