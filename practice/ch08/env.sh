# env.sh — 本專案的 shell 環境優化（取代修改 ~/.bashrc）
# 使用方式：source ./env.sh   （只影響目前這個 shell，關掉即失效）

# ── 優化 1：terminal 編碼 ── Windows 預設 cp950，Python 印中文會亂碼/報錯
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# 本專案根目錄（不寫死路徑，以 env.sh 所在位置推算）
K28_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export K28_ROOT

# 清掉 CLAUDE* 環境變數後再執行 claude，避免在 Claude session 內巢狀呼叫時被父 session 變數干擾
claude_clean() {
  local unset_args=()
  local v
  for v in $(env | grep -oE '^CLAUDE[A-Za-z0-9_]*'); do
    unset_args+=("-u" "$v")
  done
  env "${unset_args[@]}" claude "$@"
}

# ── 優化 2：常用指令 alias ──
alias cc='claude'
alias ccc='claude --continue'      # 接續最近一次對話
alias ccr='claude --resume'        # 從清單挑一個 session 接續

# ── 優化 3：非互動腳本用的 CLI flag 組合 ──
# ccp "任務"：乾淨環境 + 一次性 + 只讀本專案設定（不吃全域 ~/.claude 設定，結果可重現）
alias ccp='claude_clean -p --setting-sources project'
# ccj "任務"：同上但輸出 JSON（可用 jq 取 result / cost / model）
alias ccj='claude_clean -p --setting-sources project --output-format json'

echo "[env.sh] 已載入：cc ccc ccr ccp ccj、PYTHONUTF8=1（K28_ROOT=$K28_ROOT）"
