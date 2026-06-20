# 練習 03 解答 — 完整編排一個較大任務

## 編排四要素（以「為服務新增一組 API」為例）

### Phases（分階段，信號檔推進）
```text
Phase 0：主 agent 產合約 contracts/api-spec.yaml（含 Never modifies 條款）
Phase 1：Builder 依合約實作 src/ -> 寫 signals/BUILD_COMPLETE.md
Phase 2：主 agent 見旗 -> 派 Reviewer 審查 -> 寫 signals/REVIEW_COMPLETE.md
Phase 3：主 agent 整合 -> 產 MANIFEST.md
```

### Agent 分工
| Agent | 角色 | 讀寫邊界 |
|-------|------|---------|
| 主 agent（指揮官） | 派工/監控信號檔/整合 | 不下場寫業務碼 |
| Builder（工人） | 實作 | 可寫 src/ |
| Reviewer | 審查 | 唯讀 |

### 信號檔（signal file）
多 agent 不能直接對話，用約定檔案的存在當「完工旗子」協調步調（像接力棒/紅綠燈）：
`BUILD_COMPLETE.md` → 推進到審查；`REVIEW_COMPLETE.md` → 推進到整合。

## 限制條件達成

### 1. 指揮者/工人職責分離
主 agent 只調度不實作，維持綜觀全局 + 整合中立。

### 2. 合約 Never modifies
一開始訂合約釘死共同介面 + 邊界，讓多 agent 不溝通也不打架；地基不准動，否則照地基做的全崩。沒合約 → 介面各自解讀、檔案互踩、兜不攏。

### 3. 越權偵測（如 Reviewer 改了 src/）
- 危險一：破壞讀寫邊界（違反合約、秩序破）。
- 危險二（更致命）：破壞審查中立——Reviewer 一改 src 就從審查者變作者，再審會偏袒自己，掉回自我審查盲點，等於失去當初請它的唯一理由。
- 處置：退掉越權改動 + 拉回角色 + 修復 prompt 提醒「只能審查不能改」。

## 關鍵收穫
- 大任務編排＝phases + 分工 + 信號檔 + 整合，靠合約與邊界防亂。
- agent 編排核心是「用結構管理一群不完美個體」：乾淨 context、合約、信號檔、對抗驗證、職責分離。
