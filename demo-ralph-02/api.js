// 迷你 Todo API — Ralph 獨立版演練用空殼
// 一開始所有端點都未實作，api.test.js 會全部失敗（紅燈）。
// 規格見 api-spec.md；練習目標：用 Ralph 獨立版逐一實作到 npm test 全綠。
//
// 資料模型：
//   Todo  = { id: number, title: string, done: boolean }
//   Store = { todos: Todo[], nextId: number }   // 呼叫端建立並傳入，函式可直接修改
// 每個函式回傳 { status, body }。

export function createTodo(store, payload) {
  throw new Error("not implemented");
}

export function listTodos(store) {
  throw new Error("not implemented");
}

export function getTodo(store, id) {
  throw new Error("not implemented");
}

export function updateTodo(store, id, patch) {
  throw new Error("not implemented");
}

export function deleteTodo(store, id) {
  throw new Error("not implemented");
}
