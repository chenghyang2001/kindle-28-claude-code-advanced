# Claude Code 開源資源矩陣 — 查證與評估摘要

> 來源：課程圖片「開源範本與實例矩陣」＋ 2026-07-23 GitHub 即時查證
> 專案：kindle-28-claude-code-advanced

## 一、查證結果總表

| 圖片名稱 | 實際 repo | Stars | 活躍度 | 評級 |
| --- | --- | ---: | --- | --- |
| claude-code-templates | `davila7/claude-code-templates` | 29.8k | 非常活躍（查證當天仍有更新） | ★★★ 必知 |
| awesome-claude-code | `hesreallyhim/awesome-claude-code` | 50.7k | 非常活躍 | ★★★ 必知 |
| claude-starter-kit | ⚠️ 無法唯一對應（205 個同名候選，最高僅 331⭐） | ~100–331 | 模糊 | ★ 跳過 |
| my-claude-code-setup | `centminmod/my-claude-code-setup` | 2.5k | 活躍 | ★★ 值得讀一次 |
| claude-md-examples | `ArthurClune/claude-md-examples` | 140 | 小型、無描述 | ★ 跳過 |

## 二、圖片的問題點

1. **等級落差被視覺抹平**：前兩名 50.7k / 29.8k，「針對型」那排直接掉到幾百星，圖上看起來卻像同一等級。
2. **未標注作者（owner）**：`claude-starter-kit` 沒寫 owner，同名 repo 有 205 個，照名字去找很可能裝到別人的 repo。
3. **有明顯遺漏**：缺了 `VoltAgent/awesome-claude-code-subagents`（23.6k⭐，100+ 專業 subagent 合集）與官方 plugin marketplace——這兩個比針對型那排三個都重要。
4. **驗證時間過舊**：「Verified May 2026」距查證日已兩個月，此生態迭代極快。

## 三、對照本機環境的採用建議

| 資源 | 建議 | 理由 |
| --- | --- | --- |
| `awesome-claude-code` | 收藏，定期翻目錄 | 策展清單、訊噪比最高；可搭配 `/claude-code-setup:claude-automation-recommender` 每隔幾章看一次 |
| `claude-code-templates` | 當「食譜庫」挑著撈，勿整包裝 | 本機已有 100+ skills、40+ subagents，整批灌入 = context 污染 + 觸發詞打架。遇特定需求時去 aitmpl.com 撈單一 agent/command 回來改 |
| `my-claude-code-setup` | 花 30 分鐘讀原始碼 | 其 memory bank 系統與本機三層記憶（MEMORY.md / short-term / hot-cache）是同一問題的不同解法，可對照偷招，不建議換掉現有體系 |
| `claude-starter-kit` | 跳過 | 給從零開始的人；本機 CLAUDE.md 體系（模組化 @instructions、鐵律、hooks）成熟度已超過 |
| `claude-md-examples` | 跳過 | 同上 |

## 四、一句話總結

這張圖當「入門地圖」及格，當「精確清單」不及格——前排兩個記下來，後排三個裡只有 centminmod 值得花 30 分鐘，其餘跳過。
