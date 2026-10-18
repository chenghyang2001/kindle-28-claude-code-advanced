# 練習 01 — 基礎：把長型專案拆成 GSD 階段

## 情境說明
GSD（Get Shit Done）用明確 phases + 階段間 gate 來駕馭會跑很久的專案，比扁平 todo list 更能控管風險。

## 範例：phases 與 gate
```markdown
## Phase 0 — 合約/規格   gate: 規格經審查通過
## Phase 1 — 骨架        gate: 介面/型別定案、可編譯
## Phase 2 — 實作        gate: 單元測試綠
## Phase 3 — 整合/驗收   gate: 端對端通過 + 文件更新
```

## 任務
### 任務 1
挑一個會跑很久的專案（如重構一個模組），列出它的 phases 與每階段產出。

### 任務 2
為每個階段定義明確的 gate 條件（什麼成立才能進下一階段）。

## 驗收標準
- [ ] 至少 3 個階段，每階段有可驗收產出
- [ ] 每個 gate 是客觀可判定的（非「感覺差不多」）

## 完成後
將解答存入 `answer/ex01-answer.md`。
