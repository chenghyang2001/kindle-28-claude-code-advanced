我讀過 `cfgcli/cli.py`、`cfgcli/store.py` 和兩個測試檔，計畫如下。專案檔案都沒動，計畫另存在 `~/.claude/plans/cli-import-frolicking-peach.md`。

## `cfgcli import <file>` 實作計畫

**行為**：讀入一個 JSON 檔，做淺層合併。檔案裡有的 key 會覆寫目前的值，檔案裡沒有的 key 維持原樣。

### 要改的檔案
| 檔案 | 動作 |
|---|---|
| `cfgcli/cli.py` | 新增 3 個函式，在 `build_parser()` 註冊 `import`，更新開頭的模組說明 |
| `tests/test_import.py` | 新檔，沿用 `test_export.py` 的 `isolated_home` 寫法 |
| `cfgcli/store.py` | 不改，直接用現有的 `load_config()` / `save_config()` |

### 新增函式（都放在 `cfgcli/cli.py`）
1. **`parse_import(text) -> dict`**：解析 JSON，並檢查三件事：
   - JSON 格式正確
   - 最外層是物件（`{...}`）
   - 每個值都是字串（`set` 只會存字串，export 出去再匯回來型別也一致）
   
   不符合就拋 `ValueError`，並指出是哪個 key 出錯。
2. **`merge_config(current, incoming) -> (合併結果, 新增的 keys, 覆寫的 keys)`**：不改動傳入的 dict，方便單獨測試。
3. **`cmd_import(args)`**：
   - 讀檔用 `utf-8-sig`，Windows 記事本存出來的 BOM 也能讀。
   - 先完整驗證匯入檔，再讀目前設定、合併、寫回。驗證失敗時不會寫入半套設定。
   - 成功時印出 `已匯入 N 筆（新增 X、覆寫 Y）`。

### 退出碼（照現有慣例）
| 情境 | 退出碼 |
|---|---|
| 成功，包含匯入空物件 `{}` | 0 |
| 檔案不存在或讀不到 | 1（和 export 寫檔失敗一樣） |
| JSON 壞掉、最外層不是物件、值不是字串、目前的設定檔本身損壞 | 2（交給 `main()` 統一處理） |

### 測試案例（`tests/test_import.py`）
- **正常**：原本有 `theme`、`lang`，匯入 `{"theme":"light","font":"mono"}`。結果應是 `theme` 被覆寫、`lang` 保留、`font` 新增，訊息顯示「新增 1、覆寫 1」。
- **邊界**：匯入 `{}`，回 0，設定不變。
- **邊界**：中文 key 和值，加上帶 BOM 的檔案，都能正確匯入。
- **整合**：`export -o x.json`，清空設定，再 `import x.json`，設定要和原本一模一樣。
- **錯誤**：
  - 檔案不存在 → 回 1
  - 內容是 `{not json` → 回 2，原本的設定不被改動
  - 最外層是陣列 → 回 2
  - 值是巢狀物件或數字 → 回 2，訊息指出是哪個 key

### 驗證方式
用 `PYTHONUTF8=1 python -m pytest -q` 跑新舊全部測試，再手動跑一次 `python -m cfgcli.cli import sample.json` 冒煙測試。

### 你可能想改的設計
- **值不是字串時直接報錯**：如果你希望 `{"port": 8080}` 這種數字也能匯入，我可以改成自動轉成字串。代價是布林值會變成 `"True"`，和 JSON 的 `true` 寫法不一樣。

這個資料夾是 k28-ch03-practice 練習，你說 ok 之後，我會先問你要用快速 demo 模式（只寫檔，跑一次冒煙測試），還是完整模式（照 writer → QA → reviewer 三個 agent 依序跑）。
