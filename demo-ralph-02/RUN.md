# 如何在 Windows 10 跑 Ralph 獨立版（演練步驟）

> 獨立版 = `frankbria/ralph-claude-code`，**bash + tmux 原生工具，Windows 不能原生跑** → 走 WSL2 (Ubuntu)。

## A. 一次性安裝（在 WSL2 Ubuntu 內）

```bash
# 1. （在 PowerShell 系統管理員）安裝 WSL2 + Ubuntu，重開機後設定帳號
#    wsl --install

# 2. 進 Ubuntu，裝相依套件
sudo apt update
sudo apt install -y tmux jq git coreutils build-essential

# 3. 裝 Node（建議 nvm；或 nodesource），需 Node 18+
#    然後裝 Claude Code CLI（用 Max 訂閱登入，不要設 ANTHROPIC_API_KEY）
npm install -g @anthropic-ai/claude-code
claude   # 首次啟動依指示登入

# 4. 裝 Ralph 獨立版（一台機器只需一次）
git clone https://github.com/frankbria/ralph-claude-code.git
cd ralph-claude-code
./install.sh
# 產生全域指令：ralph / ralph-monitor / ralph-import / ralph-enable ...
```

## B. 跑這個演練專案

```bash
# 1. 切到本專案（從 WSL 存取 Windows 檔案）
cd /mnt/c/Users/user/workspace/kindle-28-claude-code-advanced/demo-ralph-02

# 2. 裝測試框架
npm install

# 3. 匯入規格 → Ralph 把 5 個端點拆成任務節點
ralph-import api-spec.md

# 4. 初始化專案（互動精靈）
ralph-enable

# 5. 🟢 先乾跑（不花任何 API、不真的呼叫）確認流程
ralph --monitor --dry-run

# 6. 真的跑（帶安全護欄：每小時上限 + 逾時）
ralph --monitor --calls 50 --timeout 30
```

## C. 安全與成本提醒（對應第五、七題）

- **先 `--dry-run`**：模擬整個迴圈但不呼叫 API、不花錢，演練最該先做這步。
- `--calls 50`：每小時最多 50 次 API（速率限制）。
- `--timeout 30`：30 分鐘逾時（會話過期）。
- Claude CLI 用 **Max 訂閱**額度（$0），**不要設 `ANTHROPIC_API_KEY`**（會改走 API 計費）。
- tmux 監控：`ralph --monitor` 會開儀表板看 loop 次數 / API 用量 / log；可關視窗（detach）出門，回來 attach 看進度。

## D. 驗收

`npm test` 全綠 = 5 個端點都實作完成。
