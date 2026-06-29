"""
待辦清單 CLI — GSD 練習用的極簡 in-memory 待辦管理模組（brownfield 基底）。

這是「已存在的舊 codebase」，提供三個核心函式：
  add_task / list_tasks / delete_task
學習者需要在此基礎上以 GSD 流程新增第 4 個功能：complete_task。
"""

import sys


def add_task(tasks: list, name: str) -> None:
    """新增一筆待辦任務到 tasks 清單中。

    Args:
        tasks: 現有的任務清單（就地修改）。
        name:  任務名稱字串。

    Raises:
        ValueError: 若 name 為空字串，拒絕新增。
    """
    if not name or not name.strip():
        raise ValueError(f"任務名稱不可為空字串：{name!r}")
    tasks.append(name.strip())


def list_tasks(tasks: list) -> list:
    """回傳目前任務清單的副本，不影響原始資料。

    Args:
        tasks: 現有的任務清單。

    Returns:
        list: tasks 的淺複製。
    """
    return list(tasks)


def delete_task(tasks: list, name: str) -> bool:
    """從清單中刪除指定名稱的任務。

    Args:
        tasks: 現有的任務清單（就地修改）。
        name:  要刪除的任務名稱。

    Returns:
        True  — 成功刪除。
        False — 清單中不存在此名稱。
    """
    if name in tasks:
        tasks.remove(name)
        return True
    return False


def _print_task_list(tasks: list) -> None:
    """輔助函式：把任務清單格式化輸出到 stdout。"""
    if not tasks:
        print("（目前沒有任何待辦任務）")
        return
    for idx, task in enumerate(tasks, start=1):
        print(f"  {idx}. {task}")


def main() -> None:
    """互動式 CLI loop：支援 add / list / delete / quit 四個指令。"""
    tasks: list = []
    print("=== 待辦清單 CLI ===")
    print("指令：add <任務名稱> | list | delete <任務名稱> | quit")
    print()

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已中斷，再見！")
            break

        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "quit":
            print("再見！")
            break

        elif cmd == "add":
            if len(parts) < 2:
                print("用法：add <任務名稱>")
                continue
            try:
                add_task(tasks, parts[1])
                print(f"已新增：{parts[1].strip()}")
            except ValueError as exc:
                print(f"錯誤：{exc}", file=sys.stderr)

        elif cmd == "list":
            _print_task_list(tasks)

        elif cmd == "delete":
            if len(parts) < 2:
                print("用法：delete <任務名稱>")
                continue
            found = delete_task(tasks, parts[1])
            if found:
                print(f"已刪除：{parts[1]}")
            else:
                print(f"找不到任務：{parts[1]!r}")

        else:
            print(f"未知指令：{cmd!r}（可用：add / list / delete / quit）")


if __name__ == "__main__":
    main()
