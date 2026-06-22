# 開發計畫 v2：使用者認證系統（OAuth 登入）

> 產出者：Session A（規劃者）。狀態：**修訂版，回應 Session B 審查**。
> 本版逐條回應審查員的 7 個 🔴 與 3 個 🟡＋1 個加分發現，全數接受。

## 變更摘要（相對 v1）

| 審查發現 | 處置 | 對應章節 |
|---|---|---|
| [01] 密鑰寫死 | 接受 → 移環境變數 + 啟動檢查 | §6 |
| [02] rate limit 記憶體 | 接受 → Redis 共享 | §4 |
| [03] rate limit 純 IP | 接受 → 帳號粒度 + 內網白名單 | §4 |
| [04] 同 email 不合併 | 接受 → 拆 users / identities 兩表 | §2 |
| [05] 假登出 | 接受 → token_version 撤銷 | §5 |
| [06] OAuth 缺 state | 接受 → state + PKCE + redirect_uri 白名單 | §3 |
| [07] 手動 CREATE TABLE | 接受 → migration（up/down） | §2 |
| [08] localStorage | 接受 → httpOnly cookie | §3 |
| [09] provider 失效 | 接受 → timeout/重試/友善錯誤 | §3 |
| [10] 任務排序 | 接受 → 抽 T0 合約層 | §7 |
| [11] 測試只 happy path | 接受 → 補失敗/邊緣案例 | §8 |
| [12] null email（加分） | 接受 → identities 以 provider_account_id 為主鍵 | §2,§3 |

## 1. 技術選型

- 框架：Next.js 16 App Router（既有）
- DB：PostgreSQL（既有）+ **migration 工具**（node-pg-migrate / Drizzle，含 up/down）
- 共享狀態：**Redis**（rate limit、state 暫存、token 撤銷）
- Token：access token（短命，15 分）+ refresh token（長命，存 httpOnly cookie）
- 測試：Playwright（happy + 失敗 + 邊緣）

> 為什麼加 Redis：需求要求多實例水平擴展，rate limit / OAuth state / 登出撤銷都需要跨副本共享狀態，記憶體做不到。

## 2. 資料庫設計（含 rollback）

**不手動執行 DDL**，改用 migration（每個變更含 up + down，先在測試環境驗證，CI 套用）。

拆兩表，讓「一個 user 可掛多個 provider 身分」：

```
users(id, email UNIQUE NULLABLE, display_name, avatar_url, token_version INT DEFAULT 0, created_at)
identities(id, user_id FK, provider, provider_account_id, email, PRIMARY/UNIQUE(provider, provider_account_id))
```

- **[04] 帳號合併**：登入時以 `(provider, provider_account_id)` 找 identity；找不到時，若有 email 就找同 email 的 user 連結，否則建新 user。email 設 UNIQUE（NULLABLE）。
- **[12] null email**：identity 主鍵用 `provider_account_id` 而非 email；email 可為 null，合併邏輯以 account_id 為準。
- **rollback**：每個 migration 附 down（drop / 還原），失敗即回滾。

## 3. 登入流程（含安全與失敗處理）

1. 點登入 → 後端產生隨機 `state` + PKCE `code_verifier`，存 Redis（短 TTL，綁 session）→ 導向 provider。
2. callback：**先驗 `state`**（不符直接拒）、驗 `redirect_uri` 白名單。 **[06]**
3. 用 `code` + PKCE 換 token（**timeout + 重試**；provider 非 200 / 逾時 → 導友善錯誤頁；`error=access_denied` → 「您取消了登入」）。 **[09]**
4. 取 provider 使用者資料（含 account_id；GitHub email 可能 null → 走 `/user/emails` 備援或留 null）。 **[12]**
5. 依 §2 邏輯找/建/連結帳號。
6. 簽 **短命 access token**（15 分，內含 `jti` + `token_version`）+ 發 **refresh token**；兩者放 **httpOnly + Secure + SameSite cookie**，前端不碰 token。 **[08]**

## 4. 頻率限制（Redis + 帳號粒度）

- 用 **Redis `INCR` + TTL** 做計數，跨副本共享、重啟不歸零。 **[02]**
- key 粒度：**OAuth 嘗試識別 / 帳號** 為主，IP 為輔；內網測試 IP 走白名單較高閾值，避免 NAT 誤殺。 **[03]**
- 套用到 **所有** auth 端點（Google + GitHub + refresh），不只 Google。

## 5. 登出（真正失效）

- 維護 `users.token_version`；access token 內嵌簽發當下的 version。
- 每次驗 token 比對 version，不符即拒。
- **登出 = token_version += 1**（撤銷所有舊 token）+ 清 cookie；被竊 token 立即失效。 **[05]**
- refresh token 一併從 Redis 撤銷。

## 6. 密鑰管理

- 所有 secret（OAuth client secret、JWT signing key）放 **環境變數 / secret manager**。 **[01]**
- 啟動時檢查必要 env 缺漏，缺則 fail-fast。
- `.env` 進 `.gitignore`，提供 `.env.example`（不含真值）。

## 7. 任務拆解與排程（修正依賴）

| # | 任務 | 依賴 | 平行 |
|---|---|---|---|
| **T0** | **OAuth 共用抽象 + API 合約 + DB migration 骨架** | — | |
| T1 | Redis 接入（rate limit / state / 撤銷） | T0 | ✅ |
| T2 | Google OAuth callback | T0 | ✅ 與 T3 |
| T3 | GitHub OAuth callback | T0 | ✅ 與 T2 |
| T4 | 前端登入頁（依 T0 合約，可先 mock） | T0 | ✅ |
| T5 | token 簽發/撤銷/refresh | T0,T1 | |
| T6 | rate limit 套所有 auth 端點 | T1,T2,T3 | |
| T7 | Playwright 測試（隨功能同步） | 各功能 | |

> [10] 修正：GitHub 不再依賴 Google（共用 T0 抽象）；前端依合約先行不返工；測試不集中最後。

## 8. 測試計畫（happy + 失敗 + 邊緣）

- ✅ Google / GitHub 各自成功登入
- ✅ 同 email 跨 provider → 合併成同一帳號（[04]）
- ✅ GitHub 私密 email（null）→ 不崩、走備援（[12]）
- ✅ rate limit 觸發 429（多副本下仍有效）
- ✅ access token 過期被拒 / refresh 續期成功
- ✅ 登出後舊 token 立即被拒（[05]）
- ✅ 缺 state / state 不符 → callback 被拒（[06]）
- ✅ provider 逾時 / access_denied → 友善錯誤頁（[09]）

## 9. 完成定義（DoD）

- 上述 §8 測試**全綠**（不只 happy path）。
- 無密鑰進版控；啟動 env 檢查通過。
- migration 可在乾淨 DB up + down 來回無誤。
- 多副本部署下 rate limit 與登出撤銷實測有效。
