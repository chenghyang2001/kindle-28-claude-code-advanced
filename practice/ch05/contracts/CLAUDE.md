# Agent 邊界合約（Phase 2 多代理分工）

所有子代理開工前必讀本檔與 `contracts/spec.md`。違反任一條 = 該輪作廢。

| 角色 | 可寫 | Never modifies |
| --- | --- | --- |
| 指揮者（主） | `contracts/`、`PHASES.md`、`signals/` 檢查、整合 | 不寫 `src/` 業務邏輯 |
| Researcher | `docs/research.md`、`signals/DONE.md` | `src/`、`tests/`、`contracts/` |
| Builder | `src/pricing.py`、`tests/test_pricing.py`、`signals/BUILD_COMPLETE.md` | `tests/snapshot.json`、`tests/cases.py`、`src/legacy_order.py`、`contracts/` |
| Reviewer | `reviews/REVIEW.md`、`signals/REVIEW_COMPLETE.md` | `src/`、`tests/`、`contracts/` |

## 信號檔協定
- 前一個信號檔存在才可開工：Researcher → `DONE.md` → Builder → `BUILD_COMPLETE.md` → Reviewer → `REVIEW_COMPLETE.md`
- 每個信號檔必含三段：`## Deliverables`、`## Next Steps`、`## Open Questions`
- `REVIEW_COMPLETE.md` 必須寫一行 `MUST_FIX: <數字>`

## 衝突處理
- 發現合約有錯 → 寫進自己信號檔的 Open Questions，**不自己改合約**，由指揮者裁決。
- 越權檢查：指揮者在每個 agent 完成後 commit，並用 `scripts/check_boundaries.sh` 對 git diff 檢查寫入路徑。
