# 開發計畫 v3：使用者認證系統（OAuth 登入）

> 產出者：Session A（規劃者）。狀態：**第三版，回應 Session B 第二輪審查**。
> 本版清掉 2 個 🔴（R1/R2），吸收 6 個 🟡/🟢（R3-R8），並把產品決策（R3/R9）移入「待業主確認」而非無限重畫。

## 變更摘要（相對 v2）

| 審查發現 | 嚴重 | 處置 | 章節 |
|---|---|---|---|
| R1 帳號合併未驗 email_verified（劫持） | 🔴 | 接受 → 只在 verified 才自動合併 | §2 |
| R2 Redis SPOF + 無降級策略 | 🔴 | 接受 → 明訂降級＋HA＋風險章 | §4, §10 |
| R3 refresh 無絕對上限（24h 語意） | 🟡 | 接受 → 設 24h 絕對上限 + 列待確認 | §5, §11 |
| R4 refresh 無輪替/重用偵測 | 🟡 | 接受 → rotation + reuse detection | §5 |
| R5 每請求查 DB 比對 version | 🟡 | 接受 → token_version 快取 Redis | §5 |
| R6 pre-auth 無帳號可當 key | 🟡 | 接受 → 分層 pre/post-auth 限流 | §3 |
| R7 破壞性 down 會刪資料 | 🟢 | 接受 → 上線後 forward-only | §6 |
| R8 state cookie SameSite=Strict 會擋掉 | 🟢 | 接受 → state 用 Lax | §3 |
| R9 全域登出踢所有裝置 | 🟢 | 列待業主確認（per-session？） | §11 |

---

## 1. 技術選型（同 v2，補強）

- Next.js 16 / PostgreSQL / **Redis（高可用：哨兵或叢集）** / Playwright
- Token：access 15 分 + refresh（**輪替制**），皆 httpOnly cookie

## 2. 帳號合併（修 R1 劫持）

找/建/連結身分時：

1. 以 `(provider, provider_account_id)` 找 identity → 找到就用。
2. 找不到、且 provider 回傳的 email **已驗證** → 才自動連結到同 email 的既有 user。
   - Google：檢查 `email_verified` claim 為 true。
   - GitHub：呼叫 `/user/emails`，**只取 `primary && verified` 的 email**。
3. email **未驗證 / 為 null** → **不自動合併**。建獨立 user，或導向「請先登入原帳號再綁定此 provider」流程。

> 為什麼：未驗證 email 可被攻擊者偽填成受害者 email；自動合併＝把攻擊者身分掛到受害者帳號（account-linking 劫持）。verified 才是可信的合併鍵。

## 3. 登入流程（修 R6/R8）

- state cookie 用 **`SameSite=Lax`**（top-level GET 導回會帶上）；access/refresh cookie 維持較嚴格設定。 **R8**
- 限流分層 **R6**：
  - **pre-auth 端點**（發起 / callback）：用 `IP + 內網白名單 + state/cookie 指紋`（此時還不知道使用者是誰）。
  - **post-auth 端點**（refresh）：用帳號粒度。
  - 文件明講：pre-auth 仍以 IP 為主，NAT 風險用內網白名單緩解，不假裝「帳號為主」能涵蓋 pre-auth。

## 4. Redis 降級與 SPOF（修 R2）

明確定義 Redis 不可用時的行為：

| 用途 | Redis 不可用時 | 理由 |
|---|---|---|
| OAuth state / 登入 | **回友善錯誤頁 + 告警**（不放行無 state 登入） | 安全 > 可用；同「第三方失效要友善錯誤」精神 |
| Rate limit | **fail-closed**，但**已登入流量（持有效 cookie）放行** | 避免限流失效被打爆，又不癱瘓既有使用者 |
| token_version 快取 | 回退讀 DB（降級但可用） | 正確性優先 |

- Redis 採 **高可用部署**（哨兵 / 叢集）。
- **§10 風險章明列「Redis 是新 SPOF」** + 監控告警。

## 5. Token 撤銷（修 R3/R4/R5）

- **R5 效能**：`token_version` **快取在 Redis**，熱路徑驗證讀 Redis 不打 DB（暴衝時 DB 不先倒）；登出時同步更新 Redis + DB。
- **R4 輪替**：refresh **每次使用即輪替**（發新、舊立即失效）；偵測到「已用過的 refresh 被重用」→ 視為被竊，撤銷整條 token family（version += 1）。
- **R3 絕對上限**：refresh 設 **24h 絕對上限**（達上限強制重新登入），對齊需求「24 小時過期」語意。（最終語意待 §11 業主確認）

## 6. Migration（修 R7）

- 早期（尚未上正式資料）migration：down 可 DROP。
- **上線後採 forward-only**：不寫破壞性 down，變更用「補償 migration」前滾，避免 rollback 把使用者資料刪光（回滾結構 ≠ 回滾資料）。

## 7-9.（同 v2：任務拆解、測試、密鑰管理，略）

測試 §8 追加：

- ✅ 未驗證 email 不會被自動合併（R1 回歸測試）
- ✅ Redis 不可用 → 登入回友善錯誤、rate limit fail-closed（R2）
- ✅ refresh 重用偵測 → 整條 family 撤銷（R4）

## 10. 風險登錄（新增）

- **Redis 為新 SPOF**：以 HA + 降級策略 + 告警緩解（見 §4）。
- account-linking：僅信 verified email（見 §2）。

## 11. 待業主確認（Open Questions — 不阻擋實作）

> 這些是**產品決策**，非工程瑕疵。記錄於此，不再為它們重畫計畫。

1. **R3**：「24 小時過期」指 access 還是整體 session？v3 暫定 refresh 24h 絕對上限，待確認。
2. **R9**：登出要「單裝置」還是「全裝置」？v3 暫採全域（token_version），若要單裝置改 per-session（refresh family）。

## 12. 完成定義（DoD）

- §8 全測試綠（含 R1/R2/R4 回歸）。
- 🔴 = 0；🟡 已處理或列入 §11。
- Redis HA + 降級策略實測。
- 無密鑰進版控；migration 在乾淨 DB 可前滾。
