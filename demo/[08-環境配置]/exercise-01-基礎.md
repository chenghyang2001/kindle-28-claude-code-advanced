# 練習 01 — 基礎：盤點並優化你的環境

## 情境說明
理想環境＝省下的每一個重複動作。先盤點 terminal / alias / CLI flag 的可優化點。

## 範例：常用 CLI flags 與設定位置
```bash
claude --model claude-opus-4-8       # 指定模型
claude -p "一次性任務"                # 非互動、印完即走（適合腳本）
claude --resume                       # 接續上一個 session
```
```text
設定檔層級：
~/.claude/settings.json        # 全域
<repo>/.claude/settings.json   # 專案（進版控、團隊共用）
<repo>/.claude/settings.local.json  # 個人覆寫（不進版控）
```

## 任務
### 任務 1
列出你目前環境 5 個可立即優化的設定（terminal、alias、CLI flag、model 預設）。

### 任務 2
實際套用其中至少 2 個並驗證生效。

## 驗收標準
- [ ] 5 個優化點具體可執行
- [ ] 至少 2 個已套用並驗證

## 完成後
將解答存入 `answer/ex01-answer.md`。
