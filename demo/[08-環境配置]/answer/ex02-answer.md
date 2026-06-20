# 練習 02 解答 — 寫一個 hook 自動化重複動作（進階）

> 目標：挑一個常做的重複動作，用 Claude Code 的 **hook** 讓它在對的時機自動發生。
> 本課成品：**SessionStart hook**，每次開這個專案自動印出學習進度。

## 一、hook 是什麼 + 常用事件

hook ＝綁在生命週期某個**時機**上、會自動跑的指令。

| 事件 | 觸發時機 | 活例子 |
|------|---------|--------|
| **SessionStart** | 開新 session 時 | 開機那串 `AUTH CHECK` |
| **UserPromptSubmit** | 送出訊息、Claude 還沒想之前 | 自動注入 `Restored Session Context` |
| **PreToolUse** | 呼叫工具**之前**（守門員） | 「寫程式三 agent 鐵律」攔 Write/Edit |
| **PostToolUse** | 工具跑完**之後** | 寫完 `.py` 自動 lint |
| **Stop** | 這回合答完、要停之前 | `Uncommitted changes detected` 提醒 |
| **PreCompact** | 壓縮對話前 | `/compact` 觸發的 voicemode hook |

## 二、四題推導（怎麼從需求對到實作）

1. **挑事件**：問「我要這件事在**什麼時間點**自動發生？」→「開專案就看到進度」＝開 session ＝ **SessionStart**。逐一刪掉 UserPromptSubmit（太吵）、PreToolUse/PostToolUse（與工具無關，張冠李戴）、Stop（收尾時機，適合提醒 commit）、PreCompact（搶救時機）。
2. **挑檔案**：放**專案層** `<repo>/.claude/settings.json` → 只此專案生效、跟著 git 進版、換機帶得走。（全域會污染別專案；local 不進 git 換機就沒。）
3. **結構**：`hooks` 物件用事件名當 key，事件底下陣列，每元素 `matcher`（可省）+ `hooks`（`type: command` + `command`）。
4. **指令**：`git log -1` 一次涵蓋「最新 commit + 最近完成的課」——因為每完成一課就 commit 一次、訊息「完成第N課」開頭，最新 commit 訊息本身就是進度。

## 三、成品檔（`.claude/settings.json`）

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "git -C \"C:/Users/user/workspace/kindle-28-claude-code-advanced\" log -1 --format=\"📚 學習進度：%s (%h)\""
          }
        ]
      }
    ]
  }
}
```

> `git -C "<絕對路徑>"`：不管 hook 從哪個 cwd 跑都抓得到本 repo。

## 四、驗證（兩項都過）

| 驗證 | 結果 |
|------|------|
| V1 JSON 合法 | ✅ python 載入成功；事件 `SessionStart`、`type: command` |
| V2 實跑 git 指令 | ✅ `📚 學習進度：完成第八課 環境配置基礎… (523f73d)` |

## 五、注意事項

- 專案層 hook 第一次載入時 Claude Code 會問「是否信任本專案 hook」，按**允許**才生效——安全機制（防 clone 別人 repo 被惡意 hook 偷跑）。
- 不過度：暫不加 `grep`+`wc` 數 ✅ 的版本（bash 專屬、Windows 易出狀況），最小單一 `git log` 已達標。

## 驗收
- [x] 挑一個重複動作（開 session 看學習進度）
- [x] 正確對到事件（SessionStart）並說明為何不選別的
- [x] 寫進正確檔案層級（專案層 settings.json）
- [x] 實作 + 驗證（JSON 合法 + 實跑 git 指令輸出正確）
