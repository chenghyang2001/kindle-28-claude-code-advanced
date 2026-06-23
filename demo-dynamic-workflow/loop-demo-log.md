# /loop demo 記錄檔

> 60 秒間隔、跑 3 次自動停。每行 = 一次喚醒的觀測。

- 第 1 次 ─ 2026-06-23 09:44:31 ─ HEAD=df2135a
- 第 2 次 ─ 2026-06-23 09:47:11 ─ HEAD=df2135a
- 第 3 次 ─ 2026-06-23 09:49:21 ─ HEAD=df2135a
- ✅ 已達 3 次，loop 結束

---

## 這個 demo 教了什麼（/loop 重點）

- **是什麼**：在 session 內，讓任務「固定間隔自我喚醒、重複跑」。對應決策矩陣左上角（持續監控／定期單一任務）。
- **本 demo**：60 秒間隔、跑 3 次自動停（停止條件寫在 prompt 裡，否則會無限跑）。
- **self-paced vs fixed-interval**：本 demo 是「一串 one-shot 喚醒」（self-paced，受 60 秒下限）；`/loop 1m <prompt>` 則建「真正 recurring cron」，最長 7 天或手動 `CronDelete`。
- **查排程**：`CronList` / `CronDelete` 是 **Claude 內部工具**（叫我跑，不是 shell/斜線指令）；`/schedule` 才是你能打的斜線指令（管雲端 routine）。
- **何時改用別的**：只跑一次→直接做；無人值守/關機也要跑→`/schedule`（雲端）；很多項目多階段→Dynamic Workflow（右上角）。
