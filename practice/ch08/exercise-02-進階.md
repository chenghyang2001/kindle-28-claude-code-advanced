# 練習 02 — 進階：寫一個 hook 自動化重複動作

## 情境說明
hooks 由 harness 在特定時機執行（不是 Claude 自己跑），可把「每次都要做的事」自動化。

## 範例：settings.json 的 hooks 區塊
```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command",
          "command": "python ~/.claude/hooks/check_auth.py" } ] }
    ],
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [ { "type": "command",
          "command": "python ~/.claude/hooks/guard.py" } ] }
    ]
  }
}
```
逃生門：在 hook 腳本支援一個 kill switch 環境變數（如 `DISABLE_HOOK=1`）。

## 任務
### 任務 1
選一個重複動作，定義 hook 的觸發時機（SessionStart / PreToolUse / Stop…）與行為。

### 任務 2
實作並測試它確實在預期時機觸發（故意觸發一次看 log）。

## 延伸思考
hooks 帶來自動化也帶來除錯難度。如何設計「可關閉 / 可逃生」的 hook？

## 完成後
將解答存入 `answer/ex02-answer.md`。
