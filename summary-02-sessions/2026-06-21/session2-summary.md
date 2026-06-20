# Session 2 收工 summary（2026-06-21）

## 一句話

互動問答 + 語音播報模式，連上第 9～14 課共 6 課，每課三題（基礎/進階/綜合）全完成、各自 commit + push。

## 完成內容

| 課 | 主題 | 三題核心 | commit |
|----|------|---------|--------|
| 09 | 官方外掛 | code-review 用途/時機；review→simplify 串接（必改歸零 gate）；feature-dev/review/simplify 分階段決策表 | c6338e2 |
| 10 | 既有專案 | onboard 先地圖後細節（只讀不改）；audit 三面向+分級；legacy 補 characterization test | ccf36e7 |
| 11 | 大規模開發 | 測試金字塔（下寬上窄）；安全重構（小步+測試+commit，先張網再跳）；expand/contract 分批 migration | a09123c |
| 12 | 自動化 | skill=門鈴(description)+SOP(步驟)；CI 自動 review（金鑰走 Secrets）；端到端三護欄（逾時/通知/單例鎖）+ 失敗降級 | bc50c46 |
| 13 | Agent 編排 | 三 agent 團隊（乾淨 context+獨立審查，指揮者不下場）；agent debate（多角度+多數決）；完整編排（合約 Never modifies+信號檔+越權偵測） | c231280 |
| 14 | 進階技巧 | 弱 prompt→多步拆解+成功標準；二分搜尋(100→7次)+假設驗證最小實驗+反理由化；5 招技巧手冊 | 89c2ef1 |

## 流程慣例（本 session 穩定運作）

- 每題：貼一題 → 等使用者「你回答」→ 給白話解析（對職場新鮮人）→ 每次回答前用 say_ui.exe 語音播報。
- 每課收尾：三題解答寫進 answer/、更新 STEP_LOG、carry N → 下一課 starter。
- 每課 commit + push 前都先徵求使用者同意（互動教學模式第 6 條），唯語音三步免徵詢。
- Stop hook 偵測未提交是預期行為——刻意留改動等使用者決定 commit 時機。

## 學習主線（第 9～14 課）

進階開發與精通：把大/模糊/危險的工作拆成小/明確/可驗證的步驟，每步保留「能判斷對錯、能回頭」的能力。貫穿所有 pattern（拆 prompt、安全網、二分除錯、對抗驗證、agent 分工）。

## 待辦（下個 session）

- 剩第 15（安全與成本）、16（快速參考）、17（資源）共 3 課。後兩課偏總結，較短。
- 建議開新 session 上（本 session 已 5 小時、context 偏長）。

## 備註

- 全程只動 .md（answer/STEP_LOG/starter/summary），無程式碼檔改動，未觸發 writer-QA 鐵律。
- 無 infra 配置變更（cron/port/path/env 皆未動）。
