# 練習 01 解答 — 依任務選對 model 控成本

> 本解答的數字全部來自實跑：`scripts/ex01-model-cost.sh` 對 3 種任務 × 3 個 model 各跑一次
> `claude -p --output-format json --setting-sources project,local`（已清掉 `CLAUDE*` 環境變數），
> 再用 `scripts/ex01-cost-table.py` 從 JSON 取 `total_cost_usd` 與 `duration_ms`。原始 JSON 在 `results/ex01/`。
> 實跑日期：2026-10-18。`haiku / sonnet / opus` 別名實際對應 `claude-haiku-5-5 / claude-sonnet-5-5 / claude-opus-5-5`。

## 三個測試任務

| 任務 | prompt（刻意短） |
| --- | --- |
| format（格式化） | 把 `name=Amy age=30 city=Taipei` 轉成 JSON |
| analysis（分析） | 看 `data/sales.csv`（6 列營收），用兩句話說各區趨勢 |
| reasoning（推理） | 經典「三個盒子標籤全貼錯」題，用 3 句內說明解法 |

## 實測成本表

| 任務 | model | total_cost_usd | duration_ms | 輸出 tokens | 相對 Haiku | 答案品質 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| format | haiku | 0.00276 | 2530 | 215 | 1.0x | ✅ 正確 |
| format | sonnet | 0.04855 | 1720 | 27 | 17.6x | ✅ 正確（且沒包 code fence，最乾淨） |
| format | opus | 0.09724 | 2105 | 41 | 35.2x | ✅ 正確 |
| analysis | haiku | 0.00227 | 2192 | 202 | 1.0x | ✅ 趨勢正確 |
| analysis | sonnet | 0.04245 | 2591 | 98 | 18.7x | ✅ 正確，多點出「9 月成長趨緩」 |
| analysis | opus | 0.08701 | 4890 | 210 | 38.3x | ✅ 最深入：指出兩區總和持平＝營收轉移 |
| reasoning | haiku | 0.00237 | 3200 | 397 | 1.0x | ❌ **答錯**：說標「蘋果」的盒子是混合，違反「標籤全錯」 |
| reasoning | sonnet | 0.04324 | 2754 | 183 | 18.3x | ✅ 正確 |
| reasoning | opus | 0.08718 | 4593 | 224 | 36.8x | ✅ 正確，步驟最清楚 |

（含 cache tokens 的完整表在 `results/ex01/cost-table.md`）

## 任務 1：三種任務各選一個最划算的 model

| 任務 | 選擇 | 理由（附實測證據） |
| --- | --- | --- |
| 格式化 / 摘要 / 通知 | **Haiku** | 三個 model 輸出一樣正確，Haiku 只要 Sonnet 的 1/18、Opus 的 1/35。這類任務沒有「更聰明」的空間，多付錢買不到東西。 |
| 分析 / 程式碼生成 | **Sonnet** | Haiku 答案也對，但 Sonnet 多抓到「成長趨緩」這種第二層訊息。一般分析用 Sonnet 是品質與價格的平衡點；如果只是很機械的資料統計，Haiku 也夠。Opus 洞察最深，但多付一倍只在需要「換個角度看」時才划算。 |
| 複雜推理 / 架構 | **Sonnet 起步，關鍵決策才上 Opus** | 這次最重要的發現：**Haiku 在推理題答錯**。省下 0.04 美元換來錯誤答案，後續修正的成本遠大於差價，所以推理題不能用 Haiku。Sonnet 這題就答對了；Opus 留給「答錯代價很高」的情境（架構決策、跨模組重構、安全設計）。 |

## 任務 2：相對成本量級

實測比例（三個任務很一致）：

```text
Haiku : Sonnet : Opus  ≈  1 : 18 : 37
```

- 單次呼叫：Haiku ≈ 0.002～0.003 美元、Sonnet ≈ 0.04～0.05、Opus ≈ 0.09～0.10。
- 量級：Haiku → Sonnet 約 **一個數量級（×18）**，Sonnet → Opus 約 **×2**。
- 換算：同一筆預算，Opus 跑 1 次 ≈ Sonnet 2 次 ≈ Haiku 35 次以上。

### 為什麼實測比例比官方價目表的差距還大？

`claude -p` 的提示很短，但每次呼叫都帶著約 **2.8 萬 token 的 Claude Code 系統提示與工具定義**
（`cache_creation ≈ 1 萬` + `cache_read ≈ 1.7～1.9 萬`）。也就是說，成本主要花在「固定開銷」，
不是 prompt 本身，而這部分按各 model 的輸入單價計費，所以單價差距幾乎原封不動反映在總成本上。
實務含意：

1. 小任務批次化：把 10 個格式化工作合成一次呼叫，固定開銷只付一次。
2. 純 API 腳本（不需工具）直接打 Messages API，可省掉這 2.8 萬 token 的系統提示。

### 速度

`duration_ms` 在 1.7～4.9 秒之間，Opus 在需要多寫字的任務明顯較慢（約 4.6～4.9 秒）。
這組樣本只跑一次，速度差異有網路波動成分，成本比例則很穩定（三任務都落在 1 : 18 : 35～38）。

## 驗收

- [x] 三任務各有 model 選擇 + 理由（含實測品質證據）
- [x] 有相對成本的量級比較（實測 1 : 18 : 37）
