# API 規格：迷你 Todo API（5 端點）

這份規格模擬第八題「收到 api-spec.md，實作多個端點 + 測試」的獨立版場景。
為了在 WSL 裡好跑，端點用**純函式**實作（不起真的 HTTP server），由 `api.test.js` 驗收。

## 資料模型

```
Todo  = { id: number, title: string, done: boolean }
Store = { todos: Todo[], nextId: number }   // 由呼叫端建立並傳入；函式可直接修改傳入的 store
```

每個端點函式都回傳 `{ status, body }`。

## 端點（實作於 api.js）

| # | 函式簽名 | 行為 | 成功狀態 | 錯誤情況 |
|---|---|---|---|---|
| 1 | `createTodo(store, { title })` | 用 `store.nextId` 當 id 建立 `{ id, title, done:false }`，推入 `store.todos`，`store.nextId++` | `201`，body = 新 todo | `title` 為空字串或缺漏 → `400`，body = `{ error: 'title required' }` |
| 2 | `listTodos(store)` | 回傳所有 todos | `200`，body = `store.todos` 陣列 | — |
| 3 | `getTodo(store, id)` | 依 id 找 todo | `200`，body = 該 todo | 找不到 → `404`，body = `{ error: 'not found' }` |
| 4 | `updateTodo(store, id, patch)` | 把 `patch` 的欄位（title / done）合併進該 todo | `200`，body = 更新後 todo | 找不到 → `404`，body = `{ error: 'not found' }` |
| 5 | `deleteTodo(store, id)` | 從 `store.todos` 移除該 todo | `200`，body = `{ deleted: true }` | 找不到 → `404`，body = `{ error: 'not found' }` |

## 驗收

`npm test`（vitest）全綠即完成。`api.test.js` 已預先寫好，初始為紅燈。
