# Claude Code 進階 — Claude Code 學習專案

> 模組化示範主檔。原本 7 段塞一起的臃腫版已拆成「5 段門面 + 2 個子檔」。
> 本檔為第七課綜合題的示範產物，不影響真實根目錄 CLAUDE.md。

## 專案說明
《Claude Code Advanced》(Javier Rayón, 2026) 的結構化學習課程，由 study-scaffold skill 生成。共 17 課，對應書本 6 部 + 附錄。

## 架構
- `demo/[NN-課程名]/` — 各課練習（基礎 → 進階 → 綜合）
- `demo/[NN]/answer/` — 本課解答
- `demo/[NN]/starter/` — 上一課的 answer/（carry 自動攜帶；[01] 無）
- `docs/` — 踩坑紀錄等學習文件
- `skills/` — 自製 skill / script（含語音工具）

## 攜帶機制
完成第 N 課後執行 `/study-scaffold carry N`，自動把 `[N]/answer/` 複製到 `[N+1]/starter/`。

## 來源
原始 PDF：`pdf/claude-code-advanced.pdf`（圖片型，722 頁）。

## NotebookLM
語音摘要 Notebook：尚未建立（可執行 `/study-scaffold nlm` 補跑）。

---

## 模組化規則引入（@import）
<!-- 又長又會持續增補的規則抽成子檔；主檔只留門面 + 引入行 + 一句註解 -->

@instructions/interactive-teaching.md   <!-- 互動問答上課的 7 條規則（一次一題、未經同意不執行指令…） -->
@instructions/voice-playback.md         <!-- 每回合語音播報流程 + 已知 caveat -->
