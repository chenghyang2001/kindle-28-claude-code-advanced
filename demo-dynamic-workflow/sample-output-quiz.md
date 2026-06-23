# hello-dynamic-workflow 實跑產出（範例）

> 這是 2026-06-23 用 `Workflow` 工具實跑 `hello-dynamic-workflow` 的真實產出。
> Run ID：`wf_7145d1d4-15e`｜4 個 agent（3 出題 + 1 彙整）｜約 64 秒。

---

## Claude Code 進階 — 隨堂測驗卷

### 題目

#### 第 1 題（難度：中等）— 主題：Skills

在 Claude Code 中，一個 Skill 的 SKILL.md 開頭 YAML frontmatter 裡的 `description` 欄位，最主要的作用是什麼？（單選）

- A. 決定這個 Skill 在檔案系統中的資料夾名稱
- B. 提供給 Claude 判斷「何時該自動觸發載入這個 Skill」的依據
- C. 設定這個 Skill 執行時可以使用哪些工具權限
- D. 指定這個 Skill 產出的檔案要存放的路徑

#### 第 2 題（難度：簡單）— 主題：Subagents

使用 Subagent 執行任務時，關於它的「上下文視窗」，下列何者正確？

- A. 與主對話共用同一個 context，所有訊息互通
- B. 擁有獨立、乾淨的 context，只把最終結果回傳給主代理
- C. 完全沒有 context，無法讀取任何檔案
- D. 會把讀過的所有原始內容全部塞回主代理的 context

#### 第 3 題（難度：中等）— 主題：Dynamic Workflows

在 Dynamic Workflow 中，`pipeline()` 與「一批批的 `parallel()`」最關鍵的差別是什麼？為什麼 `pipeline()` 被當成多階段任務的預設首選？

---

### 解答

**第 1 題：B。** Skill 是「模型自己決定要不要用」（model-invoked），Claude 靠 `description` 跟你的需求比對來決定觸發時機，所以 description 是「觸發說明書」，常明列觸發詞與「不觸發」情境。（A 由 `name`／目錄決定；C 是另外的權限設定；D 由 Skill 內容邏輯處理。）

**第 2 題：B。** Subagent 核心價值是 context 隔離：在自己乾淨的 context 跑，不被主對話污染、也不把中間原始內容回灌主代理，只回傳精煉結論。所以吞 token 的探索／log 查詢特別適合丟給它（可搭 haiku 省成本）。

**第 3 題：** 關鍵是「有沒有階段間的等待牆」。`parallel()` 是同步牆——等整批回來才能往下，快的得空等最慢的。`pipeline()` 讓每個 item 各自走完所有階段、無等待牆——item A 在 Verify 時 item B 還能在 Generate，不被最慢項目卡住整批，吞吐更高，故為預設首選；`parallel()` 適合「同階段要全部到齊才彙整」的同步點場景。
