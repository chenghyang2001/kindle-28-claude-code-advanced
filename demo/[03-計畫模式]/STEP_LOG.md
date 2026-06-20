# STEP_LOG — [03] 計畫模式

> 記錄本課的學習過程、卡關與突破。完成後重要踩坑彙整到 `docs/踩坑紀錄.md`。

## 學習日期
- 2026-06-20

## 我做了什麼
1. 以互動問答完成 Plan Mode 三題（是什麼／怎麼審查／哪種任務值得先計畫），解答寫入 `answer/ex01-answer.md`。
2. 把答案做成「文字 → 語音」工具鏈：`skills/say.py`（CLI, edge-tts → MP3 → PowerShell MediaPlayer 播放）。
3. 升級成 GUI：`skills/say_ui.py` v1.01（tkinter；播放/暫停、變速、音量增大/減小/靜音、循環、講稿顯示、自訂 icon），預設讀系統剪貼簿。
4. 用 PyInstaller 把 GUI 打包成單檔 `dist/say_ui.exe`，並換上自製喇叭 icon。
5. 建 venv + `requirements.txt`，在 venv 內重現打包，並把專案推上 GitHub（含 exe）。

## 卡關與解法
- 卡關：PowerShell 播放 MP3 時找不到檔案／播放偽失敗。
  - 根本原因：PowerShell 子行程不繼承 Git Bash 的 CWD；中文/方括號路徑編碼被搞壞；`Register-ObjectEvent` 未清理導致 exit 2 偽陰性。
  - 解法：複製到 ASCII 暫存路徑再播；腳本結尾清 EventSubscriber/Job + 明確 exit 0；只看 returncode 判失敗。
- 卡關：換了 exe icon，標題列還是 Tk 羽毛。
  - 根本原因：`--icon` 只改 exe 檔案圖示；視窗標題列是 tkinter 自己的 window icon，要程式碼 `root.iconbitmap()`，且 onefile 需 `--add-data` + `sys._MEIPASS` 才找得到 ico。
  - 解法：加 `resource_path()` + `iconbitmap`，打包加 `--add-data "app_icon.ico;."`。
- 卡關：`git add` 把 sandbox 內嵌 git repo 當壞 gitlink；PDF 64MB／方括號目錄擋不掉。
  - 根本原因：內嵌 repo 需 `git rm -rf --cached`；gitignore 中 `[02-平行化]` 的方括號是字元類別，要跳脫成 `\[..\]`。
  - 解法：移除內嵌 repo + 跳脫方括號 gitignore；pdf/ 與 build/ 一併擋掉。

## 關鍵收穫（3 句以內）
- Plan Mode 的價值＝在「還沒寫 code」時就攔住方向錯誤；判斷要不要用，看範圍 × 風險 × 可逆。
- 跨 Git Bash↔PowerShell 一律走 ASCII 暫存路徑；exe 圖示與視窗標題列圖示是兩回事。
- 用乾淨 venv 打包，exe 從 46MB 瘦到 15MB（不夾帶 numpy 等無關套件）。

## 自評
- 基礎練習：✅ 完成
- 進階練習：⬜ 完成（未進行）
- 綜合挑戰：⬜ 略過
