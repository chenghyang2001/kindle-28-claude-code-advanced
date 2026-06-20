# 練習 02 解答 — 在一個階段引入 multi-agent 分工

## 任務 1：選 Phase 2「核心實作」做分工

**為什麼選它**：合成 / 播放控制 / 剪貼簿讀取 三模組相對獨立可平行寫，又都需審查把關。

| Agent | 讀 | 寫 | 交付物 |
|-------|----|----|--------|
| 指揮者（主） | 規格 | 合約（不碰 src） | api-spec（函式簽名/IO）、整合結果 |
| Researcher | 舊 say.py/say_ui.py | ❌ | 相依/可重用地圖 |
| Builder ×N | 合約＋地圖 | **只在 src/** | 寫好＋測試綠的模組 |
| Reviewer | Builder 成果 | ❌ | 審查報告（must-fix / 建議） |

**資料流**：規格→合約；合約→Researcher/Builder；地圖→Builder；Builder 成果→Reviewer；報告→指揮者/Builder。

## 任務 2：如何避免越權 / 衝突（三機制）

### 1. 邊界（誰能碰什麼）
- Researcher / Reviewer = **唯讀**，只產報告。
- Builder = 只寫 **src/**、依合約，不改合約本身。
- 指揮者 = 只動合約與整合層，不寫業務碼。
- **可寫範圍互不重疊** → 不會兩人改到同一檔打架。

### 2. Never modifies 條款（守客觀性）
- 每個唯讀 agent 的指令白紙黑字寫：**「你絕對不可修改 src/」**。
- 為什麼關鍵：Reviewer 最容易手癢順手改 code → 變球員兼裁判，審查失去客觀性。
- 他只能在報告列 must-fix，由 Builder 去改。

### 3. 信號檔（交棒觸發點）
- Builder 寫完 → 產 `BUILD_COMPLETE.md` → 指揮者才叫 Reviewer 上場。
- Reviewer 審完 → 產 `REVIEW_COMPLETE.md`（寫明 通過 / 要改）。
- 指揮者看內容決定：有 must-fix → 丟回 Builder 修再跑一輪；通過 → 進下一階段。
- 好處：交棒**明確、有憑據**，不會搶跑或漏接。

**一句話**：邊界決定誰能碰什麼、Never modifies 守住唯讀者客觀性、信號檔讓交棒有明確觸發點。

## 延伸思考：GSD 階段化 vs 單純 todo list
- **差別**：todo list 是扁平清單、無強制檢查點，做到一半才發現方向錯；GSD 有 phases + 客觀 gate，**每段守門、風險分段控管**，還能在階段內平行分工。
- **值得用**：長型 / 高風險 / 多人或多 agent / 不可逆操作多的專案（重構大模組、上線部署）。
- **不值得（殺雞用牛刀）**：一次性腳本、單檔小修、typo——直接做比設流程快。
