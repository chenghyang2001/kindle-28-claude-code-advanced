# 審查 agent 交付物：必改/建議清單
（主 agent 原文摘要存檔；審查 agent 本身未寫任何檔，也沒有產生 .pyc）

## 必改（MUST_FIX）
1. `sorted_items()` 遇到 priority 為 None 或字串時會 TypeError 當掉（`add()` 沒有驗證 priority）。
   - 重現：`items=[{'id':1,'priority':None,...},{'id':2,'priority':1,...}]` → `sorted_items()` → `TypeError: '<' not supported between 'int' and 'NoneType'`
   - 建議：加 `_parse_priority`，None 當成 3，非 int 拋 ValueError，並補測試。

## 建議（NICE_TO_HAVE）
1. 已完成項目的 due 格式壞掉時，overdue 也會整個失敗（比合約嚴格，應寫明是刻意的）。
2. Python 3.11+ 的 `date.fromisoformat` 接受 `"20261001"`，與合約的 YYYY-MM-DD 不一致 → 可改用 strptime。
3. `due=""` 會拋 ValueError，建議補測試固定行為。
4. 缺少 `done`/`id` 欄位時的 KeyError 看不出是哪一筆。
5. overdue 依 id 排序應寫進合約或 docstring。

## 合約符合度
任務 1 全部 ✅；任務 2「priority 小者優先」❌（有會當掉的輸入），其餘 ✅。樣本結果 [1, 4, 2, 3] 正確，主 agent 的裁決成立。

## 總結：CHANGES_REQUESTED（1 條必改）
→ 必改項目的修法有爭議，交給練習 02 的 agent debate 裁決（見 reports/04-debate.md）。
