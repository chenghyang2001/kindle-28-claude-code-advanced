# 練習 03 解答 — 雙 session 隔離 SOP

> 以互動問答（Q1～Q2）方式完成，收斂成一套可照做的個人規矩。

## Q1：何時開 worktree、何時不開

| 任務 | 決定 | 為什麼 |
|------|------|--------|
| 新功能（改很多檔、做好幾天） | ✅ 開（短命 worktree） | 改動大、時間長，最需隔離；做完 merge 後拆 |
| 改 typo / 一行設定 | ❌ 不開（直接主線） | 開 worktree 成本 > 收益，殺雞用牛刀 |
| 文件 / 研究（非程式） | ✅ 開（常駐 worktree） | 想跟程式主線隔開，但非一次性 → 開固定常駐的 |

**worktree 兩種用途**：
- 🔥 短命型：一任務一個，做完拆。`feature/<task>` + `<repo>-<task>`。
- 🏠 常駐型：固定一個重複用。`docs/non-coding` + `<repo>-docs`，不拆。

判準：**改動大/時間長 → 開；一次性小修 → 不開；非程式但想隔離 → 開常駐。**

## Q2：短命 worktree 收尾流程

```bash
1. # 在 worktree 內：最後 commit（這裡 git add -A 安全，碰不到別處 WIP）
   git add -A && git commit -m "..."
2. # 交回主線（二選一）
   git push -u origin feature/<task>   # 走 PR：push → 開 PR → merge
   # 或切回主工作樹後 git merge feature/<task>   # 直接 merge
3. git worktree remove ../<repo>-<task>   # 收砧板
4. git branch -d feature/<task>           # 砍分支（先合併才刪得掉）
5. git worktree list                      # 確認乾淨
```
順序不能顛倒：**先合併、再刪分支**（沒合併 `branch -d` 會擋你，是保護機制）。

## 完整 SOP（最終交付物）

```markdown
## 何時開 worktree
- 新功能（改很多/做好幾天）：短命 worktree（feature/<task>，做完拆）
- 一次性小修（typo/一行設定）：不開，直接主線
- 文件/研究（非程式）：固定常駐 worktree（docs/non-coding，不拆）

## 紀律
- worktree 內可安全 git add -A（碰不到別處 WIP）

## 短命 worktree 收尾
1. worktree 內 commit
2. 交回主線（PR 或 merge）
3. git worktree remove
4. git branch -d（先合併才砍得掉）
5. git worktree list 確認
```

## 一句話總結
SOP 的三根支柱：**該不該開（看改動大小/是否程式）、開哪種（短命 vs 常駐）、怎麼收（合併→remove→刪分支）。**
