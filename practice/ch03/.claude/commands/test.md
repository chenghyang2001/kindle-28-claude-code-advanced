---
description: 跑 cfgcli 全部測試並摘要結果
allowed-tools: Bash(PYTHONUTF8=1 python -m pytest:*)
---
執行 `PYTHONUTF8=1 python -m pytest -q $ARGUMENTS`，然後用繁體中文回報：通過/失敗數量；若有失敗，列出測試名稱與一句話原因。不要修改任何檔案。
