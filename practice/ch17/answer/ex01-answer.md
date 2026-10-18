# 練習 01 解答：持續學習來源清單

## 任務 1：5 個追蹤來源與理由

| # | 來源 | 類型 | 追蹤理由 |
| --- | ------ | ------ | --------- |
| 1 | [官方 CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) | 官方 changelog | 每個版本的新功能、行為改變、修掉的 bug 都寫在這裡，是最權威、最早的消息。功能突然「不一樣了」先查這裡 |
| 2 | [Claude Code 官方文件](https://code.claude.com/docs/en/overview) | 官方文件 | hooks、settings、MCP、skills 的正確寫法與欄位定義；changelog 只說「有改」，文件說「怎麼用」 |
| 3 | [GitHub Releases](https://github.com/anthropics/claude-code/releases) | GitHub repo | 版本號＋發布時間，可以用 API 自動比對自己裝的版本是否落後（`claude --version`） |
| 4 | [GitHub Issues](https://github.com/anthropics/claude-code/issues) | GitHub issues | 社群踩坑第一現場：遇到怪 bug 先搜這裡，常能找到已知問題與 workaround（Windows / Git Bash 相關問題尤其多） |
| 5 | [Anthropic Engineering Blog](https://www.anthropic.com/engineering) | 官方精選文章 | 更新慢但深：agent 設計、context engineering、最佳實踐等經過整理的長文，適合每月消化一次 |

備選（社群）：Anthropic 官方 Discord、Reddit r/ClaudeAI——討論很即時，但雜訊多、無法用腳本穩定檢查，所以不放進核心 5 個。

## 任務 2：最高優先來源

**⭐ 最高優先：#1 官方 CHANGELOG.md**

理由：

- 更新最頻繁：實測最新版本 2.1.302 於 2026-10-16 發布，幾乎每 1～2 天就有新版。
- 資訊密度最高：一份檔案涵蓋所有變更，不用到處翻。
- 最好自動化：可用 GitHub API 抓最後修改時間＋第一個 `## 版本號` 標題，比對上次看到的版本。

提醒設計（**只寫設計，未建立任何排程**）：

- 頻率：每週一次（每天看太碎，會變成負擔）。
- 做法：執行 `python check_sources.py`，若 CHANGELOG 版本號與上週記錄不同，就讀新增的段落，挑 1 條「本週要試用」寫進學習日誌。
- 若要自動化：可用排程工具每週跑一次腳本並比對版本號（本練習依限制不建立）。

> 註：GitHub Issues 的「最近更新」時間其實更新得更頻繁（幾分鐘一次），但那是雜訊量，不是「值得每次看」的訊號，所以不選它當提醒對象。

## 實際驗證：`check_sources.py`

用 Python 標準庫 `urllib` 檢查 5 個網址的 HTTP 狀態，並抓最近更新日期：

| 來源 | 取日期方式 |
| ------ | ----------- |
| CHANGELOG | GitHub commits API（`path=CHANGELOG.md`）＋ raw 檔第一個 `##` 版本號 |
| Releases | `GET /repos/anthropics/claude-code/releases/latest` 的 `published_at` |
| Issues | `GET /issues?sort=updated&per_page=1` 的 `updated_at` |
| 官方文件、Blog | HTTP `Last-Modified` header（實測兩站都沒提供，會寫明「未提供」） |

錯誤處理：HTTP 錯誤、DNS / 連線失敗、逾時、JSON 解析失敗、GitHub API rate limit 都會轉成文字記錄，不會讓整支腳本中斷。`--selftest` 會多測一個不存在的網域來驗證這點。

執行結果（2026-10-18，存於 `sources-check.txt`）：

```text
[OK] 官方文件 Claude Code Docs   HTTP 200  最近更新：（網站未提供 Last-Modified）
[OK] 官方 CHANGELOG.md           HTTP 200  最近更新：2026-10-16T20:52:45Z（最新版本 2.1.302）
[OK] GitHub Releases             HTTP 200  最近更新：2026-10-16T20:53:06Z（v2.1.302）
[OK] GitHub Issues（社群踩坑）    HTTP 200  最近更新：2026-10-18T06:22:46Z
[OK] Anthropic Engineering Blog  HTTP 200  最近更新：（網站未提供 Last-Modified）
總結：5/5 可連線
```

`--selftest` 的錯誤案例輸出：

```text
[FAIL] 錯誤處理自我測試（不存在的網域）
  網址：https://no-such-host.invalid/
  連線失敗：<urlopen error [Errno 11001] getaddrinfo failed>
總結：5/6 可連線      ← 腳本照常跑完，exit 0
```

## 驗收

- [x] 5 個來源各有追蹤理由
- [x] 標出最高優先來源（CHANGELOG.md）
