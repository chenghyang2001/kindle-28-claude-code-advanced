# worktree 綁定筆記 — skill / subagent 如何關聯 git worktree

> 建立：2026-07-04（Session 18）。產出物：`wt-feature` skill + `worktree-builder` subagent。
> 對比參考：`doc/gsd-ralph-vps-demo-summary.md`（⚠️ 昨天 todo 筆記誤寫成 `doc/gsd-ralph-speckit-notes.md`，該檔不存在，以本行為準）。

## 一句話結論

**frontmatter 沒有 `worktree: true` 這種 flag。** worktree 是「行為」不是「宣告」，只能活在兩個地方：①檔案本體的指示文字（路1），②呼叫時的參數（路2）。

frontmatter 實測只吃：

- subagent：`name / description / tools / model / color`
- skill：`name / description / triggers`

## 兩條關聯 worktree 的路

| | 路1：寫進本體 | 路2：呼叫時隔離 |
| --- | --- | --- |
| 做法 | 本體指示 Claude 跑 `git worktree add → cd → 幹活 → remove` | `Agent(..., isolation:"worktree")` 或 Workflow `agent(p,{isolation:'worktree'})` |
| 誰決定隔離 | agent/skill 自己（任何人叫它都隔離） | orchestrator（主 Claude / Workflow script） |
| 誰清理 | 手動（自己或主 agent `worktree remove`） | harness 自動（沒改動自動清） |
| 現成範本 | `/code-session` 指令、本次的 `wt-feature` skill | 「冷靜的指揮官 Commander」實戰版 |
| 缺點 | 綁死 worktree 語意、清理靠人 | 檔案本身「沒 worktree 味」，忘傳參數就不隔離 |

## 本次兩個產出物的定位

- **`wt-feature`（skill，路1）**：把 `/code-session` 從 slash command 改寫成 skill。天生就該在 worktree 跑。位置 `~/.claude/skills/wt-feature/SKILL.md`。
- **`worktree-builder`（subagent，路1 自足 + 路2 相容註解）**：主 agent 派它去實作，它**自建 worktree → 幹活 → 回報 path/branch/commit → 不自行 merge**。步驟 0 會偵測「是否已被 `isolation:"worktree"` 起在隔離環境」，是則跳過自建（兩路相容）。位置 `~/.claude/agents/worktree-builder.md`。

## 關鍵 caveat（踩過才知道）

1. **worktree 隔離很貴**（~200–500ms + 磁碟），只在「多 agent 平行改同批檔會撞 `.git/index.lock`」才值得；單人改幾行別開。
2. **路1-in-subagent 的清理靠人**：worktree 是實體磁碟目錄，不 `remove` 就一直在。自足型 agent 只回報座標、不自刪，主 agent 要記得合併後 `git worktree remove` + `branch -d`。
3. **路2 靠 harness 自動清**，但只清「未改動」的 worktree；有 commit 的要自己收。
4. **Python `.venv` 不要 symlink** 進 worktree（含絕對路徑會壞）。
5. **鐵律遞迴**：subagent context 內寫程式碼**不再**觸發 code-writer/QA（避免無限遞迴），worktree-builder 自己就是 writer。
6. 這三個交付物都是 `.md`，依 `writer-qa-iron-rule` 屬逃生門、**豁免**三 agent 鐵律，故由主 Claude 直接 Write。
