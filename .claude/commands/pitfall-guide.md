---
allowed-tools: Read, Write, Grep, Glob, Bash
argument-hint: [課程編號或關鍵字] | --all
description: 掃描本專案 STEP_LOG 與 git 歷史，彙整踩坑紀錄成一份系統化排解指南
---

# 踩坑排解指南生成器

為以下範圍生成踩坑排解指南：$ARGUMENTS（未指定則涵蓋全專案）

## 專案現況（自動收集）

- 最近提交：!`git log --oneline -15`
- 各課紀錄：!`ls demo/*/STEP_LOG.md 2>/dev/null`
- 既有文件：!`ls docs/ doc/ 2>/dev/null`

## 任務

1. **收集踩坑素材**
   - 讀取範圍內的 `STEP_LOG.md`（找「踩坑」「錯誤」「失敗」「排錯」段落）
   - 掃 `docs/` 既有踩坑紀錄，避免重複收錄
   - 從 git commit message 找「修復」「排查」開頭的提交

2. **每個坑用固定四段格式整理**
   - **症狀**：看到什麼錯誤訊息 / 異常行為
   - **根因**：為什麼會發生（不是表面現象）
   - **解法**：實際奏效的步驟或指令
   - **預防**：下次怎麼避免（可否寫進 CLAUDE.md / hook）

3. **按主題分類**（依實際素材調整）
   - Windows 環境（cp950 編碼、路徑轉換、MSYS）
   - Claude Code 設定（plugin、hook、skill 觸發）
   - Git / worktree
   - 其他

4. **輸出**
   - 寫入 `docs/pitfall-guide.md`（已存在則合併更新，不覆蓋既有條目）
   - 條目按「踩到頻率」排序，常見的放前面
   - 每條附上來源（哪一課的 STEP_LOG 或哪個 commit）

注意：只整理**實際踩過**的坑，不要腦補通用性建議；查無素材的分類直接省略。
