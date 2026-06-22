"""極簡待辦清單 CLI（GSD YOLO 2-phase 練習的 brownfield 起點）。

刻意只實作 3 個核心函式（add / list / delete），且 task 以純字串 str
儲存於 in-memory 的 list[str]。complete / persistence 等功能留給學習者
之後用 GSD autonomous 自動補上的 2 個 phase，因此此處不要先寫。
"""
import json
import os
import sys


def add_task(tasks: list, name: str) -> None:
    """新增一筆 task 到 tasks。

    task 以 dict{"name": str, "done": bool} 儲存，新增時 done 預設 False。
    name 為空字串或純空白時拋 ValueError；存入前先 strip 去除前後空白，
    避免之後 delete / complete 比對時因空白差異而找不到。
    """
    if name is None or not name.strip():
        raise ValueError("task 名稱不可為空白")
    tasks.append({"name": name.strip(), "done": False})


def list_tasks(tasks: list) -> list:
    """回傳 tasks 的淺層 copy。

    回傳 copy 而非原 list，避免呼叫端在外部直接 append / remove
    動到內部儲存（保護封裝）。
    """
    return list(tasks)


def delete_task(tasks: list, name: str) -> bool:
    """刪除第一個 name 相符的 task。

    以 task["name"] 比對（比對前對 name 做 strip，與 add/complete 一致）。
    成功刪除回傳 True；找不到回傳 False（不拋例外，讓呼叫端自行決定後續）。
    """
    target = name.strip() if name else name
    for task in tasks:
        if task["name"] == target:
            tasks.remove(task)
            return True
    return False


def complete_task(tasks: list, name: str) -> bool:
    """把第一個 name 相符的 task 標記為已完成（done=True）。

    比對前對 name 做 strip（與 add/delete 一致）。標記成功回傳 True；
    找不到回傳 False（不拋例外，與 delete_task 一致）。對已完成的 task
    再次標記仍回傳 True 且維持 done=True（idempotent）；只處理第一個相符者。
    """
    target = name.strip() if name else name
    for task in tasks:
        if task["name"] == target:
            task["done"] = True
            return True
    return False


def list_pending(tasks: list) -> list:
    """回傳尚未完成（done=False）的 task 的淺層 copy list。

    維持原始插入順序；空清單或全部完成時回傳 []。回傳為新 list（元素仍為
    原 dict reference），改動回傳值的長度不影響原 tasks。
    """
    return [task for task in tasks if not task["done"]]


def save_tasks(tasks: list, path: str) -> None:
    """把 tasks（含 done 狀態）以 JSON 寫入 path，覆寫既有內容。

    用 "w" 模式開檔（即覆寫），`ensure_ascii=False` 讓中文任務名以字面
    保存（非 \\uXXXX 轉義）、`indent=2` 讓檔案人類可讀。一律 UTF-8 編碼
    （符合 cp950 防禦規則）。空清單 tasks=[] 直接序列化為 "[]"，不需特例。
    不回傳值（回 None）。
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def load_tasks(path: str) -> list:
    """從 path 讀回 list[dict{name, done}]。

    檔案不存在 → 回傳 []（優雅處理，呼應「可預期的沒有回空」慣例，不拋例外）。
    檔案存在但 JSON 格式損壞 → 讓 json.JSONDecodeError 自然往外拋（不靜默吞掉，
    讓呼叫端自行決定後續）。一律 UTF-8 讀取。
    """
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    """簡單互動 CLI loop：支援 add / list / delete / quit。"""
    tasks: list = []
    commands = "指令：add <名稱> / list / delete <名稱> / quit"
    print("極簡待辦清單 CLI")
    print(commands)
    try:
        while True:
            try:
                raw = input("> ").strip()
            except EOFError:
                # 管線輸入結束（如 echo 餵入）時優雅退出，不當成錯誤
                print()
                break
            if not raw:
                continue

            parts = raw.split(maxsplit=1)
            action = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if action == "quit":
                print("再見")
                break
            elif action == "add":
                try:
                    add_task(tasks, arg)
                    print(f"已新增：{arg.strip()}")
                except ValueError as e:
                    print(f"錯誤：{e}", file=sys.stderr)
            elif action == "list":
                current = list_tasks(tasks)
                if not current:
                    print("（清單為空）")
                else:
                    for index, task in enumerate(current, start=1):
                        print(f"{index}. {task['name']}")
            elif action == "delete":
                if delete_task(tasks, arg):
                    print(f"已刪除：{arg.strip()}")
                else:
                    print(f"找不到：{arg.strip()}")
            else:
                print(f"未知指令：{action}")
                print(commands)
    except KeyboardInterrupt:
        print("\n已中斷")


if __name__ == "__main__":
    main()
