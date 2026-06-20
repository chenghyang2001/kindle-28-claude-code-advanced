# STEP_LOG — [07] 精通 CLAUDE.md

> 記錄本課的學習過程、卡關與突破。完成後重要踩坑彙整到 `docs/踩坑紀錄.md`。

## 學習日期
- 2026-06-20

## 我做了什麼
1. 基礎：為 `skills/` 語音工具寫一份真實 5 段 CLAUDE.md（概述／架構／技術堆疊／可複製執行指令／4 條架構決策），可直接當 `skills/CLAUDE.md`（`answer/ex01-answer.md`）。
2. 進階（互動三題）：
   - 拆分依據：按關注點切（主題單一／能獨立理解／能單獨重用），三依據＝主題、變動頻率、重用範圍。
   - 動手拆：把 10 條混雜規則拆成 `code-quality` / `git-workflow` / `security` / `tech-stack` 四個子檔，主檔只剩薄薄 `@import`。
   - 陷阱題：模組化 4 代價（過度拆分／衝突無仲裁／**context 不會省**／間接層遮蔽），何時不該拆。
   - 解答整理在 `answer/ex02-answer.md`。

## 卡關與解法
- 卡關：直覺以為「CLAUDE.md 拆成多檔可以省 context／token」。
  - 根本原因：`@import` 在載入時把所有子檔內容**全部展開合併**進 context，總量不變。
  - 解法：認清模組化省的是維護性與跨專案重用，不是 token；要省 token 該用 skill 按需載入，而非塞進每次全載的 CLAUDE.md。

## 關鍵收穫（3 句以內）
- 拆分依據＝主題單一 + 能獨立理解 + 能單獨重用（積木化），通用規則放全域、專案規則留本地。
- 模組化最大誤解：以為能省 context——其實 `@import` 全展開，省的是維護＋重用。
- 好的模組化＝一主題一檔 + 主檔定優先序仲裁衝突 + 每個 `@import` 補一句註解。

## 綜合挑戰（capstone）
- 真的把本專案臃腫的根 `CLAUDE.md`（7 段）模組化：5 段門面留主檔、第 5/6 段（互動教學、語音播報）抽成子檔。
- 產出示範於 `answer/modular-demo/`（薄主檔 + `instructions/interactive-teaching.md` + `instructions/voice-playback.md`），**不動正在驅動 session 的真實根檔**。
- 套用三重點：按重用範圍分層（專案專屬放專案 instructions）／不過度拆／主檔每個 `@import` 補註解。
- 解答見 `answer/ex03-answer.md`。

## 自評
- 基礎練習：✅ 完成
- 進階練習：✅ 完成（互動三題）
- 綜合挑戰：✅ 完成（真模組化本專案 CLAUDE.md → modular-demo/）
