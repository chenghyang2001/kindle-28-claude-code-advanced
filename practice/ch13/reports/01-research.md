# 研究 agent 交付物：相依地圖 + 風險清單
（由主 agent 原文存檔；研究 agent 本身未寫任何檔）

## 1. 相依地圖
- 類別：兩個方法都掛在 `TodoStore` 上，只讀 `self.items`（list of dict），不改資料，不呼叫 `save()`。
- 欄位：`done`（bool）、`priority`（int，預設 3）、`due`（`"YYYY-MM-DD"` 或 None）、`id`（同分時的次序依據）。
- 資料來源：`add()` 原樣存入 `due`，沒有驗證格式；JSON 的 `null` 載入後是 None。
- 測試匯入：沿用 `sys.path.insert(... / "src")` 加 `from todo import TodoStore`，用 `tmp_path` 建 store。
- 樣本資料（today=2026-10-18）：逾期只有 id1；id4 的 due 等於今天，不算逾期；id3 已完成。
- 需新增 `from datetime import date`。

## 2. 風險清單
1. 高｜due 格式不合法 → 用 `date.fromisoformat()` 解析，不合法時拋 ValueError 並附上 id。
2. 高｜字串和 date 直接比較會 TypeError → 一律先轉成 date。
3. 中｜None 參與排序會 TypeError → tuple 排序鍵 `(done, priority, due is None, due_date or date.max, id)`。
4. 中｜邊界 → 用嚴格的 `<`，到期日當天不算逾期；done 的項目排除。
5. 中｜today 型別 → 非 date 拋 TypeError，datetime 轉成 `.date()`；方法內不呼叫 `date.today()`。
6. 低｜id 用 `len+1` 產生，支援刪除後會重複 → 另外回報，本任務不修。
7. 低｜sorted_items 要回傳新 list，不可改 `self.items`。

## 3. 測試案例
- Happy：樣本資料測 overdue 只回 id1；sorted_items 順序應為 4、1、2、3。
- Edge：空清單、due 等於今天、due 為 None、全部已完成、同分依 id 排、不改動原清單。
- Error：due 不合法拋 ValueError；today 傳字串拋 TypeError。

研究 agent：未修改任何檔案（主 agent 以 `git status --porcelain` 驗證：追蹤檔無變更）
