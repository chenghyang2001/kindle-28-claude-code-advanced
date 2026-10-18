# 刻意埋的問題（commit 前先記錄，用來比對外掛命中率）

| # | 位置 | 問題 | 類型 |
|---|------|------|------|
| P1 | apply_discount `coupons=[]` | 可變預設參數 + 函式內 append → 優惠券跨呼叫累積，第二筆起被重複扣 | Bug（必改） |
| P2 | `if total > BULK_THRESHOLD` | 註解/docstring 說「滿 1000（含）」，實作用 `>`，剛好 1000 不打折 | Bug（必改） |
| P3 | summarize 的 bare `except: pass` | 吞掉所有例外（含 KeyboardInterrupt），錯誤無紀錄 → silent failure | 風險（必改） |
| P4 | `revenue / (len(orders) - failed)` | 全失敗或空清單 → ZeroDivisionError | Bug（必改） |
| P5 | `== True`、`else: total = total`、`failed = failed + 1; pass`、is_vip 的 if/else return | 冗餘寫法 | 簡化（simplify） |
| P6 | 測試 `test_summarize_runs` 沒驗 revenue/average；無邊界測試 | 測試覆蓋不足 | 建議 |
