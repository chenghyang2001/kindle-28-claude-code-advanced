# 練習 02 解答 — 設計 CI 自動 review

## 任務 1：四步流程

| 步驟 | 做什麼 | 對應 |
|------|--------|------|
| 1. PR 觸發 | 有人開 PR = 訊號，CI 自動啟動 | `on: pull_request` |
| 2. 取 diff | 抓出「這次改了什麼」 | checkout + diff |
| 3. Claude 審查 | diff 餵 Claude，分必改/建議/備註 | `claude_review.sh` |
| 4. 回貼 comment | 審查結果自動貼回 PR 留言區 | 開 PR 者一看就到 |

**為什麼餵 diff 不餵整個專案：**
1. 審查對象本來就是「這次改動」
2. 整個專案幾十萬行 → 又慢又貴、token 爆炸、可能超上限
3. 焦點：只給 diff，注意力集中、審得更準（呼應第 9 課 code-review 看 diff）

## 任務 2：API key 安全注入

✅ 放 **GitHub Secrets**，yml 只引用：
```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```
執行時才注入、log 自動遮星號。

**為什麼不能寫進 yml：** yml 會 commit 進 git → 等於把鑰匙公開貼網路。public repo 全世界看得到；private 也因 git 歷史永遠留著被挖出盜用。
> = CLAUDE.md 機密管理鐵律：key/token/credentials 走環境變數或 Secrets + 進 .gitignore。不小心 commit 進去 → 光刪檔沒用（歷史還在），唯一徹底解法是作廢重發金鑰。

## 延伸思考：skill / subagent / CI 界線
| 工具 | 重點 | 一句話 |
|------|------|--------|
| skill | 固定步驟、隨叫隨到 | 你手動喚起的流程 |
| subagent | 分工、獨立 context | 你指揮的分身 |
| CI | git 事件觸發、無人值守 | 不靠你自動跑的守門員 |

## 關鍵收穫
- CI review 餵 diff（焦點/省成本），結果回貼 PR comment。
- 金鑰一律 Secrets 注入，永不寫進會進版控的 yml。
