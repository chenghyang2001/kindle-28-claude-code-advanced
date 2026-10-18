"""Bash 稽核 + 危險指令守門 hook。

觸發時機：
  - SessionStart：記錄 session 開始（方便在 log 中切分每次執行）
  - PreToolUse(Bash)：Claude 每次要跑 Bash 前，記錄指令；命中危險樣式則以 exit 2 阻擋

逃生門（kill switch）：
  - 環境變數 K28_HOOK_DISABLE=1 → 立即 exit 0，不記錄、不阻擋
  - 腳本內部任何例外 → fail-open（exit 0），絕不因 hook 壞掉卡死 Claude
"""
import datetime
import json
import os
import re
import sys
from pathlib import Path

# 危險指令樣式：命中即阻擋
DANGEROUS_PATTERNS = [
    r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+(/|~)(\s|$)",  # rm -rf / 或 ~
    r"\bgit\s+push\b.*--force\b",                    # 強制 push
    r"\bgit\s+reset\s+--hard\b",                     # 丟棄工作樹
]


def log_path() -> Path:
    """log 檔放在本專案 .claude/hooks/logs/ 底下。"""
    # 以腳本自身位置推算（.claude/hooks/xxx.py → 專案根），
    # 不依賴 CLAUDE_PROJECT_DIR：Git Bash 下它可能是 /c/... 形式，Windows Python 會誤解
    root = Path(__file__).resolve().parents[2]
    p = root / ".claude" / "hooks" / "logs" / "hook.log"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def write_log(line: str) -> None:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_path().open("a", encoding="utf-8") as f:
        f.write(f"{ts} {line}\n")


def main() -> int:
    # kill switch：最先檢查，連 stdin 都不讀
    if os.environ.get("K28_HOOK_DISABLE") == "1":
        return 0

    data = json.loads(sys.stdin.read() or "{}")
    event = data.get("hook_event_name", "?")
    session = (data.get("session_id") or "?")[:8]

    if event == "SessionStart":
        write_log(f"[{session}] SessionStart source={data.get('source', '?')}")
        return 0

    if event == "PreToolUse":
        cmd = (data.get("tool_input") or {}).get("command", "")
        for pat in DANGEROUS_PATTERNS:
            if re.search(pat, cmd):
                write_log(f"[{session}] PreToolUse BLOCK cmd={cmd!r} pattern={pat!r}")
                print(f"[bash_audit] 已阻擋危險指令：{cmd}（設 K28_HOOK_DISABLE=1 可停用此 hook）",
                      file=sys.stderr)
                return 2  # exit 2 = 阻擋該工具呼叫，stderr 回饋給 Claude
        write_log(f"[{session}] PreToolUse ALLOW cmd={cmd!r}")
        return 0

    write_log(f"[{session}] {event} (未處理)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # fail-open：hook 自身錯誤不影響 Claude
        try:
            write_log(f"[hook-error] {type(e).__name__}: {e}")
        except Exception:
            pass
        sys.exit(0)
