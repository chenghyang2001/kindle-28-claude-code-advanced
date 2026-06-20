# STEP_LOG — [09] 官方外掛

> 記錄本課的學習過程、卡關與突破。完成後重要踩坑彙整到 `docs/踩坑紀錄.md`。

## 學習日期
- 2026-06-21

## 我做了什麼
1. 互動問答完成三題：
   - 基礎：理解 `/code-review` 用途（只找問題不動手）、適用/不適用時機、輸出三類分法。
   - 進階：把 review → simplify 串成固定流程，定義「必改歸零」為硬 gate。
   - 綜合：用 feature-dev / code-review / simplify 做「分階段不重疊」決策表，含反例欄。
2. 解答寫入 `answer/ex01~03-answer.md`。

## 卡關與解法
- 卡關：review 和 simplify 該誰先誰後、之間卡什麼條件。
- 根本原因：沒分清「正確性」與「可讀性」的優先級。
- 解法：先弄對再弄漂亮——先 code-review、必改項歸零後才 simplify；simplify 會動手改，在有 bug 時叫它會把 bug 藏更深。

## 關鍵收穫（3 句以內）
- code-review 只找問題不代筆；simplify 會動手改——職責分清才不會搶改同一段。
- 串接的硬 gate 是「必改項歸零」，建議/備註只是參考。
- 選外掛看「功能人生階段」：feature-dev 開頭、code-review 中間、simplify 收尾，各守一段。

## 自評
- 基礎練習：✅ 完成
- 進階練習：✅ 完成
- 綜合挑戰：✅ 完成
