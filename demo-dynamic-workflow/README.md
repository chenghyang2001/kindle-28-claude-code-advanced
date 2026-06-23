# Demo：Dynamic Workflows（動態工作流）練習

> 目標：搞懂 Claude Code 的 **Dynamic Workflows** —— **何時用、怎麼用、為什麼用，以及不用它時有哪些替代方案**。
> 對應你那張「決策矩陣：我該部署哪種自動化武器？」的**右上角**那一格。

---

## 0. 一句話定義

**Dynamic Workflow = 由 Claude 執行的「JS 腳本驅動多代理編排」。**
你寫一段 JavaScript，用 `agent()` / `parallel()` / `pipeline()` 等原語，**用程式的控制流（迴圈、條件、扇出 fan-out）去指揮一群 subagent**，最後把結果彙整回來。

⚠️ 它**不是**一個你用鍵盤打的 `/slash` 指令。它是 Claude 內部的 `Workflow` 工具——你「請 Claude 做大規模/需交叉驗證的多代理任務」時，Claude 才會啟動它。所以「練習」的方式是：**讀懂腳本 → 叫 Claude 用這支腳本跑一次**。

---

## 1. 決策矩陣：四種自動化武器怎麼選

兩個軸：**執行頻率**（按需觸發 ↔ 持續執行）×**規模/複雜度**。

| 象限 | 武器 | 適合 | 典型場景 |
|------|------|------|---------|
| 左下 | **Skills** | 日常高頻、重複性指令 | `/chapter-audio`、`/commit` |
| 左上 | **/loop & /schedule** | 持續監控、定期的**單一**任務 | 每 5 分鐘看 CI、每天早上跑晨間簡報 |
| 右下 | **Subagents** | 複雜架構**單次觸發**，要乾淨上下文 | 派一個 code-reviewer 審這個 PR |
| 右上 | **Dynamic Workflows** | **巨量規模、需交叉驗證的持續協同** | 對 50 個檔案各跑「審查→對抗式驗證」兩階段 |

> 心法：**單一任務**往左/往下；**很多項目 × 多階段 × 要程式化控制**往右上。

---

## 2. 為什麼用（WHY）—— 它解決什麼痛點

一般你叫 Claude「平行派 3 個 agent」是可以的（一則訊息塞多個 Agent 呼叫），但**那是「一次性扇出」**：你沒辦法寫迴圈、沒辦法「item A 跑到第 3 階段時 item B 還在第 1 階段」、沒辦法「跑到沒有新發現才停」、沒辦法用 token 預算動態決定規模。

Dynamic Workflow 給你**確定性的控制流**：

- **扇出（fan-out）**：`parallel()` 同時跑 N 個，`pipeline()` 讓每個 item 獨立走完多階段（沒有階段間的等待牆）。
- **交叉驗證**：找到一個結論後，再派 3 個「唱反調的驗證者」去反駁，多數通過才採信（adversarial verify）。
- **迴圈到乾**：一直找 bug，連續 K 輪沒新發現才停。
- **規模超過單一 context**：大遷移、全庫稽核，一個對話塞不下時用它分批。
- **預算控制**：依 token 預算動態決定要派幾個 agent。

---

## 3. 何時**不要**用（替代方案對照）

| 你的需求 | 別用 Dynamic Workflow，改用 | 為什麼 |
|---------|---------------------------|--------|
| 一句話重複指令（高頻） | **Skill**（`/skill-name`） | 輕量、零編排成本 |
| 同一任務定期跑 / 持續監控 | **/loop**（本機間隔）或 **/schedule**（雲端 cron） | 單任務排程，不需多代理 |
| 單一複雜任務、要乾淨上下文 | **單一 Subagent**（Agent 工具） | 一次性、不需迴圈/扇出 |
| 只要「同時做 3 件不相干的事」 | **一則訊息內多個 Agent 呼叫** | 一次性扇出就夠，不需腳本 |
| 任務微小（改個變數） | **直接做** | 殺雞用牛刀 |

