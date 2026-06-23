# Session 13 — 第 3 章「80/20 計畫法」語音摘要 + 計畫交叉審查雙 Session 實戰

**日期**：2026-06-23（跨夜，始於 2026-06-22 晚）
**機器**：NB00547
**主題**：把第 3 章 .m4a 語音轉成繁中摘要筆記，並據此建一個「計畫交叉審查」練習包，實跑雙 Session（規劃者 A / 審查員 B）三輪閉環 v1→v3

---

## 完成事項

### 語音轉錄與摘要

- 用 `faster-whisper`（small / int8 / CPU）轉錄 `第03章｜讓_AI_一次寫對的_8020_計畫法.m4a`（984 秒 / 16.4 分鐘 / 532 句），逐字稿存 `C:/tmp/ch03.txt`
- 中文檔名在 ffprobe / cp 下有編碼問題 → 先用 Python `shutil.copy` 複製到 `C:/tmp/ch03.m4a` 再處理
- Windows Store 版 python 讀不到 MSYS `/tmp` → 轉錄腳本與素材一律放 `C:/tmp/`（Windows 路徑）
- 產出第 3 章摘要筆記 `demo-ch3-doc/ch03-80-20-計畫法摘要.md`（114 行）

### 交叉審查練習包（demo-01-spec-review）

- 主題沿用本章自身範例（OAuth 登入系統），刻意在 `PLAN.md` 埋 11 個破綻供審查
- 完整練習材料：README / REQUIREMENTS / PLAN / REVIEW 模板 / ANSWER-KEY / prompts(A 規劃者、B 審查員)

### 雙 Session 三輪交叉審查實戰（本 session 核心）

- 用 `/clone-session` 開第二視窗當 Session B（審查員）
- 使用者扮 Session B 兩輪審查、Claude 扮 Session A 規劃者修計畫，跑出 `PLAN.md → PLAN-v2.md → PLAN-v3.md` 收斂
- 第一輪：使用者抓到 10.5/11 埋的坑 + 1 個未埋的真破綻（GitHub 私密 email → null email）
- 第二輪：使用者抓到 **v2 自己引進的真漏洞**（account-linking 劫持：用 email 當合併鍵卻沒驗 `email_verified`）+ Redis SPOF 無降級策略
- v3 清掉兩個 🔴、吸收 6 個 🟡/🟢，並把產品決策（24h 語意、單/全裝置登出）移入「待業主確認」

## 關鍵技術筆記

- **語音播報慣例**：本專案每回合用 `skills/dist/say_ui.exe --file skills/_answer.txt --autoplay`，需先 `cd` 到 repo root（bash cwd 漂到子目錄時相對路徑會找不到 exe，踩過一次）
- **faster-whisper 中文**：small int8 CPU 轉 16 分鐘約 3-6 分鐘；加 `initial_prompt` 提示繁中主題可降低同音錯字
- **背景任務路徑陷阱**：`run_in_background` 的 python 腳本路徑要用 Windows 路徑（`C:/tmp/xxx.py`），不能用 `/tmp`

## 教學重點（交叉審查的 meta-lesson）

1. **停止條件是「🔴 = 0」不是「審到完美」**——v3 已收斂就核准，別無限往 v4/v5 鑽
2. **區分工程瑕疵 vs 產品決策**——後者列「待業主確認」，不該為它重畫計畫
3. **破綻在升級＝邊際效益遞減訊號**：v1 地基沒打 → v2 修舊洞挖新洞 → v3 收尾，越來越細就該收手

## 產出檔案

| 檔案 | 說明 |
|------|------|
| `demo-ch3-doc/ch03-80-20-計畫法摘要.md` | 第 3 章繁中摘要筆記（已由平行 session commit e074f2c）|
| `demo-ch3-doc/demo-01-spec-review/*` | 交叉審查練習包 + PLAN v1/v2/v3 + 兩輪 REVIEW（已 commit）|
| `summary-02-sessions/2026-06-23/session13-summary.md` | 本檔 |

> 註：`demo-ch3-doc/` 全部內容已被平行 session 於 commit `e074f2c` 收錄，本 session 專案 repo 僅新增此 summary。

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] （可選）回 Session B 對 `PLAN-v3.md` 做最後 confirm，🔴=0 即回「核准」正式結束閉環
- [ ] 清掉 `demo-ch3-doc/demo-01-spec-review/bash.exe.stackdump`（誤入版控的當機殘檔，應加進 .gitignore）
- [ ] 第 4 章可比照 `/chapter-audio` + 練習包模式繼續

### 進行中（需接續）

- 交叉審查閉環已實質完成（v3 收斂），僅差 Session B 一句正式「核准」收尾，非必要

### 注意事項

- 本機 hostname 為 **NB00547**（與 short-term 檔名綁定）；同日有多台機器平行 session（DESKTOP-FFSFP66、user 家用機），session 編號靠 summary 檔推算易撞，新增前先 `find` 確認
- `C:/tmp/ch03.txt` 逐字稿可重用（生簡報 / NotebookLM）；`C:/tmp/ch03.m4a` 為複製檔可刪
