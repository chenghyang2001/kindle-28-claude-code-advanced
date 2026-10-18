"""練習 01：檢查 5 個 Claude Code 學習來源是否可連線，並盡量抓出最近更新日期。

只用標準庫 urllib。結果寫入 sources-check.txt。
用法：
    python check_sources.py            # 檢查 5 個來源
    python check_sources.py --selftest # 額外測一個不存在的網域，驗證錯誤處理
"""
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TIMEOUT_SEC = 15
USER_AGENT = "k28-ch17-practice/1.0 (learning exercise)"
OUTPUT_FILE = Path(__file__).with_name("sources-check.txt")

# 每個來源：名稱、給人看的網址、取更新日期的方法
SOURCES = [
    {"name": "官方文件 Claude Code Docs", "url": "https://code.claude.com/docs/en/overview", "date_from": "header"},
    {"name": "官方 CHANGELOG.md", "url": "https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md",
     "date_from": "changelog"},
    {"name": "GitHub Releases", "url": "https://github.com/anthropics/claude-code/releases", "date_from": "releases"},
    {"name": "GitHub Issues（社群踩坑）", "url": "https://github.com/anthropics/claude-code/issues", "date_from": "issues"},
    {"name": "Anthropic Engineering Blog", "url": "https://www.anthropic.com/engineering", "date_from": "header"},
]

GITHUB_API = "https://api.github.com/repos/anthropics/claude-code"


def http_get(url: str):
    """回傳 (狀態碼, headers, body 文字)。網路錯誤會往外丟，由呼叫端處理。"""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return resp.status, resp.headers, body


def get_json(url: str):
    _, _, body = http_get(url)
    return json.loads(body)


def date_from_header(headers) -> str:
    return headers.get("Last-Modified") or "（網站未提供 Last-Modified）"


def date_from_changelog() -> str:
    # 用 commits API 取 CHANGELOG.md 最後一次修改時間，再從 raw 檔抓最新版本號
    commits = get_json(f"{GITHUB_API}/commits?path=CHANGELOG.md&per_page=1")
    commit_date = commits[0]["commit"]["committer"]["date"] if commits else "未知"
    _, _, raw = http_get("https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md")
    match = re.search(r"^##\s+(\S+)", raw, re.MULTILINE)
    version = match.group(1) if match else "未知"
    return f"{commit_date}（最新版本 {version}）"


def date_from_releases() -> str:
    release = get_json(f"{GITHUB_API}/releases/latest")
    return f"{release.get('published_at')}（{release.get('tag_name')}）"


def date_from_issues() -> str:
    issues = get_json(f"{GITHUB_API}/issues?state=all&sort=updated&per_page=1")
    return issues[0]["updated_at"] if issues else "未知"


DATE_FETCHERS = {"changelog": date_from_changelog, "releases": date_from_releases, "issues": date_from_issues}


def check_one(source: dict) -> str:
    """檢查單一來源，任何錯誤都轉成文字結果，不讓整支腳本中斷。"""
    try:
        status, headers, _ = http_get(source["url"])
    except urllib.error.HTTPError as e:
        return f"[FAIL] {source['name']}\n  網址：{source['url']}\n  HTTP 錯誤：{e.code} {e.reason}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return f"[FAIL] {source['name']}\n  網址：{source['url']}\n  連線失敗：{e}"

    try:
        if source["date_from"] == "header":
            updated = date_from_header(headers)
        else:
            updated = DATE_FETCHERS[source["date_from"]]()
    except urllib.error.HTTPError as e:
        updated = f"（取日期失敗：HTTP {e.code}，可能是 GitHub API rate limit）"
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, KeyError, IndexError) as e:
        updated = f"（取日期失敗：{type(e).__name__}: {e}）"

    return f"[OK]   {source['name']}\n  網址：{source['url']}\n  HTTP 狀態：{status}\n  最近更新：{updated}"


def main():
    sources = list(SOURCES)
    if "--selftest" in sys.argv:
        sources.append({"name": "錯誤處理自我測試（不存在的網域）",
                        "url": "https://no-such-host.invalid/", "date_from": "header"})
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [f"Claude Code 學習來源檢查  {now}", "=" * 50]
    ok_count = 0
    for source in sources:
        result = check_one(source)
        ok_count += result.startswith("[OK]")
        lines.append(result)
        print(result, flush=True)
    summary = f"\n總結：{ok_count}/{len(sources)} 可連線"
    lines.append(summary)
    print(summary)
    try:
        OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as e:
        print(f"錯誤：無法寫入 {OUTPUT_FILE}：{e}", file=sys.stderr)
        sys.exit(1)
    print(f"已寫入 {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
