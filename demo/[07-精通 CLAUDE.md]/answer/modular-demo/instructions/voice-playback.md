## 🔊 每次回答自動語音播報

> 從臃腫主檔抽出的子檔（第 6 段）。性質：又長又帶一堆 caveat、會持續增補。
> 若 caveat 日後暴漲，可再拆 `voice-playback-caveats.md`（現在一段一檔剛好，先不拆）。

互動教學模式下，Claude **每次回答前**都要把該次回答用 `say_ui.exe` 念出來。流程「關舊開新 + 自動播放」：

1. 用 **Write 工具**把當次回答純文字寫進 `skills/_answer.txt`（UTF-8；可去掉 markdown 符號讓朗讀順）。
2. 關掉舊播放器（沒開也不報錯）：`cmd.exe /c "taskkill /IM say_ui.exe /F"`
3. 開新播放器、自動念（背景啟動、不阻塞）：
   `cmd.exe /c start "" "skills\dist\say_ui.exe" --file "skills\_answer.txt" --autoplay`

執行檔路徑（固定）：`skills/dist/say_ui.exe`。

### 授權與例外
- 上述「taskkill 舊的 + start 新的 + Write `_answer.txt`」三步**已長期授權，每回合自動執行，不需逐次徵求同意**——這是互動教學模式第 6/7 條（未經同意不可執行指令）的**唯一明文例外**。
- 其他所有課程指令（git / python / 其他檔案寫入）仍照第 6/7 條：先貼指令、等「執行」才跑。

### 已知 caveat（非阻擋）
- `taskkill /F` 會繞過 `on_close`，每回合在 `%TEMP%` 留一個暫存 .mp3；量小不主動清（以免誤刪其他 mp3）。
- `_answer.txt` 若為空或斷網，`say_ui` 會跳 modal 錯誤視窗 → Write 時務必寫非空內容。
- 執行檔只在「啟動那一刻」讀一次文字，之後不重讀 → 一定要「關舊開新」，不能只更新剪貼簿。
- onefile exe 冷啟動 + edge-tts 合成要十幾秒，`tasklist` 太早查會誤判「沒在跑」→ 改用 `Get-Process say_ui`，別用快速輪詢判斷成敗。
- 剛重打包的未簽署 exe 首次執行可能被 SmartScreen 攔一次，按「其他資訊 → 仍要執行」後會記住。
