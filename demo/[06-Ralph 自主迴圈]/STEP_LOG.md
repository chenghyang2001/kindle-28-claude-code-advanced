# STEP_LOG — [06] Ralph 自主迴圈

> 記錄本課的學習過程、卡關與突破。完成後重要踩坑彙整到 `docs/踩坑紀錄.md`。

## 學習日期
- 2026-06-20

## 我做了什麼
1. 基礎：畫出自主迴圈狀態流（產出→驗證→判斷收斂→繼續/停止），標出 2 正常出口 + 4 逃生條件（`answer/ex01-answer.md`）。
2. 進階：用 YouTube 夜間爬蟲為例定義每輪 I/O（冪等狀態檔），列 5 護欄各擋一種失敗（`answer/ex02-answer.md`）。
3. 綜合（真寫腳本）：實作可跑的 `skills/ralph_loop.sh`（TASK.md 驅動 + 5 護欄 + dry-run），走 writer→qa→reviewer 鐵律。規格見 `answer/ex03-answer.md`。

## 卡關與解法
- 卡關：reviewer 抓到「零進展護欄用整檔雜湊」有破口。
  - 根本原因：claude 沒打勾卻亂動 TASK.md（重排版/自增子任務）→ bytes 變→雜湊變→護欄永不觸發→燒到 backstop。對「壞掉但會亂動檔案的 claude」形同虛設。
  - 解法：改用「未完成框數單調遞減」當客觀進度信號（remaining>=prev_remaining → exit 3），prev_remaining 迴圈外初始化抓第 1 輪空轉。新增 --dry-run-noop 測試鉤子驗 exit 3。
- 卡關：時間窗護欄預設 0（關閉）且沒包住 claude 呼叫。
  - 解法：MAX_SECONDS 預設改 1800、用 timeout 包住單通 claude（逾時當該輪失敗）。

## 關鍵收穫（3 句以內）
- 自主迴圈價值不在「會迴圈」，在「收斂條件 + 護欄」；護欄要擋真跑時的失控，不是 happy path。
- 進度信號要客觀（未完成框數遞減），不能拿「claude 自報的檔案狀態」當唯一真相。
- 三-agent 鐵律的審查 gate 真的有用：happy path 全綠，致命破口藏在非 dry-run 真跑模式，被 reviewer 揪出。

## 自評
- 基礎練習：✅ 完成
- 進階練習：✅ 完成
- 綜合挑戰：✅ 完成（真寫腳本 ralph_loop.sh + reviewer 抓破口後修正）
