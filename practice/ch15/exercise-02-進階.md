# 練習 02 — 進階：設計 permissions 策略

## 情境說明
好的權限策略＝高頻安全操作自動放行、危險操作必須確認，減少打斷又不失控。

## 範例：settings.json permissions
```json
{
  "permissions": {
    "allow": [
      "Bash(npm run test:*)",
      "Bash(git status)",
      "Read(./src/**)"
    ],
    "ask": [
      "Bash(git push:*)",
      "Bash(rm:*)"
    ]
  }
}
```

## 任務
### 任務 1
列出 5 條 allow / ask 規則（哪些自動允許、哪些必須確認）。

### 任務 2
為每條說明風險權衡（為何放行 / 為何要攔）。

## 延伸思考
prompt cache 如何影響成本？哪些操作會打破 cache（讓下次重算更貴）？

## 完成後
將解答存入 `answer/ex02-answer.md`。
