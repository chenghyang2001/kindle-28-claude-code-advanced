# 練習 02 — 進階：系統化除錯定位一個 bug

## 情境說明
別亂猜。用二分搜尋 + 假設-驗證，快速縮小 bug 範圍。

## 範例：工具與手法
```bash
git bisect start
git bisect bad                  # 目前壞的
git bisect good <舊的好 commit>  # 已知好的
# git 自動 checkout 中間點，你測 -> git bisect good/bad，反覆二分到兇手 commit
git bisect reset
```
假設-驗證：寫下假設 → 設計最小實驗 → 觀察 → 留下或推翻，逐步逼近根因。

## 任務
### 任務 1
用二分（git bisect 或手動對半關閉程式碼）定位一個 bug，記錄每步。

### 任務 2
寫出根因與修法（為什麼會壞、怎麼改、如何防再犯）。

## 延伸思考
哪些「理由化行為」（如「檔案太大」「測試太複雜」）會讓 AI 停工？如何在 prompt 中預防？

## 完成後
將解答存入 `answer/ex02-answer.md`。
