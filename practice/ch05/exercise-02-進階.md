# 練習 02 — 進階：在一個階段引入 multi-agent 分工

## 情境說明
某些階段可平行：例如「研究 / 實作 / 審查」由不同 agent 負責，主 agent 當架構師整合。

## 範例：分工與邊界
```text
指揮者（主）：產合約、派工、整合、處理衝突；不自己寫業務碼
├─ Researcher：只讀、產出 API/相依地圖（Never modifies src/）
├─ Builder   ：只在 src/ 實作，依合約
└─ Reviewer  ：只讀 + 出審查報告（Never modifies src/）
信號檔：DONE.md / BUILD_COMPLETE.md / REVIEW_COMPLETE.md 推進階段
```

## 任務
### 任務 1
為你選的階段畫出 agent 分工與資料流（誰讀誰寫、交付物是什麼）。

### 任務 2
明確寫出「如何避免 agent 之間越權/衝突」（邊界 + 信號檔 + Never modifies 條款）。

## 延伸思考
GSD 的階段化與單純 todo list 差在哪？何時值得用這套重量級流程、何時不值得？

## 完成後
將解答存入 `answer/ex02-answer.md`。
