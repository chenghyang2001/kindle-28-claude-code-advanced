## 測試規則
- 每個新函式至少 3 個測試：正常、邊界（空字串／None）、錯誤。
- 測試檔命名 `tests/test_<模組>.py`，一個模組一個測試檔。
- data/ 裡的範例筆記只能新增在 `data/extra/` 子資料夾，避免破壞 test_cli「剛好 2 個 .md」的假設。
- 覆蓋率目標 85%，低於 85% 不得合併。
- 不在測試裡用 `time.sleep`；需要時間的地方注入假時鐘。
- 跑全部測試的指令：`PYTHONUTF8=1 python -m pytest -q`；只跑單一檔：`PYTHONUTF8=1 python -m pytest tests/test_core.py -q`。

