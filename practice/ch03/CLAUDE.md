

## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。

## 專案簡報：cfgcli

小型設定管理 CLI（Python 3，只用標準函式庫＋pytest）。設定存成 JSON。

### 目錄
- `cfgcli/store.py`：設定檔讀寫（`config_path` / `load_config` / `save_config`）。**資料層只放讀寫，不放輸出格式。**
- `cfgcli/cli.py`：argparse 子指令（set / get / list / export）。每個子指令 = 一個 `cmd_xxx(args) -> int` + 在 `build_parser()` 註冊。
- `tests/`：pytest。每個新子指令一個新測試檔 `tests/test_<指令>.py`，不改既有測試檔。

### 慣用指令
- 測試：`PYTHONUTF8=1 python -m pytest -q`（或 `/test`）
- 手動跑：`CFGCLI_HOME=<暫存目錄> PYTHONUTF8=1 python -m cfgcli.cli <子指令>`

### 慣例
- 回傳碼：0 成功、1 使用者錯誤（找不到 key、寫檔失敗）、2 設定檔損壞（`ValueError` 由 `main()` 統一轉換）。
- 錯誤訊息印到 stderr，開頭「錯誤：」。
- JSON 輸出一律 `ensure_ascii=False`（保留中文）。
- 測試必須 `monkeypatch.setenv("CFGCLI_HOME", tmp_path)`，絕不讀寫真實 `~/.cfgcli`。
- 每個新功能的測試至少涵蓋：happy / 空設定 / 中文 / 錯誤。

### 雷區
- **不要改既有子指令的輸出格式**（`list` 的 `key=value` 有腳本依賴）。新需求一律做成新子指令或新選項。
- Git Bash 的 `/tmp/...` 路徑傳給 Windows Python 會變成 `C:\tmp\...`；檔案路徑參數先 `cygpath -w`。
- 用 bash heredoc 產 Python 原始碼時，`"\n"`、`"\u"` 會被轉義壞掉；改程式碼用編輯工具，不要用 heredoc 生成。