> 反模式：用 Dynamic Workflow 做「單一檔案 bug fix」= 用牛刀殺雞；用單一 subagent 做「50 檔案 × 兩階段審查」= 用鑷子蓋房子。

---

## 4. 怎麼用（HOW）—— 腳本骨架

每支腳本一定以 `export const meta = {...}`（**純字面值**，不可用變數）開頭，接著是 body：

```javascript
export const meta = {
  name: 'my-workflow',
  description: '一句話說明',
  phases: [{ title: 'Find' }, { title: 'Verify' }],   // 對應進度顯示分組
}

phase('Find')                                  // 開一個階段
const found = await agent('找出 X', { schema: MY_SCHEMA })   // 派一個 agent；給 schema 會回驗證過的物件
phase('Verify')
const checked = await parallel(                 // 平行跑（有同步牆，全部回來才往下）
  found.items.map(it => () => agent(`驗證：${it}`, { schema: VERDICT }))
)
return checked.filter(Boolean)
```

**三個核心原語：**

| 原語 | 作用 | 重點 |
|------|------|------|
| `agent(prompt, opts)` | 派一個 subagent | 給 `schema`（JSON Schema）→ 回**驗證過的物件**，不必自己 parse |
| `parallel(thunks)` | 同時跑一批，**等全部**回來 | 是同步牆；失敗的那個變 `null`（記得 `.filter(Boolean)`） |
| `pipeline(items, s1, s2…)` | 每個 item 獨立走完所有階段 | **沒有階段間等待牆**，預設首選；A 可在第 3 階段時 B 還在第 1 階段 |

---

## 5. 本練習的 Hello 範例

檔案：本資料夾的 [`hello-dynamic-workflow.md`](./hello-dynamic-workflow.md)（腳本＋逐步說明）。

它做的事（最小但完整地示範扇出＋結構化輸出＋彙整）：

```
Phase 1「Generate」：對 3 個主題（Skills / Subagents / Dynamic Workflows）
                     各平行派一個 agent，出一題測驗（結構化：題目/答案/難度）
Phase 2「Assemble」：再派一個 agent，把 3 題彙整成一張 markdown 測驗卷
```

學完你會看懂：`meta` 怎麼宣告、`phase()` 怎麼分組、`parallel()` 怎麼扇出、`schema` 怎麼強制結構化、最後怎麼 `return` 彙整結果。

---

## 6. 練習步驟（跟著做）

1. **讀** [`hello-dynamic-workflow.md`](./hello-dynamic-workflow.md) 的腳本，對照第 4 節的三原語，標出哪行是扇出、哪行是 schema、哪行是彙整。
2. **預測**：跑下去會派幾個 agent？（答案：3 個出題 + 1 個彙整 = 4 個）
3. **跑一次**：跟 Claude 說「用 hello-dynamic-workflow 腳本跑一次 workflow」。Claude 會用 `Workflow` 工具執行，你可在 `/workflows` 看即時進度樹。
4. **改一個變數**：把主題改成你想複習的 3 個概念，再跑一次，比較產出。
5. **填** [`STEP_LOG.md`](./STEP_LOG.md)：記下你的預測 vs. 實際、踩到什麼、何時你會選它而不是單一 subagent。

---

## 7. 一頁速記（背這個就夠）

- **是什麼**：Claude 跑的 JS 多代理編排（`Workflow` 工具），不是 `/slash`。
- **何時用**：很多項目 × 多階段 × 要程式化控制（迴圈/扇出/交叉驗證/超大規模）。
- **何時不用**：單一任務→subagent；定期單任務→/loop、/schedule；高頻指令→skill；只要一次性同時做幾件→多個 Agent 呼叫。
- **三原語**：`agent()` 派人、`parallel()` 同時跑等齊、`pipeline()` 各自跑到底（預設首選）。
- **怎麼啟動**：請 Claude 做「需要多代理編排」的事，或明確說「用 workflow 跑」。
