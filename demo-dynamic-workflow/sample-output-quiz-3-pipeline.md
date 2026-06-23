# hello-dynamic-workflow 實跑產出 #3（3 階段流水線 + 交叉驗證）

> 2026-06-23 第三次實跑，升級成 pipeline：出題 → 雙審交叉驗證 → 修正 → 彙整。
> Run ID：`wf_e2d5a8c7-24a`｜**10 agent**（3 出題 + 6 審查 + 1 彙整，Refine 0 次）｜~97 秒。
> 對應流程圖：[`last-run-graph.png`](./last-run-graph.png)

---

## 題目

**第 1 題（easy）Slash Commands**：要為專案建一個自訂 `/deploy` 指令，該怎麼做？（單選 A–D）

**第 2 題（medium）CLAUDE.md 記憶**：想把外部檔案（如 `instructions/code-quality.md`）引入 CLAUDE.md 一併載入，用哪種語法？（簡答）

**第 3 題（medium）Output Styles**：關於 Output Styles，下列何者正確？（單選 A–D）

---

## 解答

**第 1 題：B。** 自訂 slash 指令是用 **Markdown 檔**定義：專案層放 `.claude/commands/deploy.md`（檔名＝指令名）→ 打 `/deploy`；全域層放 `~/.claude/commands/`。可用 `$ARGUMENTS`/`$1` 接參數、frontmatter 設 `description`/`allowed-tools`、子目錄成命名空間（`git/commit.md` → `/git:commit`）。本專案 `/chapter-audio`、`/next-lesson` 就是實例。（A settings.json 管權限/hooks 不管指令；C 無 `command create` CLI；D 專案層＋全域層皆可。）

**第 2 題：`@ 路徑` 匯入語法**，例如 `@instructions/code-quality.md`。作用：載入 CLAUDE.md 時把被 `@` 引用的檔案一併讀進記憶，可把龐大規則模組化拆檔、主檔只負責 `@` 串接。本專案 CLAUDE.md 正是用 `@instructions/...` 多行組裝。

**第 3 題：B。** Output Styles **直接改寫系統提示（system prompt）**來改變整體行為（可移除預設的軟體工程指示），不是「附加」一段文字。內建 Default／Explanatory／Learning，用 `/output-style` 切換，可在 `~/.claude/output-styles/` 自訂。（A 是 append 行為；C CLAUDE.md 是附加到脈絡、不同機制；D 不只一種。）

> 實務坑：本機 CLAUDE.md 的「語言鐵律」規定——即使切成英文的 Explanatory/Learning style，回覆仍須繁體中文。這正示範「output style 改系統提示，但**使用者層硬規則可凌駕其上**」。

---

## 這次學到的 pipeline 重點

- `Refine` 階段 **0 次觸發** = 3 題雙審全過 → 交叉驗證在背景把關、只有出問題才介入。
- `pipeline()` **無等待牆**：某題已在 Verify 時，另一題還能在 Generate（見流程圖三條車道並進）。
- 成本：3 階段 + 雙審 → **~109 萬 token**，是簡單版的 2.5 倍。層數越多 token 越貴，依任務價值取捨。
