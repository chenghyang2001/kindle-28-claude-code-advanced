# Session 14 Summary

**日期**：2026-06-25
**專案**：kindle-28-claude-code-advanced

---

## 完成事項

### 1. addwii-yt-comment Skill 完整執行

- 影片：`Ys2vroZ3bns`（工廠偷排科技監控 Shorts）
- 因 Shorts URL 格式特殊，`get_transcript.py` 無法解析 `/shorts/VIDEO_ID`，改用 Puppeteer 提取標題 + 描述
- 生成 3 則候選留言，使用者選擇選項 1：「科技監控守護每口呼吸」（10 字，感性）
- Step 4：`like_video.py` 按讚成功（previous_rating: none → liked）
- Step 5：`post_comment.py` 發布成功（comment_id: `Ugz3iWsR_f73qRUZQeZ4AaABAg`）

### 2. SDD 工具成本調查

- 使用者詢問「之前哪個 SDD 工具燒了很多 token 和錢」
- 追查 `~/.claude/projects/C--Users-B00332-workspace-anthropic-quickstarts/memory/project_anthropic_quickstarts.md`
- 結論：`autonomous_agent_demo.py`（Anthropic Claude Code SDK 版）強制用 `ANTHROPIC_API_KEY`，走 API Credits 計費而非 Max 訂閱
- 使用者自行建立 `autonomous_cli_loop.sh`（bash + `claude` CLI 版）作為替代，走 Max 訂閱零費用

### 3. GitHub Spec Kit demo-sdd-spec-kit 提醒存入記憶

- 上次（同日 session）`specify init` 被中途停止（`stop it`），`demo-sdd-spec-kit/` 目錄已建但空
- 使用者要求提醒 2026-06-26（週五）補跑
- 已存入：`memory/reminder-sdd-spec-kit.md` + `MEMORY.md` 待辦區塊

---

## 關鍵技術筆記

### YouTube Shorts URL 解析問題

- `get_transcript.py` 無法處理 `https://www.youtube.com/shorts/VIDEO_ID` 格式
- 正規表達式只匹配 `watch?v=` 或 `youtu.be/` 格式
- **解法**：改用 Puppeteer navigate + evaluate 提取 `document.title` 和 `meta[name="description"]`
- 可考慮日後修補 `get_transcript.py` 支援 Shorts URL pattern

### Anthropic SDK vs CLI 成本差異

- SDK（`claude-code-sdk`）：強制 `ANTHROPIC_API_KEY` → API Credits 計費（貴）
- CLI（`claude -p`）：走 OAuth/Max 訂閱 → 零額外費用
- 規則：任何 autonomous 迴圈用 CLI 版，不用 SDK 版

---

## 產出檔案

| 檔案 | 動作 | 說明 |
|------|------|------|
| `memory/reminder-sdd-spec-kit.md` | 新增 | 2026-06-26 跑 specify init 的提醒 |
| `memory/MEMORY.md` | 更新 | 加入「待辦提醒」區塊 |

---

## HANDOFF（下次 session 優先處理）

### 立即行動

- [ ] **2026-06-26（週五）跑 `specify init`**：`cd ~/workspace/kindle-28-claude-code-advanced/demo-sdd-spec-kit && uvx --from git+https://github.com/github/spec-kit.git specify init my-project`，產出 spec.md / plan.md / tasks.md 三件套
- [ ] 考慮修補 `~/.claude/skills/youtube-summarizer/scripts/get_transcript.py`，加入 Shorts URL 支援（`/shorts/([a-zA-Z0-9_-]{11})`）

### 進行中（需接續）

- `demo-sdd-spec-kit/` 目錄已存在但為空，等週五補跑 specify init
- kindle-28 本書學習進度：Session 1-13 完成，第 14 課（SDD 工具比較）本 session 含外部演練

### 注意事項

- Shorts URL 需用 Puppeteer fallback，transcript script 目前不支援
- SDK 版 autonomous coding 會扣 API Credits，只用 CLI 版（`autonomous_cli_loop.sh`）
