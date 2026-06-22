"""
test_app.py — app.py 的 pytest 測試套件。

涵蓋 add_task / list_tasks / delete_task / complete_task 四個函式的：
  - happy path（正常流程）
  - edge / error case（邊界與錯誤路徑）
"""

import pytest

from app import add_task, complete_task, delete_task, list_tasks, _print_task_list


# ---------------------------------------------------------------------------
# add_task 測試
# ---------------------------------------------------------------------------

class TestAddTask:
    """測試 add_task 函式。"""

    def test_add_single_task_happy_path(self):
        """正常新增一筆任務後，清單長度應為 1 且名稱正確。"""
        tasks = []
        add_task(tasks, "買牛奶")
        assert tasks == [{"name": "買牛奶", "done": False}]

    def test_add_multiple_tasks_preserves_order(self):
        """連續新增多筆任務，順序應維持插入順序。"""
        tasks = []
        add_task(tasks, "任務A")
        add_task(tasks, "任務B")
        assert tasks == [{"name": "任務A", "done": False}, {"name": "任務B", "done": False}]

    def test_add_empty_name_raises_value_error(self):
        """空字串名稱應拋出 ValueError（不允許無意義任務）。"""
        tasks = []
        with pytest.raises(ValueError):
            add_task(tasks, "")

    def test_add_whitespace_only_raises_value_error(self):
        """純空白字串也視為空名稱，應拋出 ValueError。"""
        tasks = []
        with pytest.raises(ValueError):
            add_task(tasks, "   ")

    def test_add_task_strips_whitespace(self):
        """名稱前後的空白應被自動去除。"""
        tasks = []
        add_task(tasks, "  洗碗  ")
        assert tasks == [{"name": "洗碗", "done": False}]


# ---------------------------------------------------------------------------
# list_tasks 測試
# ---------------------------------------------------------------------------

class TestListTasks:
    """測試 list_tasks 函式。"""

    def test_list_tasks_returns_copy(self):
        """回傳值應是副本，修改後不影響原始清單。"""
        tasks = [{"name": "任務X", "done": False}]
        result = list_tasks(tasks)
        result.append({"name": "不該出現", "done": False})
        assert tasks == [{"name": "任務X", "done": False}], "原始清單不應被修改"

    def test_list_tasks_empty_list(self):
        """空清單回傳空 list。"""
        assert list_tasks([]) == []

    def test_list_tasks_returns_same_items(self):
        """回傳的項目應與原始清單完全一致。"""
        tasks = [
            {"name": "A", "done": False},
            {"name": "B", "done": True},
            {"name": "C", "done": False},
        ]
        assert list_tasks(tasks) == tasks


# ---------------------------------------------------------------------------
# delete_task 測試
# ---------------------------------------------------------------------------

class TestDeleteTask:
    """測試 delete_task 函式。"""

    def test_delete_existing_task_returns_true(self):
        """刪除存在的任務應回傳 True 並移除該項目。"""
        tasks = [{"name": "報告", "done": False}, {"name": "開會", "done": False}]
        result = delete_task(tasks, "報告")
        assert result is True
        assert tasks == [{"name": "開會", "done": False}]

    def test_delete_nonexistent_task_returns_false(self):
        """刪除不存在的任務名稱應回傳 False，清單不變。"""
        tasks = [{"name": "現有任務", "done": False}]
        result = delete_task(tasks, "不存在的任務")
        assert result is False
        assert tasks == [{"name": "現有任務", "done": False}], "清單不應被修改"

    def test_delete_from_empty_list_returns_false(self):
        """從空清單刪除任何名稱都應回傳 False。"""
        tasks = []
        result = delete_task(tasks, "隨便")
        assert result is False

    def test_delete_only_first_occurrence(self):
        """若清單中有重複名稱，只刪除第一個（list.remove 行為）。"""
        tasks = [{"name": "重複", "done": False}, {"name": "重複", "done": False}]
        delete_task(tasks, "重複")
        assert tasks == [{"name": "重複", "done": False}]


# ---

class TestCompleteTask:
    """測試 complete_task 函式。"""

    def test_complete_existing_task_returns_true_and_marks_done(self):
        """標記存在的任務完成，應回傳 True 且該任務 done 變為 True（COMP-01）。"""
        tasks = [{"name": "報告", "done": False}]
        result = complete_task(tasks, "報告")
        assert result is True
        assert tasks[0]["done"] is True

    def test_complete_nonexistent_task_returns_false(self):
        """標記不存在的任務名稱，應回傳 False 且清單不變（COMP-02）。"""
        tasks = [{"name": "現有任務", "done": False}]
        result = complete_task(tasks, "不存在的任務")
        assert result is False
        assert tasks == [{"name": "現有任務", "done": False}], "清單不應被修改"

    def test_complete_already_done_task_is_idempotent(self):
        """重複標記已完成的任務應回傳 True 且狀態維持 done=True（D-04 冪等）。"""
        tasks = [{"name": "報告", "done": True}]
        result = complete_task(tasks, "報告")
        assert result is True
        assert tasks[0]["done"] is True

    def test_complete_on_empty_list_returns_false(self):
        """對空清單呼叫 complete_task 應回傳 False，不拋錯。"""
        tasks = []
        result = complete_task(tasks, "任何名稱")
        assert result is False


# ---

class TestPrintTaskList:
    """測試 _print_task_list 顯示層的完成標記（COMP-03）。"""

    def test_print_task_list_shows_markers(self, capsys):
        """完成任務顯示 [x]，未完成任務顯示 [ ]（COMP-03 可執行驗證）。"""
        tasks = [
            {"name": "報告", "done": True},
            {"name": "買菜", "done": False},
        ]
        _print_task_list(tasks)
        out = capsys.readouterr().out
        assert "[x] 報告" in out
        assert "[ ] 買菜" in out
