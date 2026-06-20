# 練習 02 — 進階：用 .claude/ 做 pre-setup

## 情境說明
把專案慣例先寫進 `.claude/`，後續任務的計畫品質會明顯提升（一次到位率更高）。

## 範例：專案結構與設定
```text
專案根/
├── CLAUDE.md                 # 專案簡報：架構/執行方式/關鍵決策
└── .claude/
    ├── settings.json         # 專案級設定（權限、env、hooks）
    └── commands/
        └── test.md           # /test 自訂指令
```
```json
// .claude/settings.json（最小範例）
{
  "permissions": { "allow": ["Bash(npm run test:*)", "Bash(npm run lint)"] }
}
```

## 任務
### 任務 1
為一個真實專案列出 3 項最值得寫進 `.claude/` 或 CLAUDE.md 的脈絡（慣用指令、目錄說明、雷區）。

### 任務 2
建立這些 pre-setup 後，對同一個任務重跑一次計畫，比較「有/沒有 pre-setup」的計畫品質差異。

## 延伸思考
計畫模式在什麼任務上是浪費（殺雞用牛刀）？什麼任務上是必要？

## 完成後
將解答存入 `answer/ex02-answer.md`。
