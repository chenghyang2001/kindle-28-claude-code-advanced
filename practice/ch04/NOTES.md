# NOTES — k28 第 4 章練習（context rot / compact）

> 快速 demo 模式：未經 QA／reviewer 審查。

## 做了什麼

| 項目 | 檔案 |
| ------ | ------ |
| 範例資料：3 份 notes、1 份 CSV、2 份 1800 行 log | `rot-lab/notes/`、`rot-lab/data/` |
| 腐化實驗腳本：`claude -p` + `--resume` 連跑 12 回合 | `scripts/rot-experiment.sh`（可加 `--dry-run`） |
| 實驗紀錄：每回合的 session_id、成本、輸入 token 數、回覆 | `logs/rot-run1.jsonl`、`logs/rot-run2.jsonl`、`logs/*-console.txt` |
| 實驗 session 的產出檔 | `rot-lab/out-run1/`、`rot-lab/out/`（run2） |
| 練習 01 解答 | `answer/ex01-answer.md` |
| 練習 02 解答 | `answer/ex02-answer.md` |
| 壓縮必留清單（實際生效） | `./CLAUDE.md` 的「Compact Instructions」段落 |

## 驗證結果

- 兩輪實驗都跑完 12 回合，exit 0，沒有觸發自動壓縮（`compact_boundary`=0）。模型是 `claude-haiku-5-5`，兩輪合計約 0.5 美元。
- 標準答案用 grep 算出：log-1 的 E404=43／E202=41／E303=39／E505=38／E101=35；log-2 的 E202=52 最多；log-1 前 600 行中 latency>800 的有 65 筆；config.md 的 port 在第 3 回合後被改成 9090（跑完已還原成 8080）。
- 觀察到的症狀：
  - 拿舊檔案內容作答（兩輪都答 8080）
  - 數字對調但加總核對照樣通過（run2 T04）
  - 大檔把 context 塞滿後 Read 被截斷（run1 T05，只讀到 484/1801 行）
  - 沿用前面的結果不重算（T06）
  - 答案變含糊（run2 T07 答「60 筆以上」）
- 沒觀察到：忘記早期決策。T10 的 5 條全對；T11 的誘導也沒成功。輸出檔的日期、檔名、首行、emoji 已用 grep 和 regex 驗證，全部合規。

## 和題目要求的差異

1. **Run 1 被我自己污染**：我把含有 ground truth（port 8080→9090）的必留清單寫進 `./CLAUDE.md`，實驗 session 啟動時讀到了，所以 run1 T09 的回答受到影響。後來把 CLAUDE.md 裡的具體數值拿掉，跑了乾淨的 run2，結論以 run2 為主。這件事本身也是個教訓：**CLAUDE.md 會被同目錄底下的所有子 session 讀到，不要放實驗答案**。
2. 題目寫「刻意把 session 撐長」。這次是用 `claude -p --resume` 自動送 12 個子任務，不是在互動式視窗手動聊天。
3. 實驗用 haiku，不是目前這個主 session 的模型。小模型比較容易出現腐化，也比較省額度。
4. 只有 12 回合，沒有撐到觸發自動壓縮。所以「壓縮後遺失資訊」要等教練對本視窗下 `/compact` 時再驗證。
5. 練習 02 的「全域 settings」改成專案層：必留清單寫在 `./CLAUDE.md`，沒有動 `~/.claude/`。
6. 本章沒用到 MCP、plugin、worktree、GSD／Ralph，所以都沒有安裝或建立。

## /compact 實測（2026-10-18）

教練在主視窗下了：`/compact 保留：目前在做的步驟與下一步、commit hash、已修改檔案路徑、E404/E505 實驗結果、已確定的設計決策`。

### 1. 只憑記憶寫的接續摘要（照 CLAUDE.md 範本）

- 任務：k28 第 4 章 ex01、ex02，寫 NOTES.md 並在本機 commit（不 push）
- 進度：兩輪實驗、兩份解答、CLAUDE.md compact 段落、NOTES.md 都已完成並 commit；正在做壓縮後驗證
- 關鍵 ID：commit `74e6ebe`；run1 `4fd8670e-868b-4049-94c9-33b17da37b26`；run2 `87d04814-c94f-4bdb-a872-c0864a49c3c4`；沒有背景任務
- 待辦：抽查 3 件事 → 對照檔案 → 寫進 NOTES.md → commit

### 2. 抽查 3 件事：先憑記憶回答，再用檔案驗證

| 事項 | 憑記憶的回答 | 驗證方式 | 結果 |
| ------ | -------------- | ---------- | ------ |
| commit hash | `74e6ebe`，在 master，未 push | `git log --oneline` | ✅ 一致 |
| E404/E505 對調 | run2 T04 回報 E505=43、E404=38；實際是 E404=43、E505=38；加總 196 所以自我核對沒抓到 | `jq` 讀 `logs/rot-run2.jsonl` 的 T04；`grep` 重算 big-log-1 | ✅ 一致（session_id 也和 run2 相符） |
| port 被改 | T03 後腳本用 sed 改成 9090，跑完還原成 8080；兩輪 T09 都答 8080 | `scripts/rot-experiment.sh` 第 44、57 行；`rot-lab/notes/config.md` 第 3 行；兩份 jsonl 的 T09 | ✅ 一致（現在檔案是 8080） |

額外核對：兩個 session_id 也和 jsonl 一致。

### 3. 觀察與限制

- 3 件事壓縮後全部保留，數字和 ID 都沒走樣。
- 能保留下來有三個原因，三者互相加強：
  - 教練下 `/compact` 時帶的參數直接點名了 commit hash 和 E404/E505。
  - `CLAUDE.md` 的必留清單要求保留關鍵 ID 和決策。
  - 壓縮前最後一則回覆剛好列出這 3 件事。
- 這次驗證不算完全「只憑記憶」：壓縮後，系統自動把 `NOTES.md`、`answer/ex01-answer.md`、`answer/ex02-answer.md`、`scripts/rot-experiment.sh` 的內容重新附到 context 裡。所以「憑記憶」的部分可能看過這些檔案。不過完整的 session_id 和 run2 T04 的原始回覆只在壓縮摘要和 jsonl 裡，jsonl 是驗證時才去讀的。
- 結論：主動指定保留項目的 `/compact` 有效。但驗證時仍以檔案為準，不把摘要當作事實來源，這和 ex01 症狀 1 的教訓一致。
