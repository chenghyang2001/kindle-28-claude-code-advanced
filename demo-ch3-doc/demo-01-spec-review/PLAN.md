# 開發計畫：使用者認證系統（OAuth 登入）

> 產出者：Session A（規劃者）。狀態：**初稿，待審查**。
> ⚠️ 本計畫供練習用，表面專業但藏有多處問題——這正是審查員要找出來的。

## 1. 技術選型

- 框架：Next.js 16 App Router（既有專案）
- 資料庫：PostgreSQL（既有）
- OAuth：直接呼叫 Google / GitHub 的 OAuth 2.0 endpoint
- Token：使用 `jsonwebtoken` 簽發 JWT，演算法 HS256
- 測試：Playwright

## 2. 資料庫設計

新增 `users` 資料表：

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL,
  display_name VARCHAR(255),
  avatar_url TEXT,
  provider VARCHAR(50) NOT NULL,   -- 'google' 或 'github'
  created_at TIMESTAMP DEFAULT NOW()
);
```

> 直接在正式資料庫執行上述 `CREATE TABLE` 即可。

## 3. 登入流程

1. 使用者點「用 Google 登入」→ 導向 Google 授權頁。
2. Google 導回 `/api/auth/callback/google?code=...`。
3. 後端拿 `code` 換 access token，再向 Google 取使用者資料。
4. 用 email 在 `users` 找/建立使用者。
5. 簽一個 JWT（24 小時過期），回傳給前端。
6. 前端把 JWT 存進 `localStorage`，之後每個 API 請求帶在 header。

GitHub 流程同上，把 provider 換成 github。

## 4. 頻率限制

- 在登入端點加一個計數器：同一個 **IP** 每分鐘超過 5 次就回 429。
- 計數器用一個 JavaScript 物件存在伺服器記憶體裡（`const counts = {}`）。

## 5. 登出

- 前端把 `localStorage` 裡的 JWT 刪掉即可，使用者就登出了。

## 6. 密鑰

- Google / GitHub 的 client secret 與 JWT signing key 直接寫在 `auth.config.ts` 常數，方便部署。

## 7. 任務拆解與排程

| # | 任務 | 依賴 | 可平行 |
|---|---|---|---|
| T1 | 建 `users` 資料表 | — | |
| T2 | 實作 Google OAuth callback | T1 | ✅ 與 T3 平行 |
| T3 | 前端登入頁 + 串接 API | — | ✅ 與 T2 平行 |
| T4 | 實作 GitHub OAuth callback | T2 | |
| T5 | 加頻率限制 | T2 | |
| T6 | 寫 Playwright E2E 測試 | T2,T3,T4,T5 | |

## 8. 測試計畫

- Playwright 跑一條 happy path：點 Google 登入 → 成功導回 → 看到使用者名稱。
- 通過即視為完成。

## 9. 完成定義（Definition of Done）

- 能用 Google 和 GitHub 登入。
- JWT 24 小時過期。
- happy path E2E 測試綠燈。
