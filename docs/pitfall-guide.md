# 踩坑排解指南 — kindle-28-claude-code-advanced

> 由 `/pitfall-guide --all` 生成（2026-07-23）。
> 素材來源：17 課 STEP_LOG、`docs/踩坑紀錄.md`、git 修復提交。
> 條目按「踩到頻率 / 通用性」排序；第 3 課的 7 條細節在 [踩坑紀錄.md](踩坑紀錄.md)，此處僅索引不重複收錄。

---

## 一、Windows 環境（cp950 編碼、路徑轉換、MSYS）— 最常踩

### 1.1 跨 Git Bash ↔ PowerShell 傳中文/方括號路徑會壞

- **症狀**：PowerShell 播放 `demo/[03-計畫模式]/` 下的 MP3 找不到檔或開檔失敗。
- **根因**：子行程不繼承 Git Bash 的 CWD + 中文/方括號路徑跨 shell 編碼損毀。
- **解法**：`shutil.copyfile` 到 ASCII-only 暫存路徑（`tempfile`）再用絕對路徑餵 PowerShell。
- **預防**：鐵則「跨 shell 別傳中文/方括號路徑」，已寫進全域 instructions。
- 來源：`docs/踩坑紀錄.md` §1、§2（課程 03）

### 1.2 Python 不認 MSYS 的 `/c/...` 路徑

- **症狀**：`python say.py -f "/c/Users/.../q3.txt"` → 找不到檔。
- **根因**：`/c/` 前綴只有 Git Bash 認得，Windows Python 解讀成 `C:\c\...`。
- **解法／預防**：傳給 Python 一律用 `C:/Users/...`（正斜線）格式。
- 來源：`docs/踩坑紀錄.md` §3（課程 03）

### 1.3 PowerShell `Register-ObjectEvent` 未清理 → exit 2 偽陰性

- **症狀**：MP3 播完了，Python 卻判「播放失敗」。
- **根因**：事件訂閱者與背景 job 未清除，runspace 拆除時 exit 2；Python 只看 returncode 就誤判。
- **解法**：腳本結尾 `Unregister-Event` + `Remove-Job -Force` + 明確 `exit 0`。
- **預防**：判斷成敗不能只看 returncode，要搭配實際產出物驗證。
- 來源：`docs/踩坑紀錄.md` §4（課程 03）

### 1.4 快速輪詢 `tasklist` 誤判 onefile exe「沒啟動」

- **症狀**：launch 播放器後連續多次查到「0 個行程」，誤判啟動失敗。
- **根因**：onefile exe 冷啟動 + edge-tts 長講稿合成要十幾秒，加上 SmartScreen 偶攔一次，行程出現時間飄移——每次都查太早。
- **解法**：放棄快速輪詢；用「下回合 `taskkill` 抓得到活行程」反證它在跑。
- **預防**：caveat 已寫進專案 CLAUDE.md（語音播報段落）。
- 來源：`demo/[04-脈絡管理]/STEP_LOG.md`

---

## 二、Claude Code 設定（plugin、hook、跨機器同步）

### 2.1 跨機器同步時 `enabledPlugins` 不會自動帶過來

- **症狀**：CLAUDE.md 記「已啟用 claude-md-management」，但 `/revise-claude-md` 在這台機器跑不出來。
- **根因**：市集快取有該外掛 ≠ 該機 `~/.claude/settings.json` 真的啟用；文件記載與實機配置漂移。
- **解法**：`claude plugin install claude-md-management@claude-plugins-official` 補裝，`/reload-plugins` 即生效（免重啟）。
- **預防**：排錯通則——先 `grep <plugin> ~/.claude/settings.json` 看 `enabledPlugins` 有沒有該項，缺項就補裝或 `claude plugin enable`。已記入 CLAUDE.md。
- 來源：commit `27d384e`（課程 09 外掛實戰）

### 2.2 settings.json hook 硬編碼絕對路徑 → 跨機器失效

