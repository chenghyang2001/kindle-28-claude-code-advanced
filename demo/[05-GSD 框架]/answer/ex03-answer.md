# 練習 03 解答 — 用 GSD 跑真實小專案（整合 MANIFEST）

# MANIFEST — audio_utils 抽離重構

**專案**：把 `say_ui.py` 的純函式 `clamp_rate` / `clamp_volume` 抽成獨立可測模組 `audio_utils.py`，say_ui.py 改用之。
**日期**：2026-06-20

## 各階段交付物與 gate（皆客觀可驗收）

| Phase | 交付物（路徑） | gate 條件 | 結果 |
|-------|---------------|-----------|------|
| 0 規格 | `answer/phase0-spec.md` | 規格定案、API/邊界表確定 | ✅ |
| 1 骨架 | `skills/audio_utils.py`（簽名+型別+常數） | 可 import、可編譯 | ✅ |
| 2 實作 | `skills/audio_utils.py`（含 __main__ 冒煙） | **單元測試全綠**（QA 3/3 + 7 assert） | ✅ |
| 3 整合 | `skills/say_ui.py`（改 import）+ 重打包 `skills/dist/say_ui.exe` | py_compile 過 + `import say_ui` 不報錯 + **exe 重建後可跑** | ✅ |
| 4 manifest | 本檔 | 串起所有階段 | ✅ |

## multi-agent 分工（Phase 2-3 實際執行）
- **指揮者（主 Claude）**：產合約（phase0-spec）、派工、整合、處理 reviewer 回報。不寫業務碼。
- **code-writer**：建 audio_utils.py + 改 say_ui.py（Manifest + SHA256）。
- **code-qa**：5 層驗證，3 test case 全綠；`is` 檢查確認非複製貼上。
- **code-reviewer**：adversarial review，抓到「exe 是重構前舊版、onefile 風險未實證」的關鍵缺口 → 要求補 rebuild+冒煙。

## 關鍵驗證證據（非口頭「做完了」）
- QA：clamp_rate 1.0→1.0 / 5.0→2.0 / 0.1→0.5；clamp_volume 50→50 / 150→100 / -10→0 / 33.7→33 全綠。
- `say_ui.clamp_rate is audio_utils.clamp_rate` → True（真的是同一物件）。
- onefile bundle 證明：`build/say_ui/Analysis-00.toc` 與 `PYZ-00.toc` 皆含 `audio_utils`。
- runtime：重建後 `Get-Process say_ui` = 2（父+子），exe 正常啟動 → import 在打包後可解析。

## 已知限制 / 未解問題
- `skills/` 非 package（無 `__init__.py`），靠「腳本目錄在 sys.path」吃扁平 import；若日後改用 `python -m skills.say_ui` 會壞。
- PyInstaller 重建**必須在 `skills/` 目錄下**執行（spec 用相對路徑 `say_ui.py` / `app_icon.ico`）。
- 重建未簽署 exe 首次可能被 SmartScreen 攔一次。

## 下一步
- 若要再擴大：把 synth/播放邏輯也抽成模組、補 CI 跑 audio_utils 測試。
- 本練習已達標：5 階段、每段有可驗收交付物、最終 manifest 串接完成。

## 踩坑（本課活教材）
驗證 exe 是否在跑時，`tasklist | grep say_ui` 連續多次誤回 0（編碼/時機），
改用 `powershell Get-Process say_ui` 才準。呼應第四課：脈絡/雜訊多時判斷力下降，要用**確定性證據**（toc、Get-Process）而非快速輪詢。
