# 練習 03 — 綜合挑戰：完整編排一個較大任務

> 選配：完成前兩個練習後再挑戰

## 挑戰情境
為一個較大任務設計完整編排：phases + agent 分工 + 信號檔 + 最終整合。

## 範例：信號檔推進
```text
contracts/api-spec.yaml      # Phase 0 產出的合約（含 Never modifies 條款）
signals/BUILD_COMPLETE.md    # Builder 完成 -> 主 agent 推進到審查
signals/REVIEW_COMPLETE.md   # Reviewer 完成 -> 主 agent 整合
MANIFEST.md                  # 最終整合
```

## 限制條件
- 需有指揮者 / 工人職責分離（指揮者不下場實作）
- 需有越權偵測（例如 Reviewer 改了 src/）與脈絡漂移處置

## 完成後
將解答存入 `answer/ex03-answer.md`。
