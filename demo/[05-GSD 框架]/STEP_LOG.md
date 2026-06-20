# STEP_LOG — [05] GSD 框架

> 記錄本課的學習過程、卡關與突破。完成後重要踩坑彙整到 `docs/踩坑紀錄.md`。

## 學習日期
- 2026-06-20

## 我做了什麼
1. 基礎：把「say.py/say_ui.py 整合成語音套件」拆成 5 phases，每階段定客觀 gate（解答 `answer/ex01-answer.md`）。
2. 進階：選 Phase 2 核心實作做 multi-agent 分工（指揮者/Researcher/Builder/Reviewer），寫出防越權三機制——邊界 + Never modifies + 信號檔（解答 `answer/ex02-answer.md`）。
3. 綜合（真的 build）：用 GSD 跑真實重構——把 clamp_rate/clamp_volume 抽成 `skills/audio_utils.py`、say_ui.py 改 import、重打包 exe。Phase 2-3 實跑 code-writer→qa→reviewer 三-agent 鐵律。交付物 + manifest 見 `answer/phase0-spec.md`、`answer/ex03-answer.md`。

## 卡關與解法
- 卡關：reviewer 抓到「磁碟上 exe 是重構前舊版，onefile 能否收進 audio_utils 未實證」。
  - 根本原因：QA 只跑了原始碼模式（CWD=skills/ import 必成功），對 onefile 打包風險零覆蓋。
  - 解法：重打包 + 用 `build/say_ui/Analysis-00.toc`、`PYZ-00.toc` 含 audio_utils 證明 bundle；再啟動 exe（`Get-Process say_ui`=2）證明 runtime import 可解析。
- 卡關：判斷 exe 是否在跑，`tasklist | grep say_ui` 連續誤回 0。
  - 根本原因：onefile 冷啟動慢 + 編碼/時機；快速輪詢不可靠。
  - 解法：改用 `powershell Get-Process say_ui`（準）。

## 關鍵收穫（3 句以內）
- GSD = phases + 客觀 gate；gate 必須可明確判定（測試綠/可編譯/能跑），不能「感覺差不多」。
- multi-agent 防亂三件套：邊界（誰能寫什麼）、Never modifies（守唯讀者客觀性）、信號檔（交棒觸發點）。
- 驗證要用確定性證據（toc / Get-Process），不要用快速輪詢自我欺騙——呼應第四課脈絡衛生。

## 自評
- 基礎練習：✅ 完成
- 進階練習：✅ 完成
- 綜合挑戰：✅ 完成（真的 build：audio_utils 抽離 + exe 重打包驗證）
