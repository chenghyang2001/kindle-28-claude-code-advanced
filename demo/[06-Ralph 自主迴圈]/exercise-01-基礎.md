# 練習 01 — 基礎：看懂 Ralph 自主迴圈

## 情境說明
Ralph 讓 Claude 在無人監督下持續「產出 → 驗證 → 再產出」直到收斂。核心是明確的終止條件與護欄。

## 範例：最小自主迴圈骨架（bash + claude -p）
```bash
#!/bin/bash
set -euo pipefail
MAX=10                      # 迭代上限（backstop，防失控）
for i in $(seq 1 "$MAX"); do
  claude -p "讀 TASK.md，做下一個未完成項目，完成後在該項打勾。"
  if ! grep -q '\[ \]' TASK.md; then   # 收斂條件：沒有未完成項
    echo "全部完成於第 $i 輪"; break
  fi
done
```

## 任務
### 任務 1
畫出這個迴圈的狀態流（產出 → 驗證 → 判斷收斂 → 繼續/停止）。

### 任務 2
標出迴圈的終止條件與「逃生」條件（什麼情況立刻停）。

## 驗收標準
- [ ] 狀態流清楚標出收斂判斷點
- [ ] 至少 2 個停止條件（收斂 + backstop 上限）

## 完成後
將解答存入 `answer/ex01-answer.md`。
