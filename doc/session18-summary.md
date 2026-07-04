# Session 18 摘要：把「skill / subagent 綁 git worktree」做成兩個交付物 + 兩路 demo

> 日期：2026-07-04 ｜ 題目：worktree 綁定（路1 寫本體 / 路2 呼叫時隔離）｜ 依據：使用者昨天的 todo 筆記

## 這次要解的問題

昨天筆記問：skill / subagent 怎麼「關聯」一個 git worktree？直覺以為 frontmatter 有 `worktree: true` 這種 flag——**沒有**。frontmatter 實測只吃 subagent `name/description/tools/model/color`、skill `name/description/triggers`。結論：**worktree 是「行為」不是「宣告」**，只能寫進本體（路1）或呼叫時給參數（路2）。

## 三個交付物（都是 .md，鐵律逃生門，主 Claude 直接寫）

| 檔案 | 定位 |
|------|------|
| `~/.claude/skills/wt-feature/SKILL.md` | **路1 skill**。`/code-session` 的 skill 版，7 步：取任務名→動態推導路徑→查佔用→從 `origin/$DEFAULT` 建 worktree→偵測相依→開發→自己 merge+清理。「自己做」。|
| `~/.claude/agents/worktree-builder.md` | **路1 自足 + 路2 相容 subagent**。主 agent 派它，它自建 worktree→實作→**只回報座標、不 merge**。步驟 0 偵測是否已在 worktree（路2 起的）→ 是則跳過自建。「派人做」。|
| `doc/worktree-binding-notes.md` | 專案內筆記，記路1/路2 對照 + 修正昨天筆記誤寫的參考檔路徑（`gsd-ralph-speckit-notes.md` 不存在，實為 `gsd-ralph-vps-demo-summary.md`）。|

## 兩路 demo（成果永久留在 repo）

- **路1（demo A）**：`worktree-builder` 自建兄弟目錄 worktree + 分支 `feature/add-greet` → 產出 `demo/wt-demo/greet.py`（問候語 + 空值防禦 + 冒煙測試）→ 回報座標 → 主 agent merge（fast-forward）+ 清理。commit `127af32`。
- **路2（demo B）**：用 `Task(isolation:"worktree")` 呼叫同一個 `worktree-builder`。harness 把 worktree 建在 `.claude/worktrees/agent-afc726.../`、分支名 harness 亂數 `worktree-agent-afc726...`。agent 步驟 0 正確偵測「我已在別人建好的 worktree 裡」→ 回報 `SELF_CREATED: no` → 產出 `demo/wt-demo/farewell.py`。commit `9f74b73`。
- **本 session 收尾 demo B**：因 agent 有 commit，harness 不自動清 → 主 agent 手動 `merge → push → worktree remove → branch -d`。驗證後 `demo/wt-demo/` 下 `greet.py`+`farewell.py` 並存、worktree 清單只剩主目錄、分支只剩 main。

## 帶走的重點

- **一個 agent 吃兩路的關鍵**：步驟 0 用 `[ -f "$(git rev-parse --show-toplevel)/.git" ]` 偵測——linked worktree 的 `.git` 是**檔案**（gitdir 指標）不是目錄。是檔案就代表「已在別人建好的 worktree 裡」，跳過自建。
- **`git branch -d` 前必先 `git push`**：`-d` 安全刪比對 `origin/main`，沒 push 就罵 "not fully merged"。順序恆為 merge→push→worktree remove→branch -d。路1 收 `greet.py` 踩過一次。
- **merge 未必產生 merge commit**：線性後代會 fast-forward，`-m` 被忽略。今天收 `farewell.py` 就是 ff（我先前預測「非 ff」是錯的，據實更正）。
- **路2 的「harness 自動清」只對沒改動的 worktree 生效**：agent 一 commit，worktree 就被視為有價值保留，落回主 agent 手上收。
- 交付物全是 `.md` → 依 writer-qa 鐵律屬逃生門，豁免三 agent 流程。

## commit

- `c832dc6` worktree 綁定筆記
- `127af32` greet.py（路1 demo）
- `9f74b73` farewell.py（路2 demo）
- （skill + subagent 兩檔在 `.claude` repo，commit `8658adb`）
