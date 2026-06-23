---
name: quiz-workflow
description: 用 Dynamic Workflow（多代理編排）一鍵生成「Claude Code 觀念測驗卷」。對 N 個主題各平行出一題、再彙整成 markdown 測驗卷。當使用者說「出測驗」「出題」「隨堂測驗」「quiz workflow」「考我 Claude Code」「生成測驗卷」「用 workflow 出題」時觸發。可帶逗號分隔的主題當參數（如 `quiz-workflow Hooks, MCP, Plugins`）；沒給就用預設 3 個主題。不觸發：Socratic 口試（用 grill-me）、單純問答、非測驗的內容生成。
---

# quiz-workflow — 把出題 workflow 包成 skill

把 `demo-dynamic-workflow/hello-dynamic-workflow.md` 的多代理出題流程固化成「一句話重跑」的 skill。

## 這個 skill 怎麼運作（重要）

skill **不會自己跑 JS**。被觸發時，**主 Claude 去呼叫 `Workflow` 工具**，餵下面這段腳本（把 `TOPICS` 換成使用者的主題）。所以這支 skill = 「Workflow 啟動器 + 參數處理」。

## 執行步驟（主 Claude 照做）

1. **解析主題**：從使用者參數取逗號分隔的主題清單。
   - 有參數 → 用它（如 `Hooks, MCP Servers, Plugins`）。
   - 沒參數 → 用預設：`['Skills', 'Subagents', 'Hooks']`。
2. **呼叫 `Workflow` 工具**，`script` 用下面這段（把 `__TOPICS__` 替換成步驟 1 的 JS 陣列字面值）。
3. **回報**：把 workflow 回傳的測驗卷貼給使用者；若在互動教學模式，依專案規則用 `say_ui` 語音播報。

## Workflow 腳本（餵給 Workflow 工具的 `script`）

```javascript
export const meta = {
  name: 'quiz-workflow',
  description: '對 N 個主題各平行出一題測驗，再彙整成測驗卷',
  phases: [
    { title: 'Generate', detail: '每主題平行出一題' },
    { title: 'Assemble', detail: '彙整成 markdown 測驗卷' },
  ],
}

// __TOPICS__ 由 skill 依使用者參數替換；下面是預設值
const TOPICS = ['Skills', 'Subagents', 'Hooks']

const QUIZ_SCHEMA = {
  type: 'object',
  properties: {
    question: { type: 'string' },
    answer: { type: 'string' },
    difficulty: { type: 'string', enum: ['easy', 'medium', 'hard'] },
  },
  required: ['question', 'answer', 'difficulty'],
}

phase('Generate')
const items = await parallel(
  TOPICS.map((topic) => () =>
    agent(
      `用繁體中文，針對 Claude Code 的「${topic}」概念，出一題「單一觀念」測驗題，附正解與難度（easy/medium/hard）。`,
      { label: `quiz:${topic}`, phase: 'Generate', schema: QUIZ_SCHEMA }
    ).then((q) => ({ topic, ...q }))
  )
)

phase('Assemble')
const valid = items.filter(Boolean)
const sheet = await agent(
  `把下面這些題目排成一張繁體中文 markdown 測驗卷：先依序列出所有「題目＋難度」，最後加一個「解答」區塊。\n\n${JSON.stringify(valid, null, 2)}`,
  { label: 'assemble', phase: 'Assemble' }
)

log(`完成：${valid.length} 題`)
return sheet
```

## 使用範例

| 使用者輸入 | 行為 |
|-----------|------|
| `出測驗` | 用預設 3 主題（Skills/Subagents/Hooks）|
| `quiz-workflow Hooks, MCP Servers, Plugins` | 對這 3 個主題出題 |
| `考我 Claude Code 的 Slash Commands、Output Styles` | 對這 2 個主題出題 |

## 成本提醒

每個主題 1 個 agent + 1 個彙整 agent。N 主題 ≈ (N+1) 個 agent。主題越多 token 越貴；預設 3 個約 4 個 agent。
