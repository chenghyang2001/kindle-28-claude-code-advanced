# 練習 02 解答：讀完本書後的一個月學習路徑

## 任務 1：每週一個可驗收目標

| 週 | 學習重點 | 可驗收目標（怎樣算達成） | 驗收指令 / 檢查方式 |
| --- | --------- | ------------------------ | ------------------- |
| 1 | 平行化（02）＋環境配置（08）套進日常 | 專案層設定可用、CLAUDE.md 有實際規則、至少開過 1 個平行 worktree、學習日誌 3 天以上 | `bash check_week1.sh`（exit 0 = 達成，見下方完整說明） |
| 2 | 實做 1 個 hook（08）＋ 1 個 skill（12） | 專案層 `.claude/settings.local.json` 有 1 個 hook 且觸發時真的產生效果；`.claude/skills/<名稱>/SKILL.md` 存在且能被叫出 | `python -c "import json;d=json.load(open('.claude/settings.local.json',encoding='utf-8'));assert d.get('hooks'),'沒有 hook'"`；`test -f .claude/skills/*/SKILL.md && grep -q '^name:' .claude/skills/*/SKILL.md`；再手動觸發一次並看 hook 的輸出或 log |
| 3 | 用 GSD（05）跑一個真實小專案 | 小專案有 `.planning/` 規劃檔，至少 1 個 phase 跑完並有可執行的成果與測試 | `test -f .planning/ROADMAP.md && ls .planning/phases/*/*SUMMARY*.md`；並執行該專案的測試指令（如 `python -m pytest`）必須全過 |
| 4 | 回顧踩坑紀錄，沉澱成個人守則（練習 03） | `docs/踩坑紀錄.md` 至少 5 條踩坑，每條有「現象 / 原因 / 解法」；整理出 `docs/個人守則.md` ≥ 5 條，且每條都連回對應的踩坑 | `[ $(grep -c '^## ' docs/踩坑紀錄.md) -ge 5 ]`；`[ $(grep -cE '^[0-9]+\.' docs/個人守則.md) -ge 5 ]`；`grep -c '踩坑紀錄' docs/個人守則.md`（≥5 表示每條都有出處） |

原則：每個目標都要「留下可被檢查的檔案或結果」，不能只是「讀過」「懂了」。

## 任務 2：綁定第 1 週的可驗收小目標

**目標**：把平行化＋環境配置套進日常工作流，而且要「真的用了」，不是「設好放著」。

**達成條件（4 項全部 PASS）**：

1. `.claude/settings.local.json` 是合法 JSON，且 `permissions.allow` 至少 1 條（環境配置真的設了）
2. `CLAUDE.md` 至少 5 行（有寫專案規則，不是空檔）
3. `git worktree list` 至少 2 個（主目錄＋1 個平行工作區，代表真的用過平行化）
4. `learning-log/week1.md` 至少 3 筆 `- YYYY-MM-DD` 開頭的記錄（一週內至少 3 天真的用上）

**自動驗收**：`check_week1.sh`

```bash
bash check_week1.sh --dry-run   # 乾跑：只列出要檢查的項目與指令
bash check_week1.sh             # 實際檢查（全部唯讀）；exit 0 = 達成，1 = 未達成
```

實測三種情況：

```text
# (a) 乾跑：列出 4 項 [DRY] 與指令，exit 0

# (b) 剛開始、還沒準備：
[FAIL] 專案層 .claude/settings.local.json 合法且有 permissions.allow
[PASS] CLAUDE.md 至少 5 行
[FAIL] git worktree 至少 2 個（實際用過平行化）
[FAIL] learning-log/week1.md 至少 3 筆日期記錄
結果：PASS 1 / FAIL 3  → 第 1 週目標：未達成（exit 1）

# (c) 建好設定、日誌，並在 repo 內開 .worktrees/week1-demo 之後：
[PASS] ×4
結果：PASS 4 / FAIL 0  → 第 1 週目標：達成（exit 0）
```

（測完已 `git worktree remove` 並刪除 demo 分支。）

## 延伸思考：如何避免「收藏一堆資源卻沒消化」？

1. **輸入要換成輸出**：每看一則來源，學習日誌就要多一行「做了什麼 → 學到什麼」。只有收藏、沒有日誌記錄 = 沒消化。驗收腳本只算日誌，不算書籤。
2. **限制在讀清單的數量**：同時最多 3 個「待消化」項目，要加新的就得先完成或刪掉一個，避免清單無限長大。
3. **驗收寫成程式**：像 `check_week1.sh` 這樣把「達成」定義成可執行的檢查，exit 1 就是沒做完，沒辦法用「大概懂了」騙自己。
4. **固定回顧時間（只寫設計，不建排程）**：每週固定一個時段跑當週的驗收腳本＋ `check_sources.py`，沒過的目標移到下週並寫下原因。要做提醒可以用行事曆或排程工具，本練習依限制不建立。
5. **公開承諾**：把每週目標和驗收結果 commit 進 repo，git log 本身就是學習紀錄，空白的週一眼就看得出來。
