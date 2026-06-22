# 怎麼跑這個 demo（逐字可複製的指令）

> 對應《Claude Code Advanced》第 3 章「雙 Session 雙重檢視」。
> 本檔是 README「怎麼開兩個 Session 練習」的**逐字指令版**——直接複製貼上，不用自己想措辭。

---

## 核心一句話

每一輪審查，都用同一個句型，只換最後要審的檔名：

```
請讀 prompts/session-b-reviewer.md 當作你的角色設定，
然後對照 REQUIREMENTS.md，無情審查 PLAN.md。
```

> 關鍵：讓 AI **先讀角色提示詞**（變成充滿懷疑精神的 Staff Engineer），**再對照需求**（有客觀標準），最後才審計畫。三者順序不能亂，否則它會憑感覺誇獎而不是挑錯。

---

## 完整一輪迭代（Session B 審 → Session A 修 → 再審）

### 第 1 輪：審初稿 PLAN.md

在一個**乾淨的 Session**貼：

```
請讀 prompts/session-b-reviewer.md 當作你的角色設定，
然後對照 REQUIREMENTS.md，無情審查 PLAN.md。
```

→ 得到一份發現清單（🔴必改 / 🟡建議 / 🟢備註）+ 裁決（核准 / 需修正）。

### 第 2 輪：把審查意見退回 Session A 修計畫

在**另一個 Session**（規劃者）貼 `prompts/session-a-planner.md`，並把上一輪的 REVIEW 內容貼在它的「修計畫追加指令」區塊，要求產出 `PLAN-v2.md`。

### 第 3 輪：審修訂版 PLAN-v2.md

回到 Session B（或新開乾淨 Session），換檔名再審一次：

```
請讀 prompts/session-b-reviewer.md 當作你的角色設定，
然後對照 REQUIREMENTS.md，無情審查 PLAN-v2.md。
```

### 第 N 輪：持續到核准

```
請讀 prompts/session-b-reviewer.md 當作你的角色設定，
然後對照 REQUIREMENTS.md，無情審查 PLAN-v3.md。
```

重複「審 → 修 → 再審」，直到 Session B 回覆 **核准（approved）**、🔴 = 0 為止。

---

## 練完對答案

```
對照 ANSWER-KEY.md 看我漏了什麼
```

> 官方埋了 11 個坑：找到 7 個以上算及格，10 個以上是 Staff Engineer 水準。
> 對完答案後，把「漏掉的原因」寫進 `docs/learning-notes-reviewer.md`（見該檔的四個受害者視角 checklist）。

---

## 指令對照表（換檔名即可）

| 輪次 | 審查對象 | 指令（換最後檔名） |
|---|---|---|
| 1 | `PLAN.md`（初稿，埋了 11 坑） | `…無情審查 PLAN.md。` |
| 2 | `PLAN-v2.md`（修掉 v1 的 11 條） | `…無情審查 PLAN-v2.md。` |
| 3 | `PLAN-v3.md`（修掉 v2 新引進的 R1/R2） | `…無情審查 PLAN-v3.md。` |
| 對答案 | `ANSWER-KEY.md` | `對照 ANSWER-KEY.md 看我漏了什麼` |

---

## 為什麼要這樣跑（心法）

- **在純文字計畫階段改一行字，成本幾乎是零**；等寫了幾千行、跟資料庫深度耦合才發現架構崩潰，要花三倍時間哭著重構。
- 這套 demo 的價值就在 v1→v3 三輪**全程沒寫半行 code**，就把「會劫持帳號、多副本下漏洞百出、回滾會刪資料」的設計磨成可放心開工的計畫。
