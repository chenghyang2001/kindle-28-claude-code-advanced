"""核對 CHEATSHEET.md：每個 claude CLI flag 是否真的出現在 --help，斜線指令是否在本版清單。

用法：
  PYTHONUTF8=1 python check_cheatsheet.py              # 核對 CHEATSHEET.md
  PYTHONUTF8=1 python check_cheatsheet.py --selftest   # 用假 flag / 假指令驗證偵測邏輯
斜線清單來源：help-snapshots/init.json（claude -p stream-json 的 init 事件）。
"""
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FLAG_RE = re.compile(r"(?<![\w-])(-{1,2}[A-Za-z][\w-]*)")
WORD_RE = re.compile(r"^[a-z][a-z-]*$")
_help_cache: dict[tuple, str] = {}
# Windows 的 npm 安裝是 claude.CMD，subprocess 不會自己補副檔名，要先 which
CLAUDE_BIN = shutil.which("claude")


def clean_env() -> dict:
    """題目要求：呼叫 claude 前清掉 CLAUDE 開頭的環境變數（避免被當成巢狀 session）。"""
    return {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}


def get_help(path: tuple) -> str:
    if path not in _help_cache:
        try:
            proc = subprocess.run([CLAUDE_BIN, *path, "--help"], capture_output=True,
                                  encoding="utf-8", errors="replace", timeout=60, env=clean_env())
            _help_cache[path] = proc.stdout + proc.stderr
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"錯誤：無法執行 claude {' '.join(path)} --help：{exc}", file=sys.stderr)
            sys.exit(2)
    return _help_cache[path]


def is_real_subcommand(path: tuple) -> bool:
    """help 的 Usage 行要含每個子指令字（支援 plugin|plugins 這種別名），否則代表被當成 prompt。"""
    first = next((l for l in get_help(path).splitlines() if l.startswith("Usage:")), "")
    names = set(re.split(r"[\s|]+", first))
    return all(word in names for word in path)


def resolve(tokens: list) -> tuple:
    """取最長的有效子指令前綴（最多 2 層）；回傳 (子指令路徑, 無效的子指令字或 None)。"""
    words = []
    for tok in tokens[:2]:
        if not WORD_RE.match(tok):
            break
        words.append(tok)
    for n in range(len(words), 0, -1):
        if is_real_subcommand(tuple(words[:n])):
            return tuple(words[:n]), None
    return (), (words[0] if words else None)


def split_cmd(cmd: str) -> list:
    try:
        return shlex.split(cmd)
    except ValueError:
        return cmd.split()


def check_claude_span(cmd: str, line: str) -> list:
    tokens = split_cmd(cmd)[1:]
    if "--" in tokens:  # `--` 之後是交給 MCP server 的參數，不屬於 claude
        tokens = tokens[:tokens.index("--")]
    path, bad_sub = resolve(tokens)
    results = []
    if bad_sub and not tokens[0].startswith("-") and not tokens[0].startswith('"'):
        marked = "⚠" in line
        results.append(("SUB", f"claude {bad_sub}", "已標註不存在" if marked else "不存在（未標註！）", marked))
    elif path:
        results.append(("SUB", "claude " + " ".join(path), "OK", True))
    help_flags = set(FLAG_RE.findall(get_help(path)))
    for tok in tokens:
        if not tok.startswith("-"):
            continue
        flag = tok.split("=", 1)[0]
        ok = flag in help_flags
        where = "claude " + " ".join(path) if path else "claude"
        results.append(("FLAG", f"{where} {flag}", "OK" if ok else "不在 help", ok))
    return results


def load_slash() -> set:
    snap = ROOT / "help-snapshots" / "init.json"
    try:
        data = json.loads(snap.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"錯誤：讀不到斜線清單 {snap}：{exc}", file=sys.stderr)
        sys.exit(1)
    return set(data.get("slash_commands", []))


def check_text(text: str, slash: set) -> list:
    results = []
    for line in text.splitlines():
        for span in re.findall(r"`([^`]+)`", line):
            span = span.strip()
            if span.startswith("claude "):
                results += check_claude_span(span, line)
            elif re.match(r"^-{1,2}[A-Za-z]", span):  # 表格內單獨寫的 flag，視為主指令的 flag
                results += check_claude_span("claude " + span, line)
            elif re.match(r"^/[a-z]", span):
                name = span.split()[0].lstrip("/")
                if name in slash:
                    results.append(("SLASH", "/" + name, "OK", True))
                elif "〔TUI〕" in line:
                    results.append(("SLASH", "/" + name, "TUI 專用（已標註）", True))
                else:
                    results.append(("SLASH", "/" + name, "不在本版清單", False))
    return results


def report(results: list) -> int:
    seen, bad = set(), 0
    for kind, item, status, ok in results:
        if (kind, item) in seen:
            continue
        seen.add((kind, item))
        bad += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {kind:5} {item:45} {status}")
    print(f"\n共 {len(seen)} 項，FAIL {bad} 項")
    return bad


def selftest(slash: set) -> None:
    fake = ("| x | `claude -p \"hi\" --no-such-flag` |\n| y | `/no-such-cmd` |\n"
            "| z | `claude mcp add --scope project --bogus d -- npx s --not-claude` |\n")
    res = {(k, i): ok for k, i, _, ok in check_text(fake, slash)}
    assert res[("FLAG", "claude -p")] is True
    assert res[("FLAG", "claude --no-such-flag")] is False
    assert res[("SLASH", "/no-such-cmd")] is False
    assert res[("FLAG", "claude mcp add --scope")] is True
    assert res[("FLAG", "claude mcp add --bogus")] is False
    assert ("FLAG", "claude mcp add --not-claude") not in res, "-- 之後的參數不該被檢查"
    print("selftest PASS：假 flag、假斜線指令都抓得到，-- 之後的參數有略過")


def main() -> None:
    if CLAUDE_BIN is None:
        print("錯誤：PATH 找不到 claude 指令", file=sys.stderr)
        sys.exit(2)
    slash = load_slash()
    if "--selftest" in sys.argv:
        selftest(slash)
        return
    try:
        text = (ROOT / "CHEATSHEET.md").read_text(encoding="utf-8")
    except OSError as exc:
        print(f"錯誤：讀不到 CHEATSHEET.md：{exc}", file=sys.stderr)
        sys.exit(1)
    sys.exit(1 if report(check_text(text, slash)) else 0)


if __name__ == "__main__":
    main()
