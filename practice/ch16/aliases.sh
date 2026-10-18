#!/bin/bash
# Claude Code 小抄延伸：只收「打字長、參數固定、每天會用」的指令。
# 用法：source ./aliases.sh（不寫進 ~/.bashrc，需要時才載入）

# 非互動跑一次、不留 session 紀錄（每次都要打 3 個 flag，最值得縮）
cc_p() {
  if [ $# -eq 0 ]; then echo "用法：cc_p \"提示詞\"" >&2; return 1; fi
  claude -p "$1" --output-format text --no-session-persistence "${@:2}"
}

# 給腳本吃的 JSON 輸出 + 預算上限，避免自動化跑爆
cc_json() {
  if [ $# -eq 0 ]; then echo "用法：cc_json \"提示詞\" [預算USD]" >&2; return 1; fi
  claude -p "$1" --output-format json --max-budget-usd "${2:-0.5}" --no-session-persistence
}

# 平行任務開 worktree（名稱必填，避免一堆匿名 worktree）
cc_wt() {
  if [ $# -eq 0 ]; then echo "用法：cc_wt <worktree 名稱>" >&2; return 1; fi
  claude -w "$1"
}

alias ccc='claude -c'                     # 接續本目錄最近 session
alias ccplan='claude --permission-mode plan'
alias ccsafe='claude --safe-mode'         # 設定壞掉時排錯用
