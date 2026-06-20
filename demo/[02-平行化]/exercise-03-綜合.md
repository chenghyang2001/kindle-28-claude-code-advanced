# 練習 03 — 綜合挑戰：設計雙 session 隔離慣例

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
寫一份你自己的「雙 session 隔離 SOP」：何時用 worktree、何時直接在主線、完工如何收尾，讓未來的你零思考照做。

## 範例骨架
```markdown
## 何時開 worktree
- 寫程式 feature：是（短命，feature/<task>，完工 merge 後 remove）
- 非程式任務（文件/研究）：固定一個常駐 docs worktree
- 改一行 typo：否，直接主線

## 收尾紀律
- worktree 內 commit 可安全 git add -A（碰不到別處 WIP）
- 完工：merge 回主線 或 發 PR -> git worktree remove + 刪分支
```

## 限制條件
- 需涵蓋短命 feature worktree 的清理步驟
- 需說明合併回主線的時機（直接 merge vs PR）

## 完成後
將解答存入 `answer/ex03-answer.md`。
