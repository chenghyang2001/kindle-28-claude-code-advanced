# Demo 01：計畫交叉審查練習（雙 Session 雙重檢視）

> 對應《Claude Code Advanced》第 3 章「進階戰術 I：引入『資深工程師』進行雙重檢視」。

## 你要練什麼

把自己訓練成 **Session B（審查員）**——一位充滿懷疑精神的 **Staff Engineer**。
拿到一份看起來很專業的開發計畫，要能挑出：

- 🩹 **脆弱點**（fragile points）：哪裡一碰就壞
- 🕳️ **缺失的邊緣情況**（missing edge cases）：happy path 以外沒想到的狀況
- 🔗 **未考慮的依賴關係**（unconsidered dependencies）：外部服務、執行順序、資料相依

## 角色與流程（對照投影片）

```
Session A (規劃者)  ──提交初步計畫──▶  Session B (審查員 / Staff Engineer)
       ▲                                         │
       └──────── 核准或提出修正後，退回執行 ◀──────┘
```

- **Session A（規劃者/協調者）**：拆解任務、更新路線圖，**不寫程式**。產出 `PLAN.md`。
- **Session B（審查員）**：扮 Staff Engineer，無情審查 `PLAN.md`，把發現寫進 `REVIEW.md`。

## 檔案地圖

| 檔案 | 角色 | 用途 |
|---|---|---|
| `REQUIREMENTS.md` | 共用 | 原始需求（審查時拿來對照計畫有沒有達標） |
| `PLAN.md` | Session A 產出 | **被審查的對象**（已故意埋瑕疵） |
| `prompts/session-a-planner.md` | Session A | 規劃者的提示詞（要重做/修計畫時用） |
| `prompts/session-b-reviewer.md` | Session B | 審查員的提示詞（複製貼上即可開審） |
| `REVIEW.md` | Session B 填寫 | 審查發現清單（模板，等你填） |
| `ANSWER-KEY.md` | 解答 | 埋了哪些坑（**練完再看**，先別偷看） |

## 怎麼開兩個 Session 練習

### 做法 A：你自己當審查員（最推薦，先練眼力）

1. 開 **Session B**：把 `prompts/session-b-reviewer.md` 的內容貼進去，並附上 `REQUIREMENTS.md` + `PLAN.md`。
2. 在開審前，**先自己讀 `PLAN.md`**，把你覺得有問題的地方寫進 `REVIEW.md`。
3. 再讓 Session B 的 AI 審一次，跟你的清單比對。
4. 最後翻 `ANSWER-KEY.md` 對答案，看漏了幾個。

### 做法 B：完整雙 Session 對打（體驗真實流程）

1. **Session A**（新視窗）：貼 `prompts/session-a-planner.md`，讓它根據 `REQUIREMENTS.md` 重新產一份計畫（覆蓋或另存 `PLAN-v2.md`）。
2. **Session B**（另一視窗）：貼 `prompts/session-b-reviewer.md` + 那份計畫，產出審查意見。
3. 把 Session B 的意見**貼回 Session A**，要求它修計畫 → 產出 `PLAN-v2.md`。
4. 重複到 Session B 回覆「**核准（approved）**」。

> 開第二個視窗的方式：可用 `/clone-session`（複製目前設定開新視窗），或直接另開一個 Claude Code CLI。

## 驗收標準（你算練成的條件）

- [ ] 在 `REVIEW.md` 找出 **至少 7 個** 真實問題（滿分 11，見 ANSWER-KEY）
- [ ] 每個發現都標上類別（脆弱點 / 邊緣情況 / 依賴）與嚴重度（🔴必改 / 🟡建議 / 🟢備註）
- [ ] 對每個 🔴 給出**具體修正方向**，而不只是「這裡怪怪的」
- [ ] 能解釋「為什麼在純文字計畫階段抓出來，比寫完幾千行才發現便宜得多」
