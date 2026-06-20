# 練習 03 — 綜合挑戰：安全 + 成本檢查表

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
為一個會接觸 DB / API key / 使用者輸入的工作流，做一次安全 + 成本檢查表。

## 範例：用 Docker 隔離高風險執行
```dockerfile
FROM python:3.12-slim
RUN useradd -m runner            # 非 root 執行，縮小爆炸半徑
USER runner
WORKDIR /work
# 把不可信任務跑在容器內，限制其能碰到的東西
```

## 限制條件
- 檢查表需含機密管理（不硬編碼、進 .gitignore）與注入防禦（參數化查詢、輸入驗證）
- 需含 model 成本上限的護欄（避免失控燒錢）

## 完成後
將解答存入 `answer/ex03-answer.md`。
