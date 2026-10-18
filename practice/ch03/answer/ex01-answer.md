# 練習 01 解答 — 先計畫再動手（Plan Mode）

## 題目專案

自建的小 CLI `cfgcli`（Python，設定存成 JSON）：

| 檔案 | 內容 |
| --- | --- |
| `cfgcli/store.py` | `config_path()` / `load_config()` / `save_config()`；`CFGCLI_HOME` 環境變數可改設定檔位置 |
| `cfgcli/cli.py` | `set` / `get` / `list` 子指令（本練習新增 `export`） |
| `tests/test_cli.py` | 既有 3 個測試 |

基線先 commit（`d367403`），之後才進計畫模式，方便看 diff。

## 任務 1：觸發 Plan Mode 的任務描述

```text
為這個 CLI 加一個 `export` 子指令，把目前設定輸出成 JSON。
先給我實作計畫（要改哪些檔、新增哪些函式、測試怎麼寫），等我說 ok 再寫。
```

實際操作：呼叫 `EnterPlanMode` 進入計畫模式（此時只能讀檔、只能寫計畫檔），寫完計畫後呼叫 `ExitPlanMode` 送審，核准後才動 `cfgcli/cli.py`。

## 計畫 v1（第一版，未審查）

1. 在 `cfgcli/store.py` 新增 `export_config(path)`：把設定寫到指定檔案。
2. 在 `cfgcli/cli.py` 新增 `cmd_export(args)`，註冊 `export` 子指令，參數 `--output/-o`（必填）。
3. 順便把 `cmd_list` 的輸出也改成 JSON，讓兩個指令格式一致。
4. 在 `tests/test_cli.py` 加一個測試：export 後讀檔比對內容。

## 任務 2：計畫審查（修改了 4 個步驟）

| v1 步驟 | 問題 | 修改後 |
| --- | --- | --- |
| **3. 把 `list` 也改成 JSON** | 超出任務範圍；改到既有指令輸出，會打破 `test_list_sorted` 和使用者依賴 `key=value` 格式的腳本。這是審查重點「會不會動到不該動的檔」的典型例子 | **整步刪除**，`list` 不動 |
| 2. `--output` 必填 | 無法 `cfgcli export > x.json` 或接管線，違反 CLI 慣例 | 預設輸出 stdout，`-o` 選填 |
| 1. store 新增 `export_config(path)` | 和 `save_config` 重複寫檔邏輯；檔案 I/O 混進資料層較難測 | 改純函式 `to_json(config) -> str`，寫檔留在 CLI 層；`store.py` 不改 |
| 4. 只有 1 個 happy path 測試 | 漏掉測試：空設定、中文、壞檔 | 新檔 `tests/test_export.py`，5 個測試（不改既有測試檔） |

最重要的一條是**刪除步驟 3**：v1 裡最危險的就是這種「順便」的改動，在計畫階段刪掉，比寫完再 revert 便宜得多。

## 計畫 v2（核准版）重點

- `to_json()` 用 `ensure_ascii=False, indent=2, sort_keys=True`（中文保留原文、輸出穩定可 diff）
- `cmd_export()`：無 `-o` 印 stdout；有 `-o` 寫檔（UTF-8），`OSError` → stderr + exit 1
- 壞掉的設定檔沿用既有 `ValueError` → `main()` 回 exit 2
- 不改：`store.py`、`set/get/list`、`tests/test_cli.py`

## 實作與驗證結果

```text
$ PYTHONUTF8=1 python -m pytest -v
tests/test_cli.py::test_set_then_get PASSED
tests/test_cli.py::test_get_missing_key_returns_error PASSED
tests/test_cli.py::test_list_sorted PASSED
tests/test_export.py::test_export_stdout_is_valid_json PASSED
tests/test_export.py::test_export_empty_config PASSED
tests/test_export.py::test_export_keeps_chinese PASSED
tests/test_export.py::test_export_to_file PASSED
tests/test_export.py::test_export_corrupt_config_returns_error PASSED
8 passed in 0.15s

$ python -m cfgcli.cli set 名稱 測試 && python -m cfgcli.cli set theme dark && python -m cfgcli.cli export
{
  "theme": "dark",
  "名稱": "測試"
}
$ python -m cfgcli.cli export -o <Windows 路徑>\out.json
已匯出到 ...\out.json
```

diff 範圍：只動 `cfgcli/cli.py`（+26/−1）＋ 新增 `tests/test_export.py`，與計畫一致。

## 驗收

- [x] 拿到一份分步計畫（非直接動手）：`EnterPlanMode` → 計畫檔 → `ExitPlanMode` 核准後才寫碼
- [x] 對計畫做了實質審查：v1 → v2 改了 4 步，其中刪掉 1 個越界步驟

## 實作中碰到的小插曲（計畫沒預料到的）

1. 用 heredoc 包 Python 產生程式碼時，`"\n"`、`"\u"` 被當成跳脫字元 → SyntaxError，改用 Edit 修正。
2. Git Bash 的 `/tmp/...` 路徑傳給 Windows Python 的 `-o`，被寫到 `C:\tmp\...`，改用 `cygpath -w` 轉換。這條寫進了練習 02 的 CLAUDE.md「雷區」。
