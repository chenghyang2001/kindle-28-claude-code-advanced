# k28-ch05-practice — GSD 階段化 + 多代理重構演練

把亂寫的 `src/legacy_order.py` 重構成 `src/pricing.py`，用 `PHASES.md` 的四個階段與 gate 控管，Phase 2 由 Researcher／Builder／Reviewer 三個子代理以信號檔接力。

## 結構
- `src/pricing.py`：重構後的計價模組（subtotal / discount / shipping / tax / calculate）
- `src/legacy_order.py`：相容層，`calc()` 委派給 `pricing.calculate`
- `contracts/`：規格（spec.md）與 agent 邊界（CLAUDE.md）
- `signals/`：DONE / BUILD_COMPLETE / REVIEW_COMPLETE 信號檔
- `docs/research.md`、`reviews/REVIEW.md`：Researcher、Reviewer 產出
- `scripts/check_gate.py`：gate 檢查；`scripts/check_boundaries.sh`：越權檢查
- `logs/`：gate 與越權檢查的實際輸出

## 使用
```bash
PYTHONUTF8=1 python -m unittest discover tests -v
PYTHONUTF8=1 python scripts/check_gate.py 3
bash scripts/check_boundaries.sh reviewer <base> <head>
```
