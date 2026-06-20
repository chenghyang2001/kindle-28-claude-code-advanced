# 練習 02 — 進階：把臃腫 CLAUDE.md 模組化

## 情境說明
CLAUDE.md 太長會稀釋重點。用 `@import` 把主題拆成獨立 instructions 檔，主檔只留引用。

## 範例：模組化
```markdown
# CLAUDE.md（主檔）
@instructions/code-quality.md
@instructions/dev-workflow.md
@instructions/tech-stack.md
```
```text
專案根/
├── CLAUDE.md
└── instructions/
    ├── code-quality.md
    ├── dev-workflow.md
    └── tech-stack.md
```

## 任務
### 任務 1
把一份臃腫 CLAUDE.md 至少 2 個主題抽成獨立 `@import` 檔。

### 任務 2
驗證主檔仍能完整載入（規則沒漏），並說明你怎麼確認的。

## 延伸思考
CLAUDE.md 與 memory（持久記憶）各自適合放什麼？界線在哪？

## 完成後
將解答存入 `answer/ex02-answer.md`。
