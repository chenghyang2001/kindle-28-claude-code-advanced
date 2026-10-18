# 計畫：新增 `import` 子指令

## Context

cfgcli 目前有 set / get / list / export。需要反向操作：從外部 JSON 檔讀入設定，**合併**進目前設定（`export -o x.json` → `import x.json` 可來回）。

## 行為規格

- 指令：`cfgcli import <file>`
- 合併規則：`config.update(imported)` —— 同名 key 由匯入檔覆蓋，其他既有 key 保留。
- 成功輸出（stdout）：`已匯入 N 筆設定（新增 a 筆、覆蓋 b 筆）`，回傳 0。
- 驗證先做完才寫檔：任何錯誤都不會留下半套結果。

| 情況 | 回傳碼 | stderr |
| --- | --- | --- |
| 檔案不存在 / 無法讀取（OSError） | 1 | `錯誤：無法讀取 <file>（…）` |
| 匯入檔不是合法 JSON / 不是 UTF-8 | 1 | `錯誤：<file> 不是合法的 JSON（…）` |
| 頂層不是物件（例如陣列） | 1 | `錯誤：<file> 頂層必須是 JSON 物件` |
| 值是巢狀 dict / list | 1 | `錯誤：<key> 的值必須是純量` |
| 寫回設定檔失敗（OSError） | 1 | `錯誤：無法寫入設定檔（…）` |
| **目前設定檔**損壞 | 2 | 沿用 `load_config` 的 `ValueError` → `main()` 統一轉換 |

注意陷阱：`json.JSONDecodeError`、`UnicodeDecodeError` 都是 `ValueError` 子類，若不在 `cmd_import` 內攔下會被 `main()` 誤判成回傳 2（「設定檔損壞」）。匯入檔壞是使用者錯誤，必須回 1。

讀檔用 `encoding="utf-8-sig"`，相容 Windows 記事本存出的 BOM。

## 要改的檔案

### 1. `cfgcli/cli.py`（唯一的程式改動）

- 新增 `read_import_file(path: str) -> dict`：讀檔 → `json.loads` → 檢查頂層為 dict、值皆為純量（str/int/float/bool/None）；失敗時 raise 一個 cli 內部用的例外（或直接回傳錯誤訊息），由 `cmd_import` 印 stderr 並回 1。
  - 放在 cli.py 而非 store.py：store.py 依 CLAUDE.md 只負責「設定檔本身」讀寫，外部匯入檔的解析/驗證屬於指令層（同 `to_json` 放在 cli.py 的做法）。
- 新增 `cmd_import(args) -> int`：`read_import_file` → `load_config()`（重用 `cfgcli/store.py:14`）→ 計算新增/覆蓋數 → `config.update` → `save_config()`（重用 `cfgcli/store.py:24`，包 OSError → 1）→ 印摘要。
- `build_parser()` 註冊：`p_import = sub.add_parser("import", help="從 JSON 檔匯入並合併設定")`，位置參數 `file`。
- 更新模組 docstring：`set / get / list / export / import`。
- **不動** set / get / list / export 任何輸出格式。

### 2. `tests/test_import.py`（新檔，不改既有測試檔）

沿用 `tests/test_export.py` 的 `isolated_home` autouse fixture（`monkeypatch.setenv("CFGCLI_HOME", ...)`）。案例：

1. **happy**：既有 `theme=dark, lang=en`，匯入 `{"lang":"zh","size":"L"}` → 結果三個 key、`lang` 被覆蓋；stdout 含「新增 1 筆、覆蓋 1 筆」。
2. **空設定**：無設定檔時匯入 → 設定檔被建立且內容正確。
3. **空匯入檔** `{}` → 回 0，設定不變。
4. **中文**：匯入 `{"名稱":"測試"}` → `get 名稱` 印出「測試」，設定檔內無 `\u`。
5. **來回測試**：`export -o f.json` → 清空 → `import f.json` → 內容相同。
6. **BOM**：以 `utf-8-sig` 寫入匯入檔 → 成功。
7. **錯誤：檔案不存在** → 1，stderr 開頭「錯誤：」。
8. **錯誤：非法 JSON** → 1（確認不是 2）。
9. **錯誤：頂層為陣列** → 1。
10. **錯誤：巢狀值** → 1，且原設定檔內容完全未變（原子性）。
11. **錯誤：目前設定檔損壞** → 2。

### 3. `CLAUDE.md`

目錄說明的子指令清單加上 `import`（一行）。

## 驗證

1. `PYTHONUTF8=1 python -m pytest -q` —— 既有測試 + 新測試全綠。
2. 手動冒煙：

   ```bash
   TMP=$(cygpath -w "$(mktemp -d)")
   CFGCLI_HOME="$TMP" PYTHONUTF8=1 python -m cfgcli.cli set theme dark
   echo '{"theme":"light","名稱":"測試"}' > "$TMP/in.json"   # 路徑用 cygpath 轉過的
   CFGCLI_HOME="$TMP" PYTHONUTF8=1 python -m cfgcli.cli import "$TMP/in.json"
   CFGCLI_HOME="$TMP" PYTHONUTF8=1 python -m cfgcli.cli list
   ```

3. 本機 commit：「新增 import 子指令與測試」。
