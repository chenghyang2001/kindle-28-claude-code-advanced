# REVIEW_COMPLETE — Reviewer

MUST_FIX: 0

## Deliverables

- `reviews/REVIEW.md`：逐條對照合約規則 1–7 和裁決 1–4，全部符合；MUST_FIX 0 項，NICE_TO_HAVE 5 項，並回覆 Builder 的 3 個 Open Questions。
- 驗證結果：unittest 27/27 OK；隨機比對 20,000 筆＋門檻邊界窮舉，跟 legacy 在值、key 順序、型別上 mismatch 都是 0；例外型別與訊息一致；Builder 邊界檢查 OK。
- 只寫入 `reviews/REVIEW.md` 和本檔，沒有修改 src/、tests/、contracts/，沒有 commit。

## Next Steps

1. 指揮者 commit 本輪產出，並執行 `bash scripts/check_boundaries.sh reviewer <base> HEAD` 與 `PYTHONUTF8=1 python scripts/check_gate.py 2`，確認 GATE 2 PASS。
2. 視需要把 NICE_TO_HAVE 3、4（隨機比對測試、門檻組合測試）排給 Builder 的後續 phase。

## Open Questions

1. 要不要把 `discount()` 的參數 `subtotal` 改名為 `amount`？這是公開介面變更，需要指揮者改合約（Reviewer 建議改，但不在本輪）。
2. 要不要把 `shipping` / `tax` 的參數註記統一成 `int | float`？Reviewer 建議同意，需要指揮者裁決後修改合約。