- **症狀**：hook 在公司機正常，換一台機器就找不到腳本。
- **根因**：hook command 寫死 `C:\Users\<name>\...`，違反全域「禁止硬編碼路徑」鐵律。
- **解法**：改用 `$CLAUDE_PROJECT_DIR` 環境變數組路徑。
- **預防**：hookify 規則 `no-hardcoded-paths` 會對程式碼/設定檔寫入 `C:\Users\` 時 warn。
- 來源：commit `010b7f2`（課程 11 前後的 user-level hook 修復）

---

## 三、Git / worktree

### 3.1 內嵌 git repo 讓 `git add` 出現壞掉的 gitlink

- **症狀**：worktree 練習在 `sandbox/` 留下 3 個內嵌 repo，`git add` 當成 gitlink 出錯。
- **解法**：`git rm -rf --cached` 移除快取後再處理。
- 來源：`docs/踩坑紀錄.md` §7a（課程 02 衍生）

### 3.2 .gitignore 的 `[ ]` 是字元類別，不匹配字面目錄名

- **症狀**：寫 `demo/[02-平行化]/sandbox/` 想擋卻無效。
- **根因**：gitignore pattern 中 `[...]` 是 glob 字元類別語法。
- **解法／預防**：跳脫成 `demo/\[02-平行化\]/sandbox/`；本專案課程目錄全帶方括號，新增 ignore 規則時都要跳脫。
- 來源：`docs/踩坑紀錄.md` §7b（課程 02 衍生）

---

## 四、自主迴圈 / 自動化設計

### 4.1 Ralph 零進展護欄用「整檔雜湊」有致命破口

- **症狀**：happy path 測試全綠，但真跑時護欄可能永不觸發、燒到 backstop。
- **根因**：claude 沒完成任務也會「亂動」TASK.md（重排版、自增子任務）→ bytes 變 → 雜湊變 → 護欄以為有進展。對「壞掉但會動檔案的 claude」形同虛設。
- **解法**：改用客觀進度信號——「未完成框數單調遞減」（`remaining >= prev_remaining` → exit 3），並加 `--dry-run-noop` 測試鉤子驗證。
- **預防**：進度信號要客觀可驗，不能拿 AI 自報狀態當唯一真相；審查 gate（reviewer）確實能抓到這種非 happy-path 破口。
- 來源：`demo/[06-Ralph 自主迴圈]/STEP_LOG.md`

### 4.2 時間窗護欄預設關閉且沒包住 claude 呼叫

- **症狀**：單輪 claude 卡死時整個迴圈跟著卡死，MAX_SECONDS 形同虛設。
- **解法**：MAX_SECONDS 預設改 1800，用 `timeout` 包住每一通 claude 呼叫（逾時當該輪失敗）。
- **預防**：無人值守三護欄缺一不可——逾時防卡死、通知防沉默、單例鎖防重入。
- 來源：`demo/[06-Ralph 自主迴圈]/STEP_LOG.md`

### 4.3 自動化管線把「單步失敗」一律當「全停」

- **症狀**：多環節自動任務一步掛掉整條停，其餘可完成的工作全被拖累。
- **根因**：失敗處理策略未區分「可隔離失敗」與「後續無意義的失敗」。
- **解法**：合理降級——隔離失敗那步（標記+記錄+通知）繼續處理其餘；只有繼續沒意義時才乾淨停。
- **預防**：設計自動化時先問每一步「它掛了，後面還有意義嗎？」再決定停或續。
- 來源：`demo/[12-自動化]/STEP_LOG.md`

---

## 五、打包 / 工具鏈（低頻但費時）

- **exe 圖示 ≠ 視窗標題列圖示**：`--icon` 只改檔案圖示，標題列要程式碼 `root.iconbitmap()` + `--add-data` 包入 ico。（`docs/踩坑紀錄.md` §5）
- **打包前先進乾淨 venv**：全域 Python 打包 46MB（夾帶無關 DLL），乾淨 venv 只裝必要套件 → 15MB。（`docs/踩坑紀錄.md` §6）

---

## 附：查無素材而省略的分類

skill 觸發、MCP 連線——各課 STEP_LOG 中無「實際踩過」的紀錄，依生成規則省略不腦補。
