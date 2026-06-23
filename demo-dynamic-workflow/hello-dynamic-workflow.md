# hello-dynamic-workflow 範例腳本

這是要餵給 Claude `Workflow` 工具的腳本。**你不用自己執行**——讀懂它，然後跟 Claude 說「用這支腳本跑一次 workflow」。

---

## 腳本

```javascript
export const meta = {
  name: 'hello-dynamic-workflow',
  description: '對 3 個 Claude Code 主題各生一題測驗，再彙整成一張測驗卷',
  phases: [
    { title: 'Generate', detail: '每個主題平行生一題' },
    { title: 'Assemble', detail: '彙整成 markdown 測驗卷' },
  ],
}

// 想複習的 3 個主題（練習時可自由替換）
const TOPICS = ['Skills', 'Subagents', 'Dynamic Workflows']

// 強制每個出題 agent 回「結構化物件」，不必自己 parse 文字
const QUIZ_SCHEMA = {
  type: 'object',
  properties: {
    question: { type: 'string' },
    answer: { type: 'string' },
    difficulty: { type: 'string', enum: ['easy', 'medium', 'hard'] },
  },
  required: ['question', 'answer', 'difficulty'],
}

// ── Phase 1：扇出（fan-out）──
// parallel() 同時派 3 個出題 agent，等 3 個都回來
phase('Generate')
const items = await parallel(
  TOPICS.map((topic) => () =>
    agent(
      `用繁體中文，針對 Claude Code 的「${topic}」概念，出一題「單一觀念」測驗題，附正解與難度（easy/medium/hard）。`,
      { label: `quiz:${topic}`, phase: 'Generate', schema: QUIZ_SCHEMA }
    ).then((q) => ({ topic, ...q }))   // 把 topic 併進結果方便後面用
  )
)

// ── Phase 2：彙整（synthesis）──
// 失敗的 agent 會是 null，先濾掉；再派一個 agent 把題目排版成測驗卷
phase('Assemble')
const valid = items.filter(Boolean)
const sheet = await agent(
  `把下面這些題目排成一張繁體中文 markdown 測驗卷：先依序列出所有「題目＋難度」，最後加一個「解答」區塊。\n\n${JSON.stringify(valid, null, 2)}`,
  { label: 'assemble', phase: 'Assemble' }
)

log(`完成：${valid.length} 題`)
return sheet
```

---

## 逐行對照（學習重點）

| 區塊 | 在教哪個概念 |
|------|------------|
| `export const meta` | 每支 workflow 必備的「純字面」宣告；`phases` 對應進度樹分組 |
| `QUIZ_SCHEMA` | **結構化輸出**：給了 schema，`agent()` 回的是驗證過的物件，不是要你 regex 的字串 |
| `parallel(TOPICS.map(... () => agent(...)))` | **扇出**：3 題同時生成；注意傳的是「**回傳 Promise 的函式**」陣列（thunk），不是直接呼叫 |
| `.then(q => ({ topic, ...q }))` | 把上下文（topic）併進結果，後面彙整才知道誰是誰 |
| `items.filter(Boolean)` | **防呆**：parallel 裡失敗的 agent 會變 `null`，一定要濾 |
| 第二個 `agent(...)`（無 schema） | **彙整**：無 schema → 回純文字；把多個結果收斂成一份產出 |
| `return sheet` | workflow 的最終回傳值（會交回給主 Claude 呈現給你） |

---

## 預期產出

一張 markdown 測驗卷，含 3 題（每個主題 1 題）＋題末解答區。
過程中你會在 `/workflows` 看到：`Generate` 階段 3 個 `quiz:*` 並排跑 → `Assemble` 階段 1 個 `assemble`。

---

## 進階：把它升級成「右上角」的真本事

這個 hello 範例只示範「扇出 + 彙整」。Dynamic Workflow 真正的殺手級用法是再加一層**對抗式交叉驗證**，例如把第 2 階段換成：

```javascript
// 對每題派 2 個「審題者」檢查正解對不對，多數通過才留
pipeline(
  TOPICS,
  (topic) => agent(`出題：${topic}`, { schema: QUIZ_SCHEMA, phase: 'Generate' }),
  (quiz) => parallel([
    () => agent(`這題正解正確嗎？只回 true/false 與理由：${JSON.stringify(quiz)}`, { schema: VERDICT, phase: 'Verify' }),
    () => agent(`從另一角度再驗一次：${JSON.stringify(quiz)}`, { schema: VERDICT, phase: 'Verify' }),
  ])
)
```

`pipeline()` 的好處：題目 A 進到「驗證」時，題目 B 還能同時在「出題」——**沒有階段間等待牆**，這是它比「一批批 parallel」更快的關鍵。
