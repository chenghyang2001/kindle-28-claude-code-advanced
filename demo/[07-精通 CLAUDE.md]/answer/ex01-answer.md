# 練習 01 解答 — 為 skills/ 語音工具寫一份精煉 CLAUDE.md

> 任務 1（5 段骨架）+ 任務 2（填真實內容）合併，以下即可直接當 `skills/CLAUDE.md`。

---

# 中文語音工具（skills/）

## 專案概述
把文字轉成繁體中文語音的小工具。提供 CLI 版與 GUI 版；GUI 支援播放/暫停、重播、變速、音量、靜音、循環、**自動播放**，預設讀系統剪貼簿。亦含一支與語音無關的 Ralph 自主迴圈腳本。

## 架構
```
skills/
├─ say_ui.py        # GUI 主程式（tkinter + WMP COM）；--file/--text/剪貼簿、--autoplay
├─ audio_utils.py   # 純函式：clamp_rate / clamp_volume（被 say_ui import，可獨立測）
├─ say.py           # 獨立 CLI 版（edge-tts → MP3 → 播放）
├─ ralph_loop.sh    # Ralph 自主迴圈（TASK.md 驅動，與語音無關）
├─ say_ui.spec      # PyInstaller onefile 設定（相對路徑）
├─ app_icon.ico     # 視窗/exe 圖示
└─ dist/say_ui.exe  # 打包產物
```

## 技術堆疊
- Python 3.x
- TTS：`edge-tts`，語音 `zh-TW-HsiaoChenNeural`
- 播放：Windows Media Player COM（`WMPlayer.OCX`）透過 `pywin32`
- GUI：`tkinter`
- 打包：PyInstaller（onefile，單檔 exe）

## 執行方式（可直接複製跑）
```bash
# 原始碼直跑（GUI，自動播放某檔）
.venv/Scripts/python.exe skills/say_ui.py --file skills/_answer.txt --autoplay

# 打包 exe（務必在 skills/ 目錄下跑，spec 用相對路徑）
cd skills && PYTHONUTF8=1 ../.venv/Scripts/pyinstaller.exe say_ui.spec --noconfirm

# 確認 exe 是否在跑（用 Get-Process，不要用 tasklist）
powershell -NoProfile -Command "(Get-Process say_ui -EA SilentlyContinue|Measure-Object).Count"

# Ralph 自主迴圈乾跑
bash skills/ralph_loop.sh --task TASK.md --dry-run
```

## 重要架構決策（為什麼這樣設計）
1. **clamp 純函式抽到 audio_utils.py**：為了不開 GUI / 不碰 COM 就能跑單元測試（關注點分離）。
2. **打包必須在 skills/ 執行**：`say_ui.spec` 用相對路徑 `say_ui.py`/`app_icon.ico`，換 CWD 會找不到進入點。
3. **確認 exe 狀態用 `Get-Process` 而非 `tasklist`**：`tasklist | grep` 在 onefile 冷啟動期會誤回 0（本專案踩坑）。
4. **GUI 啟動時只讀一次文字、不重讀剪貼簿**：故「每回合語音播報」必須關舊開新，不能只更新剪貼簿。

## 驗收
- [x] 5 段齊全
- [x] 執行指令可直接複製跑
- [x] ≥1 條「為什麼這樣設計」（這裡 4 條，全是本專案才有的真實資訊）
