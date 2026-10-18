"""待辦清單 CLI：支援 add / list / done，資料以 JSON 存檔（只用標準庫）。"""
import argparse
import json
import os
import sys
from pathlib import Path

DEFAULT_DB = "todo.json"  # 可用環境變數 TODO_DB 覆寫


def load_tasks(path) -> list[dict]:
    """讀取任務清單；檔案不存在回傳 []，JSON 壞掉 raise ValueError。"""
    db_path = Path(path)
    if not db_path.exists():
        return []
    try:
        # utf-8-sig：相容記事本存檔時加上的 BOM
        tasks = json.loads(db_path.read_text(encoding="utf-8-sig"))
    except UnicodeDecodeError as e:
        raise ValueError(f"存檔不是 UTF-8 編碼：{db_path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"存檔 JSON 格式錯誤：{db_path}（{e}）") from e
    if not isinstance(tasks, list):
        raise ValueError(f"存檔內容不是任務清單：{db_path}")
    for task in tasks:
        if not _is_valid_task(task):
            raise ValueError(f"存檔任務格式錯誤：{db_path}：{task!r}")
    return tasks


def _is_valid_task(task) -> bool:
    # 用 type() is int 排除 bool（True 也是 int 的子類）
    return (
        isinstance(task, dict)
        and type(task.get("id")) is int
        and isinstance(task.get("title"), str)
        and isinstance(task.get("done"), bool)
    )


def save_tasks(path, tasks) -> None:
    """以 UTF-8 寫入任務清單；中文保持原樣（ensure_ascii=False）。"""
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # 先寫暫存檔再 os.replace：寫到一半中斷也不會毀掉舊存檔
    tmp_path = db_path.with_name(db_path.name + ".tmp")
    tmp_path.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(tmp_path, db_path)


def add_task(path, title) -> dict:
    """新增任務；標題去頭尾空白後為空則 raise ValueError。"""
    clean_title = (title or "").strip()
    if not clean_title:
        raise ValueError("標題不可為空")
    tasks = load_tasks(path)
    next_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {"id": next_id, "title": clean_title, "done": False}
    tasks.append(new_task)
    save_tasks(path, tasks)
    return new_task


def list_tasks(path) -> list[dict]:
    """回傳依 id 排序的任務清單。"""
    return sorted(load_tasks(path), key=lambda t: t["id"])


def mark_done(path, task_id) -> dict:
    """標記任務完成；找不到 id raise KeyError，重複標記不報錯。"""
    tasks = load_tasks(path)
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_tasks(path, tasks)
            return task
    raise KeyError(f"找不到任務 #{task_id}")


def _resolve_db(cli_db) -> str:
    """DB 路徑優先序：--db > TODO_DB > 預設 todo.json。"""
    if cli_db:
        return cli_db
    env_db = os.environ.get("TODO_DB")
    return env_db if env_db else DEFAULT_DB


def _use_utf8_console() -> None:
    # Windows cp950 終端機印中文會 UnicodeEncodeError，改成 utf-8
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError, OSError):
            pass


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="待辦清單 CLI")
    parser.add_argument("--db", help="存檔路徑（優先於環境變數 TODO_DB）")
    sub = parser.add_subparsers(dest="command", required=True)
    p_add = sub.add_parser("add", help="新增任務")
    p_add.add_argument("title", nargs="+", help="任務標題")
    sub.add_parser("list", help="列出任務")
    p_done = sub.add_parser("done", help="標記完成")
    # 收字串自己轉：合約要求 id 非數字回 exit 1（argparse type=int 會變 2）
    p_done.add_argument("id", help="任務 id")
    return parser


def main(argv=None) -> int:
    """CLI 入口，回傳 exit code。"""
    _use_utf8_console()
    args = _build_parser().parse_args(argv)
    db = _resolve_db(args.db)
    try:
        if args.command == "add":
            task = add_task(db, " ".join(args.title))
            print(f"已新增 #{task['id']}：{task['title']}")
        elif args.command == "list":
            tasks = list_tasks(db)
            if not tasks:
                print("（沒有待辦事項）")
            for t in tasks:
                mark = "x" if t["done"] else " "
                print(f"[{mark}] #{t['id']} {t['title']}")
        elif args.command == "done":
            try:
                task_id = int(args.id)
            except ValueError:
                raise ValueError(f"id 必須是數字：{args.id}") from None
            task = mark_done(db, task_id)
            print(f"已完成 #{task['id']}：{task['title']}")
    except KeyError as e:
        print(f"錯誤：{e.args[0]}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"錯誤：無法存取存檔 {db}（{e.strerror}）", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
