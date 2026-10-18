# 練習 01 解答 — 盤點並優化環境

> 限制：不改 `~/.bashrc`、`~/.claude/` 等全域檔。shell 優化寫成本資料夾 `env.sh`（`source ./env.sh` 後生效），model 預設寫在本專案 `.claude/settings.json`。

## 任務 1：5 個可立即優化的設定

| # | 類別 | 現況痛點 | 優化做法 | 位置 | 狀態 |
|---|------|---------|---------|------|------|
| 1 | terminal | Windows 預設 cp950，Python 印中文常亂碼或 `UnicodeEncodeError` | `export PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8` | `env.sh` | ✅ 已套用 |
| 2 | alias | `claude --continue` / `--resume` 每天打很多次 | `cc`、`ccc`、`ccr` | `env.sh` | ✅ 已套用 |
| 3 | CLI flag | 腳本裡跑 `claude -p` 會被父 session 的 `CLAUDE*` 變數與全域設定干擾，結果不可重現 | `claude_clean()` 清掉 `CLAUDE*` 變數；`ccp` = `claude_clean -p --setting-sources project`；`ccj` 另加 `--output-format json` | `env.sh` | ✅ 已套用 |
| 4 | model 預設 | 每次手動加 `--model`；練習用的 demo 不需要最貴的模型 | `"model": "sonnet"` | `.claude/settings.json` | ✅ 已套用 |
| 5 | 權限 | 唯讀的 git 指令每次都要按允許；`-p` 模式下沒授權的工具會直接被拒 | `permissions.allow` 加 `git status/diff/log`、`echo` | `.claude/settings.json` | ✅ 已套用 |

其他可做但這次沒做的：status line（題目限制不執行 `/statusline`）、`settings.local.json` 放個人覆寫。

## 任務 2：套用並驗證（5 個全部套用）

### env.sh（優化 1–3）
```bash
$ shopt -s expand_aliases; source ./env.sh
[env.sh] 已載入：cc ccc ccr ccp ccj、PYTHONUTF8=1（K28_ROOT=~/workspace/k28-ch08-practice）
$ type cc ccc ccr ccp ccj
  cc is aliased to `claude'
  ccc is aliased to `claude --continue'
  ccr is aliased to `claude --resume'
  ccp is aliased to `claude_clean -p --setting-sources project'
  ccj is aliased to `claude_clean -p --setting-sources project --output-format json'
$ python -c "import sys;print('stdout encoding =',sys.stdout.encoding,'中文OK')"
stdout encoding = utf-8 中文OK
父 shell CLAUDE* 變數數：11
claude_clean 子環境 CLAUDE* 變數數：0
```

### model 預設 + 權限 allowlist（優化 4–5）
`bash tests/verify_e2e.sh model` 用 `ccj` 跑真的 `claude -p`，**沒有加 `--model`，也沒有加 `--allowedTools`**：
```text
result=7                       ← 成功執行 git status --short 並回報行數
models=claude-sonnet-5-5       ← JSON modelUsage 證明用的是 settings.json 的 sonnet
permission_denials=0           ← allowlist 生效，Bash(git status) 沒被拒
cost_usd=0.0540205
```

## 驗收
- [x] 5 個優化點具體可執行（每項都有實際指令或設定）
- [x] 至少 2 個已套用並驗證（實際 5 個都套用，並分別驗證）
