"""極簡待辦清單 CLI（GSD YOLO 練習用 starter）。

刻意只保留五個核心函式（add_task / list_tasks / delete_task /
complete_task / list_pending），task 以 dict 形式存放於
in-memory list[dict]，每個任務結構為 {"name": str, "done": bool}。
"""

import copy
import sys


def add_task(tasks: list, name: str) -> None:
    """將任務名稱加入清單。

    Args:
        tasks: 儲存任務的 list[dict]（原地修改）。
        name: 任務名稱；空字串或純空白視為非法。

    Raises:
        ValueError: 當 name 去除前後空白後為空。
    """
    # 先 strip 再判斷，避免「   」這類純空白被當成有效任務
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("任務名稱不可為空白")
    tasks.append({"name": cleaned, "done": False})


def list_tasks(tasks: list) -> list:
    """回傳任務清單的深層複本。

    回傳 deepcopy 而非內部 reference，確保呼叫端無論是對 list 本身
    或對 dict 內的欄位（如 done）進行修改，都不會竄改內部狀態。

    Args:
        tasks: 儲存任務的 list[dict]。

    Returns:
        與內部內容相同、但完全獨立的新 list[dict]。
    """
    return copy.deepcopy(tasks)


def delete_task(tasks: list, name: str) -> bool:
    """刪除第一個符合名稱的任務（不論完成狀態）。

    Args:
        tasks: 儲存任務的 list[dict]（原地修改）。
        name: 要刪除的任務名稱（需完全相符）。

    Returns:
        True 表示有刪到；False 表示清單中不存在該任務。
    """
    for i, task in enumerate(tasks):
        if task["name"] == name:
            tasks.pop(i)
            return True
    return False


def complete_task(tasks: list, name: str) -> bool:
    """將指定名稱的任務標記為已完成。

    若任務已完成，仍回傳 True（冪等性）；若找不到，回傳 False。

    Args:
        tasks: 儲存任務的 list[dict]（原地修改）。
        name: 要標記為完成的任務名稱（需完全相符）。

    Returns:
        True 表示找到並標記成功（或已完成）；False 表示清單中不存在該任務。
    """
    for task in tasks:
        if task["name"] == name:
            task["done"] = True
            return True
    return False


def list_pending(tasks: list) -> list:
    """回傳所有尚未完成的任務名稱字串清單。

    Args:
        tasks: 儲存任務的 list[dict]。

    Returns:
        list[str]，僅包含 done=False 任務的 name 值。
    """
    return [task["name"] for task in tasks if not task["done"]]


def main() -> None:
    """簡單互動式 CLI 主迴圈，支援 add / list / delete / quit 四指令。"""
    tasks: list = []
    print("極簡待辦清單 CLI（指令：add / list / delete / quit）")
    while True:
        try:
            command = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            # 使用者按 Ctrl+D / Ctrl+C 時優雅結束，不留下 traceback
            print()
            break

        if command == "quit":
            break
        elif command == "add":
            name = input("任務名稱：")
            try:
                add_task(tasks, name)
                print(f"已新增：{name.strip()}")
            except ValueError as exc:
                print(f"錯誤：{exc}", file=sys.stderr)
        elif command == "list":
            current = list_tasks(tasks)
            if not current:
                print("（清單為空）")
            else:
                for index, task in enumerate(current, start=1):
                    print(f"{index}. {task['name']}")
        elif command == "delete":
            name = input("要刪除的任務名稱：").strip()
            if delete_task(tasks, name):
                print(f"已刪除：{name}")
            else:
                print(f"找不到任務：{name}", file=sys.stderr)
        else:
            print("未知指令，可用：add / list / delete / quit", file=sys.stderr)


if __name__ == "__main__":
    main()
