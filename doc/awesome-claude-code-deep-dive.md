# awesome-claude-code 深入探勘 — 介紹 + 兩分類對照本機方案

> 來源：`hesreallyhim/awesome-claude-code`（50.7k⭐，Claude Code 生態星數最高的社群專案）
> 探勘日期：2026-07-24。README 實測：25 個主題分類、收錄 225 個 GitHub 專案。

## 一、這是什麼

- **不是工具，是「Claude Code 生態系黃頁」**：整個 repo 幾乎只有一份 README，人工精選（hand-picked）分類整理社群專案，每條附連結 + 一句話介紹 + 建立/最後 commit 日期徽章（一眼判斷專案死活）。
- awesome list 是 GitHub 文化：`awesome-XXX` = 有人幫你把大海撈針做完。50.7k 星代表五萬人認為值得收藏。
- **三種用法**：有需求時查黃頁（分類跳轉）、定期翻 Recently Added 看新貨、翻目錄找靈感。
- **定位對比**：`claude-code-templates` 是素材庫（撈了就能用），awesome list 是地圖（指路不給料）。

## 二、25 個分類概覽

Start Here / From Anthropic / Documentation & Learning / Research / Providers & Runtime /
Remote Control & Voice I/O / Alternative Clients / Status Lines / Design & UI/UX /
Writing & Prose / Creative Media / Infrastructure & DevOps / Security /
Multi-Agent Orchestration / Skills / Memory & Context Persistence /
Observability & Monitoring（含 Session Monitors、Usage & Cost）/ Linting …等

> 對照發現：本機已自造其中至少 5 類的輪子（多代理編排、記憶系統、遠端遙控、語音 I/O、成本監控）。
> 所以這份清單的用途是「對答案」——看同一問題別人怎麼解，值得偷招就偷。

## 三、Memory & Context Persistence（9 個）vs 本機三層記憶

本機現況：`MEMORY.md` 索引 + 單事實檔、`short-term/` 每日快照、`hot-cache.md` 滾動精華（純 Markdown、可版控、零依賴）。

| 專案 | 解法 | 對照結論 |
| --- | --- | --- |
| **Selvedge** ⭐ | 「AI 版 git blame，記的是 why」——agent 改碼當下捕捉推理，SQLite | 本機記憶記「結論」，它記「當時為何這樣決定」，是 MEMORY.md 較弱的維度 |
| **roampal-core** ⭐ | 結果導向記憶：建議有效升權、無效降權 | learnings.md 只進不出；「淘汰壞經驗」概念可用 Markdown 慣例實現 |
| **Callimachus** | 跨工具 session 歷史全索引（關鍵字+語意搜尋） | 本機 session summary 只能 grep，語意搜尋是缺口 |
| MAMA | SQLite + 本地 embeddings，記決策演化 | 與 short-term→長期升級同構但自動化 |
| fable | 逐字轉錄索引、byte-identical 召回 | 太重，不需要 |
| presence | 每 repo 記憶 + 信心閘門 + 投影 AGENTS.md 給其他 AI 工具 | 「投影給其他工具」若開始用 Codex 可回頭看 |
| capy / Claude Mnemonic / Hivemind | 隱私虛擬化 / 通用記憶 / traces→skills | 非本機痛點，跳過 |

**結論**：檔案式記憶「可讀、可版控、可手改」是優勢，不換。吸收兩個概念：Selvedge 的「記 why」、roampal 的「壞建議降權」。

## 四、Multi-Agent Orchestration（僅 2 個）vs 本機編排體系

| 專案 | 內容 | 對照 |
| --- | --- | --- |
| **Agent Collab Skills** | 任務拆分 / 輸出調和器 / 對抗式辯論 / 共享記憶 / 驗收閘門 | 幾乎是 writer→QA→reviewer 鐵律的市集版；「輸出調和器」（多 agent 產出衝突合併）目前本機靠主 Claude 手工，可參考 |
| **gstack** | Garry Tan（YC 總裁）的個人配置「開源軟體工廠」 | 與 GSD 同類；價值在「看業界大佬怎麼組 Claude Code」 |

**觀察**：此分類只收 2 個，明顯低估實際生態——GSD、Ralph loop、superpowers 都沒被收錄。
印證 awesome list 侷限：**策展人視野有死角，清單 ≠ 全貌**；適合當起點，不能當普查。

## 五、最終建議順位

1. **Selvedge**（記 why）
2. **roampal-core**（記憶降權）
3. **Agent Collab Skills** 的輸出調和器

三者都先「讀 README 偷概念」，不急著裝——現有體系已跑順，引進工具的成本 > 借鑑想法的成本。
