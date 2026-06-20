# 練習 03 — 綜合挑戰：打造完整環境配置

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
為自己組一套完整配置：terminal + alias + 1 個 hook + 1 個 MCP + model 預設，全部可攜（跨機器）。

## 範例：接 MCP server
```bash
# 加一個 MCP server（之後可在 session 內呼叫其工具）
claude mcp add --transport stdio my-server -- python /path/to/server.py
claude mcp list
```

## 限制條件
- 所有路徑不可硬編碼（用 `~` / `$HOME` / `%USERPROFILE%`）
- 需附每項設定的「為什麼」（解決什麼痛點）

## 完成後
將解答存入 `answer/ex03-answer.md`。
