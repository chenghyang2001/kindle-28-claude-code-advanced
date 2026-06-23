# STEP_LOG — Dynamic Workflows 練習（2026-06-23 完成）

## 學習目標

- [x] 說得出 Dynamic Workflow 是什麼（一句話）
- [x] 講得出何時用、何時改用 skill / loop / schedule / 單一 subagent
- [x] 看懂 hello 腳本的三原語（agent / parallel / pipeline）
- [x] 實跑一次 hello-dynamic-workflow
- [ ] 改一個變數再跑一次（下次練習）

---

## Q&A 紀錄

### Q1：Dynamic Workflow 跟「一次平行派 3 個 agent」差在哪？

- 我的作答：說「你回答」
- 正解：三點差異 —
  1. **控制流**：workflow 有迴圈/條件/預算控制；一次性派 agent 沒有。
  2. **階段**：`pipeline()` 無同步牆，可各自跑到底；一次性 parallel 有牆，全做完同一步才能下一步。
  3. **結果處理**：workflow 用 schema + 程式化彙整/交叉驗證，背景自動；一次性要人腦手動接。

### Q2：四情境配對 → **4/4 全對** ✅

1. 每天 8:00 固定晨間簡報 → **`/schedule`**（雲端定時；若本機監控改 `/loop`）
2. 40 個 PR 各「審查→對抗式驗證」+彙整 → **Dynamic Workflow**
3. 單一錄音轉摘要（一次性） → **單一 Subagent**（若 40 檔批次則升級 workflow）
4. `commit` 高頻固定動作 → **Skill**

- 黃金規律：**項目從 1 個變很多個 = subagent 升級 workflow 的分界線**。

### Q3：hello 腳本三原語指認

- 我的作答：說「你回答」
- 正解：
  - 結構化輸出 = `QUIZ_SCHEMA` + `agent(..., { schema })`
  - 扇出 = `await parallel(TOPICS.map(t => () => agent(...)))`
  - 彙整 = 第二個 `agent(...)`（`phase('Assemble')`，無 schema → 回純文字）
- 重點雷：`parallel()` 放的是 **thunk（`() => agent(...)`）**，不是直接 `agent(...)`。

---

## 實跑觀察

- 預測派幾個 agent：**4**（3 出題 + 1 彙整）→ 實際 **4** ✅
- Run ID：`wf_7145d1d4-15e`｜耗時 ~64 秒｜背景完成
- 進度樹：`Generate` 階段 3 個 `quiz:*` 並排 → `Assemble` 階段 1 個 `assemble`
- 產出：見 [`sample-output-quiz.md`](./sample-output-quiz.md)（workflow 第 3 題自己考了 pipeline vs parallel，等於自我複習）

---

## 我的結論：什麼時候我會主動選 Dynamic Workflow？

- 當任務是「**很多項目 × 多階段 × 要程式化控制（迴圈/扇出/交叉驗證）**」時。
- 單一任務一律先想 subagent / loop / schedule / skill，項目一旦變多再升級 workflow。

---

## 延伸練習（2026-06-23 同日）

### A. `/loop`（決策矩陣左上角）
- 實跑：60 秒間隔、3 次自動停的 self-paced loop（`loop-demo-log.md`）。
- 學到：
  - `/loop` = session 內固定間隔/自抓節奏的重複任務；**停止條件必須寫在 prompt 裡**，否則無限跑。
  - self-paced loop = 一串 **one-shot** 喚醒（受 60 秒下限）；`/loop 1m` = 真正 **recurring cron**（最長 7 天）。
  - **`CronList`/`CronDelete`/`ScheduleWakeup` 是 Claude 內部工具**（叫 Claude 跑，**不是** shell/斜線指令）；`/schedule` 才是使用者能打的斜線指令（雲端 routine）。

### B. 把 workflow 包成 skill（右上 → 左下 降維）
- 產出：`.claude/skills/quiz-workflow/SKILL.md`（內嵌出題 workflow 腳本 + 觸發詞 + 參數）。
- 學到：
  - **skill 不會自己跑 JS**；它是「指示」，被觸發時叫主 Claude 去呼叫 `Workflow` 工具。
  - 效果：原本要貼整段 JS，現在「一句話 + 主題參數」就重跑 → 把右上角強但麻煩的武器降成左下角高頻指令。
  - project skill 放 `.claude/skills/` **熱載入**（`/reload-skills` 或新 session）。
  - 端到端驗證：打 `quiz-workflow Hooks, MCP Servers, Plugins` → skill 觸發 → Workflow 跑 4 agent → 回測驗卷 ✅。

### 成本實感（同日 4 次 workflow 累計）
- 簡單版 ~44 萬 token/次；3 階段交叉驗證版 ~109 萬/次。層數/審查員越多越貴 → 依任務價值取捨。
