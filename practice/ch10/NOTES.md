# NOTES — K28 第 10 章練習（onboard + audit）

## 做了什麼

1. `git clone --depth 1 https://github.com/pallets/itsdangerous vendor/itsdangerous`（commit `672971d`），`vendor/` 已加進 `.gitignore`，全程只讀不改（`git -C vendor/itsdangerous status` 乾淨）。
2. 在本專案建 `.venv`（已 gitignore），只裝 `pytest`、`freezegun` 來跑官方測試，沒有安裝到全域。
3. 練習 01：模組地圖、資料流圖、例外階層、`/init` 式 CLAUDE.md 草稿；5 個疑點自問自答，每題附 `檔案:行號`，並寫成 `scripts/ex01_probe.py` 實際驗證。
4. 練習 02：10 項 audit 發現（高 1／中 3／低 6），每項附 `檔案:行號`；能跑的都寫進 `scripts/ex02_audit_probe.py` 實測。最嚴重的 F1（`loads_unsafe` 解壓炸彈）除了修補方向，也用子類別做了可執行的修補驗證。

## 產出檔案

| 檔案 | 內容 |
| --- | --- |
| `answer/ex01-answer.md` | 練習 01 解答 |
| `answer/ex02-answer.md` | 練習 02 解答（含延伸思考） |
| `scripts/ex01_probe.py`、`scripts/ex01_output.txt` | 練習 01 驗證腳本與輸出 |
| `scripts/ex02_audit_probe.py`、`scripts/ex02_output.txt` | 練習 02 佐證腳本與輸出 |
| `.gitignore` | 排除 `vendor/`、`.venv/`、快取與當機檔 |

## 驗證結果

- 官方測試：`PYTHONPATH=src .venv/Scripts/python -m pytest -q` → **297 passed**（第一次缺 `freezegun`，2 個測試檔收集失敗；裝進本地 `.venv` 後全過）。
- `PYTHONUTF8=1 python scripts/ex01_probe.py` → 5/5 題通過。
- `PYTHONUTF8=1 python scripts/ex02_audit_probe.py` → 9 個佐證全部執行完成。重點數字：27 KB 的偽造 token 讓 `loads_unsafe` 峰值記憶體到 60.1 MB（`loads` 只要 0.2 MB）；加上 1 MB 解壓上限後降到 2.1 MB，正常 token 往返不受影響。
- 行號：一開始用 `cat -n` 一次串多個檔案，行號有位移；最後全部改用逐檔 `grep -n` 重新確認過。

## 和題目要求的差異

- **「請 Claude 產出模組地圖」**：本身就是 Claude 在執行，所以直接由我讀碼產出，沒有另外開 `claude -p` 子行程。
- **「追問到懂」**：依本章補充改成自問自答，題目從 3 題加到 5 題，每題用腳本實證。
- **`/init`**：會在目標 repo 寫 CLAUDE.md，違反「vendor 只讀不改」，所以改成把草稿放在 `answer/ex01-answer.md` 裡。
- **`git log --oneline -20`**：`--depth 1` 只有 1 筆 commit，無法看演化歷史；需要時可 `git fetch --unshallow`。
- **audit 範例框架裡的「硬編碼機密、未參數化 SQL」**：itsdangerous 沒有資料庫、也沒有硬編碼機密，這兩類查無發現；改以這個函式庫實際的風險面（金鑰驗證、演算法、解壓、時間）來找。
- **嚴重度**：F1 標「高」是以「對不受信任輸入呼叫 `loads_unsafe`」為前提；官方文件已標示它僅供除錯，若嚴格照文件使用，實際風險會降到中。
- 沒有對上游開 issue 或 PR（題目限制不建 repo、不 push）。

## 已知限制（快速模式）

- 這是快速 demo 模式，腳本沒經過獨立 QA／審查。
- 解壓炸彈只測到 20 MB，沒有測更大的尺寸，避免拖垮本機。
- F5（SHA1）、F6（預設 salt）的風險判斷依據是一般資安共識，沒有做密碼學層級的分析。
