# CHANGELOG — say_ui.py 中文語音播放器

> 版本格式：`MAJOR.MINOR`（minor 保持兩位數，例如 1.01）。
> 對應檔案：`skills/say_ui.py`（GUI 版）。CLI 版見 `skills/say.py`。

## v1.01 — 2026-06-20

### 新增

- **版本號顯示**：視窗標題顯示 `中文語音播放器 v1.01（2026-06-20）`；程式內以 `__version__` / `__release_date__` 常數記錄。
- **音量控制（三顆按鈕）**：
  - 🔊 **音量增大**（+10）
  - 🔉 **音量減小**（-10）
  - 🔇 **靜音**（toggle，按鈕在「靜音」↔「取消靜音」切換）
  - 旁邊顯示目前音量（0–100）。底層用 WMP COM `settings.volume` 與 `settings.mute`。
- 新增模組函式 `clamp_volume()`（夾界 0–100）與 `WmpAudio.set_volume/get_volume/change_volume/toggle_mute`。

### 驗證

- Writer → QA（24 驗證點 PASS）→ code-reviewer 三 agent 流程；ruff 乾淨。

## v1.00 — 2026-06-20

### 新增（初版 GUI）

- tkinter 中文 GUI 語音播放器。
- 文字來源優先序：`--file` ＞ `--text` ＞ **系統剪貼簿（預設）**。
- edge-tts 合成 MP3（`zh-TW-HsiaoChenNeural`）→ Windows Media Player COM 播放。
- 功能：講稿顯示區、播放/暫停切換、重播、變慢/變快（0.5–2.0x 即時變速）、循環播放、離開（含右上角 X，自動清暫存檔）。

### 已知 nice-to-have（reviewer 標記、非必改）

- 播完後（循環關閉時）播放鈕仍停在「暫停」字樣，可加 playState 輪詢同步。
- 暫存 mp3 偶發殘留 %TEMP%（unlink 撞 WMP 檔案鎖），可關閉前先卸載 URL 再刪。
- 剪貼簿 PowerShell fallback 對 Big5 外字元（emoji/日文）會缺字（主路徑 tkinter 不受影響）。

---

## 相關工具

- `skills/say.py` — CLI 版（文字 → edge-tts MP3 → PowerShell MediaPlayer 播放），無 GUI。
