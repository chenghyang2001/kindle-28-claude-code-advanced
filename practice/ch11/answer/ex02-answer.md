# 練習 02 解答：一次安全重構——`Library.report()`

## 重構對象

重構前的 `bookshelf/service.py` `Library.report()`（commit `7c8bebb`）：一個 25 行的函式同時做這些事：

- 查 DB
- 分類（借出、逾期、已還）
- 統計三個計數器
- **自己再算一次罰金**（寫死 `* 5` 和 `> 200`，和 `rules.calc_fine` 重複）
- 用 `+` 串接字串排版

問題：罰金規則有兩份，改一份就會不一致；計算和排版混在一起，必須建 DB 才能測。

## 任務 1：重構步驟與每步驗證（實際執行的 git 紀錄）

| 步驟 | commit | 改了什麼（每次只處理一件事） | 驗證 |
| --- | --- | --- | --- |
| 0 | `7c8bebb` | 先寫 characterization test，**不動程式** | 31 passed；做突變檢查（見下方） |
| 1 | `5151cb8` | 逾期罰金改呼叫 `calc_fine(d, today)`，刪掉寫死的 5 和 200 | 31 passed |
| 2 | `2728113` | 抽出純函式 `summarize_loans(rows, today) -> Summary`（含 `Entry`、`Summary` dataclass），`report()` 只負責排版 | 31 passed |
| 3 | `0277ea8` | 抽出 `format_entry(e)`，改用 f-string；`report()` 縮成 4 行；為兩個新純函式補單元測試 | 33 passed |

每一步都是「改程式 → `pytest -q` 全綠 → `git commit`」。任何一步失敗都能 `git revert` 到上一個綠燈點，不用一次重來。

重構後的 `report()`：

```python
def report(self, today: date) -> str:
    s = summarize_loans(db.all_loans(self.conn), today)
    header = f"=== 借閱報表 {today.isoformat()} ==="
    footer = f"借出中：{s.out}，逾期：{s.late}，已收罰金：{s.collected}"
    return "\n".join([header, *map(format_entry, s.entries), footer])
```

## 任務 2：測試如何當安全網

### 1. Characterization test（`tests/integration/test_report_characterization.py`）

- **golden master**：設計一個情境，涵蓋 `report()` 的每條分支：
  - 未逾期
  - 逾期 4 天（罰 20）
  - 逾期很久（封頂 200）
  - 已還但有罰金
  - 準時歸還（不應出現在報表上）

  再把當下的實際輸出**逐字**寫成 `EXPECTED`。這個測試不判斷輸出合不合理，只保證輸出不變。
- **空資料庫**：只印表頭和 `0, 0, 0` 統計
- **邊界**：到期日當天不算逾期（原程式用 `today > due`）

寫完後 `service.py` 的覆蓋率從 60% 變成 100%，也就是 `report()` 的每一行、每條分支都被釘住了。

### 2. 突變檢查：確認安全網真的有效

故意把封頂 200 改成 199，再跑 characterization test：

```text
FAILED tests/integration/test_report_characterization.py::test_report_golden_master
1 failed, 2 passed
```

測試有抓到改動。之後 `git checkout` 還原，回到 31 passed。只有綠燈不代表測試有用，要看到它在該失敗時真的會失敗。

### 3. 其他層的保護

- 既有整合測試（借書、還書、罰金寫回 DB）保護 `report()` 讀到的資料
- 單元測試 `test_fine_capped_at_200` 保護步驟 1 換用的 `calc_fine`
- E2E 測試保護 CLI 對外的行為

### 對照結果：對外輸出不變

- 同一份 `EXPECTED` 字串在重構前後都通過
- 最終 33 passed，`service.py` 100%，總覆蓋率 96%
- CLI 手動 demo 的報表格式和重構前一致

## 延伸思考：大規模 migration 為什麼要分批？

一次改到底的風險：

1. **出錯時很難定位**：一個大 diff 裡同時改了 50 個地方，測試紅了也不知道是哪一處造成的。小步走時，失敗一定出在最後那一小步。
2. **無法部分回滾**：只能全部撤回，連改對的部分也一起丟掉。每步一個 commit，就能只 revert 出問題的那步。
3. **安全網會失效**：大改通常連測試一起改，「行為不變」就沒有東西能證明了。本練習刻意在重構期間完全不動 characterization test。
4. **合併衝突與凍結期**：長時間的大分支會和主線越差越遠。分批的話，每批都能合併、上線、觀察。
5. **審查品質下降**：沒有人能認真看完 3000 行的 diff，分批後每次只要看一個關注點。
6. **正式環境風險集中**：DB schema 或資料 migration 一次全切，壞了會影響全部使用者。分批（例如雙寫 → 回填 → 切換讀取 → 移除舊欄位，搭配 feature flag 或灰度發布）可以把影響範圍控制在一小部分。

本練習就是一個縮小版：3 個小步驟、3 個綠燈 commit。每一步的 diff 都能一眼看完，任何一步都能單獨回滾。
