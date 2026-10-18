"""極簡 todo 清單模組（練習用任務專案）"""
import json
from datetime import date, datetime
from pathlib import Path


def _parse_due(item):
    """把 due 字串轉成 date；None 原樣回傳。"""
    due = item.get("due")
    if due is None:
        return None
    try:
        return date.fromisoformat(due)
    except (TypeError, ValueError) as exc:
        # add() 不驗證 due 格式，壞資料要在這裡指出是哪一筆，方便使用者修正
        # 只印 id 與型別名稱，不印原值，避免把檔案內容洩漏到 log／錯誤訊息
        raise ValueError(f"id={item.get('id')} 的 due 格式不合法（型別 {type(due).__name__}）") from exc


DEFAULT_PRIORITY = 3


def _parse_priority(item):
    """驗證 priority：None（或缺欄位）視為預設值 3；bool、非 int、< 1 拋 ValueError。"""
    value = item.get("priority")
    if value is None:
        return DEFAULT_PRIORITY
    # bool 是 int 的子類別，必須明確排除，否則 True 會被當成 1
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"id={item.get('id')} 的 priority 不合法（型別 {type(value).__name__}）")
    return value


class TodoStore:
    """以 JSON 檔保存的 todo 清單"""

    def __init__(self, path):
        self.path = Path(path)
        self.items = []
        if self.path.exists():
            self.items = json.loads(self.path.read_text(encoding="utf-8"))

    def add(self, title, priority=3, due=None):
        if not title or not title.strip():
            raise ValueError("title 不可為空")
        new_id = len(self.items) + 1
        # 在寫入端擋下壞值；None 明確存成預設值 3，讀取端就不必再猜
        valid_priority = _parse_priority({"id": new_id, "priority": priority})
        item = {"id": new_id, "title": title.strip(),
                "priority": valid_priority, "due": due, "done": False}
        self.items.append(item)
        return item

    def done(self, item_id):
        for item in self.items:
            if item["id"] == item_id:
                item["done"] = True
                return item
        raise KeyError(f"找不到 id={item_id}")

    def save(self):
        self.path.write_text(json.dumps(self.items, ensure_ascii=False, indent=2), encoding="utf-8")

    def overdue(self, today):
        """回傳未完成且 due 早於 today 的項目（依 id 排序）"""
        # datetime 是 date 的子類別，必須先判斷，否則與 date 比較會出錯
        if isinstance(today, datetime):
            today = today.date()
        elif not isinstance(today, date):
            raise TypeError(f"today 必須是 datetime.date，收到 {type(today).__name__}")
        result = []
        for item in self.items:
            # 先解析再判斷 done，讓壞資料不論狀態都能被發現
            due_date = _parse_due(item)
            if not item["done"] and due_date is not None and due_date < today:
                result.append(item)
        return sorted(result, key=lambda item: item["id"])

    def sorted_items(self):
        """回傳排序後的新 list，不改動 self.items"""
        def sort_key(item):
            due_date = _parse_due(item)
            # None 不能和 date 比較，用 date.max 佔位；前一欄 due is None 已確保它排最後
            return (item["done"], _parse_priority(item), due_date is None,
                    due_date or date.max, item["id"])
        return sorted(self.items, key=sort_key)
