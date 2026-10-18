# NOTES — 第 5 章演練紀錄（快速 demo 模式）

## 做了什麼
1. 自建題目專案：`src/legacy_order.py`（30 行亂寫的計價函式）＋ 10 筆特徵測試案例與 snapshot。
2. 練習 01：寫 `PHASES.md`（Phase 0–3 + gate）與 `scripts/check_gate.py`，Phase 0–1 實際走完並跑 gate（後來 Phase 2–3 也走完）。
3. 練習 02：用 Agent 工具依序派 Researcher → Builder → Reviewer 三個子代理，靠 `signals/DONE.md` → `BUILD_COMPLETE.md` → `REVIEW_COMPLETE.md` 推進；每個 agent 完成後獨立 commit，用 `scripts/check_boundaries.sh` 檢查 git diff。
4. Phase 3 整合：`legacy_order.calc` 改為委派給 `pricing.calculate`，補 README。

## 驗證結果
- gate 0／1／2／3 全 PASS（`logs/gates-final.txt`）。
- 全部測試 27 個綠（2 特徵 + 25 pricing）。Reviewer 另跑 20,000 筆隨機訂單比對舊版，差異 0。
- 越權檢查：三個角色都只動到白名單檔；Researcher、Reviewer 對 `src/` 0 次修改。
- 反向測試（證明檢查有效）：
  - spec 改成 `Status: DRAFT` → gate 0 FAIL
  - Phase 1 前 pricing.py 不存在 → gate 1 FAIL；Phase 2 前 → gate 2 五項 FAIL
  - 把 VIP 折扣改成 int → gate 2「snapshot 逐筆一致」FAIL（抓到型別漂移）
  - 暫存分支模擬 Reviewer 改 src → `check_boundaries.sh` exit 1

## 和題目要求的差異 / 注意事項
- 題目只要求寫文件；這裡額外把 gate 與越權都做成可執行腳本並實跑。
- 指揮者在裁決 Open Questions 時改了 `src/pricing.py` 骨架的**型別註記**（`float` → `int | float`），屬介面合約、不是業務邏輯，但嚴格說不是 Builder 改的。Phase 3 的 `legacy_order.py` 委派（2 行）也由指揮者做，屬整合工作。
- gate 2 的型別比對原本跟 legacy 比，Phase 3 後 legacy 委派給 pricing 會變成自己比自己，已改成跟 `snapshot.json` 比。同理，`tests/test_pricing.py` 裡「與 legacy_order.calc 比對」的測試在 Phase 3 後也變成同義反覆，行為仍由 snapshot 鎖住；之後可移除或改比 snapshot。
- Builder／Reviewer 提出的 NICE_TO_HAVE（`discount` 參數改名、`shipping/tax` 註記改 `int | float`、加固定種子隨機測試）未處理，留作下一輪。
- GSD 已全域安裝，但沒有跑 `/gsd-*` 指令，phases/gate 是手寫在 PHASES.md（題目允許）。
- 沒有用到外部帳號、token、MCP、plugin；未建 GitHub repo、未 push。
- 快速模式：未走三 agent QA/審查流程（本專案 CLAUDE.md 豁免）。
