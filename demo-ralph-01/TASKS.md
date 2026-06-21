# Ralph 練習任務清單：網頁小計算機

目標：實作 `calc.js` 裡的 5 個純函式，讓 `calc.test.js` 全部通過（綠燈）。

迴圈規則（給 Ralph Loop 用）：

- 一個任務一個任務做，**每完成一個就跑 `npm test`**
- 綠燈 → 換下一個任務；紅燈 → 照錯誤訊息修
- 全部測試通過時輸出 `<promise>DONE</promise>`

## 任務

- [ ] 任務 1：`add(a, b)` — 回傳 `a + b`
- [ ] 任務 2：`subtract(a, b)` — 回傳 `a - b`
- [ ] 任務 3：`multiply(a, b)` — 回傳 `a * b`
- [ ] 任務 4：`divide(a, b)` — 回傳 `a / b`；當 `b === 0` 時 `throw new Error('Cannot divide by zero')`
- [ ] 任務 5：`percent(a, b)` — 回傳 a 的 b%（即 `a * b / 100`）

## 啟動指令（裝好 ralph-wiggum 外掛後，在本資料夾的 Claude Code 執行）

```text
/ralph-loop "讀 TASKS.md，逐一把函式實作到 calc.js，每寫完一個就跑 npm test，綠燈換下一個、紅燈照錯誤訊息修。全部測試通過時輸出 <promise>DONE</promise>。" --completion-promise "DONE" --max-iterations 10
```
