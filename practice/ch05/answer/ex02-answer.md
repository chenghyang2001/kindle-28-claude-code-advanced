# 練習 02 解答 — 在 Phase 2 引入 multi-agent 分工

## 任務 1：分工與資料流
選 Phase 2（實作）。主 Claude 當指揮者，用 Agent 工具**依序**派三個子代理，靠 `signals/` 的信號檔推進。

```text
指揮者（主 Claude）
  │ 產合約 contracts/spec.md + contracts/CLAUDE.md，每個 agent 完成後 commit + 越權檢查
  ▼
Researcher ── 讀 src/legacy_order.py、spec、snapshot（可執行舊函式驗證）
  │ 寫 docs/research.md（分支對照、14 個常數名、14 條陷阱、7 筆額外案例）
  │ 寫 signals/DONE.md ──► 指揮者讀 Open Questions，裁決 4 題並更新 spec / gate
  ▼
Builder ── 讀 spec、research.md、DONE.md
  │ 寫 src/pricing.py、tests/test_pricing.py（25 測試）
  │ 寫 signals/BUILD_COMPLETE.md
  ▼
Reviewer ── 讀全部 + 跑測試 + 20,000 筆隨機比對舊版
  │ 寫 reviews/REVIEW.md
  │ 寫 signals/REVIEW_COMPLETE.md（MUST_FIX: 0）
  ▼
指揮者跑 check_gate.py 2 → PASS → 進 Phase 3
```

| 角色 | 讀 | 寫（唯一允許） | 交付物 |
| --- | --- | --- | --- |
| Researcher | src、tests、contracts | `docs/research.md`、`signals/DONE.md` | 行為/相依地圖 |
| Builder | 上述 + research | `src/pricing.py`、`tests/test_pricing.py`、`signals/BUILD_COMPLETE.md` | 實作＋測試 |
| Reviewer | 全部 | `reviews/REVIEW.md`、`signals/REVIEW_COMPLETE.md` | 審查報告 |

## 任務 2：避免越權/衝突的機制
1. **邊界合約**：`contracts/CLAUDE.md` 用表格寫每個角色的可寫清單與 Never modifies；每個子代理的 prompt 也重複一次硬性限制。
2. **信號檔協定**：前一個信號檔存在才開工；每個信號檔必含三段（Deliverables / Next Steps / Open Questions）；gate 2 自動檢查三段完整。
3. **合約問題不自己改**：Researcher 提出 4 題、Builder 提出 3 題，都只寫進 Open Questions，由指揮者裁決（裁決寫在 spec 底部）。
4. **事後稽核**：每個 agent 完成後指揮者獨立 commit，再跑 `scripts/check_boundaries.sh <role> <base> <head>`，比對 `git diff --name-only` 是否都在白名單內。
5. **序列執行**：三個 agent 不平行，避免同時寫檔。

### 實際驗證（`logs/gates-final.txt`）
- Researcher `8e6e24a..c3ad51d`：只動 `docs/research.md`、`signals/DONE.md` → OK
- Builder `0e5309f..2ecc848`：只動 `src/pricing.py`、`tests/test_pricing.py`、`signals/BUILD_COMPLETE.md` → OK
- Reviewer `2ecc848..beedfff`：只動 `reviews/REVIEW.md`、`signals/REVIEW_COMPLETE.md` → OK
- `git log -- src/` 在 Phase 2 期間只有 Builder commit 與指揮者的合約 commit（只改型別註記）碰過 src/，Researcher、Reviewer 0 次。
- 反向測試：在暫存分支模擬 Reviewer 改 `src/pricing.py` → 腳本回報「越權！」exit 1（分支已刪）。

## 延伸思考：GSD 階段化 vs 單純 todo list
| | todo list | GSD 階段 + gate |
| --- | --- | --- |
| 順序 | 任意勾 | 前一 gate 沒過不能進下一階段 |
| 完成定義 | 主觀打勾 | 腳本判定（測試、檔案、字串） |
| 回退偵測 | 無 | 每個 gate 重跑前面的 gate |
| 多代理 | 難控邊界 | 合約 + 信號檔 + diff 稽核 |

**值得用**：會跑好幾個小時或跨 session 的工作、多個 agent 協作、行為不能變的重構、改錯代價高（金額、資料遷移）。
**不值得用**：改 typo、單檔小修、一次性腳本、探索性原型——寫合約和 gate 的成本會比工作本身還高。這次 30 行的模組其實偏小，用這套流程是為了演練；真實專案大約到「多檔、多天、多人/多 agent」才划算。
