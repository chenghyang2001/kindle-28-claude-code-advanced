## 程式碼風格
- 命名一律 snake_case，常數全大寫；布林變數用 is_/has_ 開頭。
- 每個函式不超過 30 行，巢狀不超過 3 層，超過就提取子函式。
- 註解寫「為什麼」不寫「做什麼」，註解與 docstring 一律繁體中文。
- 讀寫檔一律 `encoding="utf-8"`，不依賴系統預設（Windows 是 cp950）。
- 不用裸 `except:`；I/O 錯誤只在 cli.py 處理，core.py 只丟 ValueError。
- 新增 CLI 參數時，help 文字要用繁體中文，且 README 與本檔「執行方式」同步更新。
- 單一輸入檔大小上限 2 MB（MAX_FILE_BYTES = 2_097_152），超過要印警告並略過。
- 輸出欄位順序固定為 lines → words → headings，不可調換（下游試算表依賴欄位位置）。

