# Claude Code 進階 — Claude Code 學習專案

## 專案說明

這是《Claude Code Advanced》(Javier Rayón, 2026) 的結構化學習課程，由 study-scaffold skill 自動生成。共 17 課，對應書本 6 部 + 附錄。

## 架構

- `demo/[NN-課程名]/` — 各課練習（基礎 → 進階 → 綜合）
- `demo/[NN]/answer/` — 本課解答（完成後填入）
- `demo/[NN]/starter/` — 來自上一課的 answer/（carry 自動攜帶；[01] 無）
- `docs/` — 踩坑紀錄等學習文件
- `skills/` — 學習過程中自製的 skill / script（選配）

## 攜帶機制

完成第 N 課後執行：`/study-scaffold carry N`
→ 自動把 `[N]/answer/` 複製到 `[N+1]/starter/`

## 來源

- 原始 PDF：`pdf/claude-code-advanced.pdf`（圖片型，722 頁）

## 互動式教學模式（重要，所有課程適用）

使用者要求以「互動問答」方式上每一課，規則如下：

1. **一次只貼一個問題**：開一課時，Claude 一次只丟出一個問題，然後**停下來等使用者回答**，不可一口氣把整課做完。
2. **使用者能答就答**：使用者若會，就自己回答；Claude 給回饋（對/不對、補充）。
3. **使用者答不出 → Claude 給答案 + 解析**：使用者明確說「你回答」或答不出來時，Claude 才提供答案，並**用對「職場新鮮人」講解的方式**做解析（白話、舉例、說明為什麼）。
4. **答完一題才進下一題 / 下一課**：逐題推進，問題與解答陸續寫入該課 `answer/` 與 `STEP_LOG.md`。
5. 此模式對**之後所有課程**都生效，直到使用者另行指示。
6. **🔴 未經同意不可執行指令（最重要）**：任何要跑的指令（Bash / git / python / 檔案寫入等），Claude **一律先把指令「貼出來」給使用者看，不可自動執行**。要等使用者明確說「執行」「跑吧」「do it」之類才動手。讓使用者主導節奏、過程中可以猜對猜錯，Claude 不替使用者把練習做完。
7. **示範（demo）也一樣**：要展示某段指令會做什麼，先貼指令 + 說明預期結果，等使用者同意才實跑驗證。

> 反模式 1：不要像第一課那樣由 Claude 一次把三個練習全做完。改成「貼問題 → 等回答 → 視情況給解析 → 下一題」。
> 反模式 2：不要未經同意就 Bash 執行指令/跑 demo（2026-06-20 踩到：未經同意就跑了 worktree demo）。先貼指令，等「執行」指令再跑。

## 🔊 每次回答自動語音播報（2026-06-20 使用者要求）

互動教學模式下，Claude **每次回答前**都要把該次回答用 `say_ui.exe` 念出來。流程「關舊開新 + 自動播放」：

1. 用 **Write 工具**把當次回答純文字寫進 `skills/_answer.txt`（UTF-8；可去掉 markdown 符號讓朗讀順）。
2. 關掉舊播放器（沒開也不報錯）：

   ```
   cmd.exe /c "taskkill /IM say_ui.exe /F"
   ```

3. 開新播放器、自動念（背景啟動、不阻塞）：

   ```
   cmd.exe /c start "" "skills\dist\say_ui.exe" --file "skills\_answer.txt" --autoplay
   ```

執行檔路徑（固定）：`skills/dist/say_ui.exe`。`--autoplay` 是 2026-06-20 為此需求加的（走 code-writer→QA→reviewer 三步 + 重打包）。

**授權與例外**：

- 上述「taskkill 舊的 + start 新的 + Write `_answer.txt`」三步，**使用者已長期授權，每回合自動執行，不需再逐次徵求同意**——這是「互動式教學模式」第 6/7 條（未經同意不可執行指令）的**唯一明文例外**。
- 其他所有課程指令（git / python 練習 / 其他檔案寫入）**仍照第 6/7 條**：先貼指令、等「執行」才跑。

**已知 caveat（reviewer 指出，非阻擋）**：

- `taskkill /F` 會繞過 `on_close`，每回合在 `%TEMP%` 留一個暫存 .mp3；量小、不主動清以免誤刪其他 mp3。
- `_answer.txt` 若為空或斷網，`say_ui` 會跳 modal 錯誤視窗——故 Write 時務必寫非空內容。
- 執行檔只在「啟動那一刻」讀一次文字，之後不重讀；所以一定要「關舊開新」，不能只更新剪貼簿。
- onefile exe 冷啟動＋edge-tts 合成要十幾秒，`tasklist` 太早查會誤判「沒在跑」；別用快速輪詢判斷成敗。
- 剛重新打包的未簽署 exe 首次執行可能被 SmartScreen 攔一次（跳「Windows 已保護你的電腦」），按「其他資訊→仍要執行」後會記住，之後不再攔。

## NotebookLM

語音摘要 Notebook：尚未建立（可執行 `/study-scaffold nlm` 補跑）
