# 練習 01 — 基礎：為模組規劃測試金字塔

## 情境說明
大型 codebase 靠測試金字塔分配精力：大量單元、適量整合、少量端對端。

## 範例：金字塔與比例
```text
        /  E2E  \        少量（關鍵流程，慢但真實）
       / 整合測試 \      中量（API + DB 互動）
      /  單元測試  \     大量（純函式、驗證邏輯，快）
```
```bash
pytest tests/unit -q             # 快、常跑
pytest tests/integration -q      # 較慢、PR 時跑
pytest --cov=mypkg --cov-report=term-missing   # 看覆蓋缺口
```

## 任務
### 任務 1
為一個中型模組畫出它該有的測試金字塔（各層放什麼）。

### 任務 2
用 coverage 報告指出目前覆蓋的缺口（哪些分支沒測到）。

## 驗收標準
- [ ] 三層各有具體測試項目
- [ ] 指出至少 2 個覆蓋缺口

## 完成後
將解答存入 `answer/ex01-answer.md`。
