# 練習 01 解答：為 `bookshelf` 模組規劃測試金字塔

## 受測模組

自建的中型模組 `bookshelf/`（書籍借閱管理，sqlite3 標準庫，約 180 個敘述）：

| 檔案 | 職責 | 適合的測試層 |
| --- | --- | --- |
| `rules.py` | ISBN-10/13 檢查碼、日期解析、逾期罰金（純函式） | 單元 |
| `db.py` | sqlite3 schema 與 CRUD（參數化查詢） | 整合 |
| `service.py` | `Library`：借書、還書、報表（商業規則） | 整合（+ 拆出的純函式做單元） |
| `cli.py` | argparse 指令列入口 `python -m bookshelf.cli` | 端對端（E2E） |

## 任務 1：測試金字塔

```text
              /  E2E (1)  \          tests/e2e/         子程序真的跑 CLI，約 0.7 秒
             / 整合 (13)    \        tests/integration/ Library + 真實 sqlite（記憶體 / 暫存檔）
            /  單元 (19)      \      tests/unit/        純函式，0.04 秒跑完
```

（數字是練習 02 做完後的最終測試數，共 33 個。）

### 單元層（大量、快、常跑）——`tests/unit/`

- `is_valid_isbn`：合法 ISBN-13、ISBN-10、帶連字號；檢查碼錯誤、長度錯誤、空字串、含字母
- ISBN-10 結尾 `X`，以及 `X` 出現在中間（非法）
- `normalize_isbn`：去掉空白和連字號；傳入 `None` 時丟 `ValidationError`
- `parse_date`：正確格式，以及 `2026/10/18` 這類錯誤格式
- `calc_fine`：準時是 0、逾期 3 天是 15、**逾期很久時封頂 200**
- （練習 02 重構後新增）`summarize_loans`、`format_entry`：用 dict 假資料，不需要 DB

### 整合層（中量、PR 時跑）——`tests/integration/`

- 新增書籍後依書名排序列出
- 不合法的 ISBN 被拒絕
- 借書的到期日是 14 天後
- 同一本書不能被借出兩次
- 逾期歸還時，罰金寫回 DB 的 `loans.fine`
- 資料寫進暫存檔後重新連線仍然在（持久化）
- 錯誤路徑：空書名、重複新增、借不存在的書、沒借就還
- `report()` 的 characterization test（練習 02）

### E2E 層（少量、最真實）——`tests/e2e/`

- 用 `subprocess` 執行完整流程 `add → borrow → return → list`，檢查 stdout 有到期日、「罰金 25 元」、書名

### 實際執行

```bash
pytest tests/unit -q          # 13 passed in 0.04s（baseline）
pytest tests/integration -q   # 6 passed in 0.07s
pytest tests/e2e -q           # 1 passed in 0.69s   ← 一個 E2E 就比全部單元測試慢 17 倍
pytest --cov=bookshelf --cov-report=term-missing
```

設定在 `pyproject.toml`：`branch = true` 開分支覆蓋；`patch = ["subprocess"]` 讓 E2E 子程序裡跑的 `cli.py` 也被算進覆蓋率（coverage 7.10 以上才有）。

## 任務 2：用 coverage 報告找缺口

### Baseline（`reports/coverage-01-baseline.txt`）

```text
Name                    Stmts   Miss Branch BrPart  Cover   Missing
bookshelf\cli.py           49      5     14      2    86%   49-50, 52-54, 59->exit
bookshelf\db.py            26      0      0      0   100%
bookshelf\rules.py         31      1     12      1    95%   24
bookshelf\service.py       58     26     22      4    50%   23, 25, 32, 43, 50-73
TOTAL                     165     32     48      7    76%
```

### 找到的缺口

| # | 位置 | 缺口 | 風險 |
| --- | --- | --- | --- |
| 1 | `service.py` 50-73 | `report()` **整個函式沒測過** | 報表格式和逾期判斷出錯也不會被發現 |
| 2 | `service.py` 23、25、32、43 | 四個錯誤路徑：空書名、重複新增、查無此書、沒借就還 | 只測了快樂路徑 |
| 3 | `rules.py` 24 | ISBN-10 含非法字元的 `return False` 分支 | 驗證可能放過壞資料 |
| 4 | `cli.py` 49-50、52-54 | `list` 指令、錯誤時印 stderr 並回傳 exit code 1 | CLI 錯誤處理沒保護 |
| 5 | **coverage 看不到** | `calc_fine` 的封頂 200 是用 `min()` 寫的，不是 `if` 分支，所以沒測也顯示 100% | 覆蓋率高不代表規格都驗證過 |

另外，只跑單元測試時總覆蓋率只有 30%（`rules.py` 95%，其他檔案幾乎都沒跑到）。這說明單元測試只保護純邏輯，DB 和 CLI 要靠上面兩層。

### 補測試後（`reports/coverage-02-after-gap-tests.txt`）

補了 2 個測試函式（參數化後共 7 個案例）和 1 個盲點測試：

- `test_isbn10_check_digit_x_and_bad_chars`（缺口 3）
- `test_service_error_paths`（缺口 2，4 種錯誤）
- `test_fine_capped_at_200`（缺口 5，靠讀規格補的，coverage 數字不會變）

```text
bookshelf\rules.py         31      0     12      0   100%   (95% → 100%)
bookshelf\service.py       58     22     22      0    60%   (50% → 60%)，剩 50-73
TOTAL                     165     27     48      2    81%   (76% → 81%)
```

缺口 1（`report()`）留到練習 02，用 characterization test 補上後 `service.py` 變成 100%，總覆蓋率 96%（`reports/coverage-03-after-refactor.txt`）。

缺口 4（CLI 的 `list` 和錯誤 exit code）沒寫自動測試，只在 NOTES 的 CLI 手動 demo 中驗證過（exit=1 有出現）。

### 補測試時踩到的坑

第一次寫的反例 `12345678-9X` 竟然是**合法的** ISBN-10（加權和 220 剛好被 11 整除），所以測試失敗。這表示失敗的可能是測試本身，不一定是程式。後來改用 `1234X67890`（X 在中間）。
