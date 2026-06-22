"""app.py 五個核心函式的 pytest 測試（dict 模型版）。

涵蓋 add_task / list_tasks / delete_task / complete_task / list_pending
的 happy path、邊界與冪等性，共 11 個測試。
"""

import pytest

from app import add_task, complete_task, delete_task, list_pending, list_tasks


class TestAddTask:
    """add_task 的行為測試。"""

    def test_add_happy_path(self):
        """正常新增：任務應出現在清單中，且前後空白被 strip。"""
        tasks: list = []
        add_task(tasks, "  買牛奶  ")
        assert tasks == [{"name": "買牛奶", "done": False}]

    def test_add_empty_name_raises(self):
        """空白名稱應拋出 ValueError 且不汙染清單。"""
        tasks: list = []
        with pytest.raises(ValueError):
            add_task(tasks, "   ")
        assert tasks == []


class TestListTasks:
    """list_tasks 的行為測試。"""

    def test_list_happy_path(self):
        """回傳內容應與內部清單的 name 一致。"""
        tasks = [{"name": "a", "done": False}, {"name": "b", "done": False}]
        assert [t["name"] for t in list_tasks(tasks)] == ["a", "b"]

    def test_list_returns_copy(self):
        """回傳的是複本，竄改它不應影響內部清單。"""
        tasks = [{"name": "a", "done": False}]
        returned = list_tasks(tasks)
        returned.append({"name": "b", "done": False})
        assert len(tasks) == 1


class TestDeleteTask:
    """delete_task 的行為測試。"""

    def test_delete_happy_path(self):
        """刪除存在的任務應回傳 True 並移除該項。"""
        tasks = [{"name": "a", "done": False}, {"name": "b", "done": False}]
        assert delete_task(tasks, "a") is True
        assert tasks == [{"name": "b", "done": False}]

    def test_delete_non_existent_returns_false(self):
        """刪除不存在的任務應回傳 False 且清單不變。"""
        tasks = [{"name": "a", "done": False}]
        assert delete_task(tasks, "x") is False
        assert tasks == [{"name": "a", "done": False}]


class TestCompleteTask:
    """complete_task 的行為測試。"""

    def test_complete_happy_path(self):
        """存在的任務標記為完成應回傳 True 且 done 為 True。"""
        tasks = [{"name": "a", "done": False}]
        assert complete_task(tasks, "a") is True
        assert tasks[0]["done"] is True

    def test_complete_not_found_returns_false(self):
        """不存在的任務應回傳 False 且清單不變。"""
        tasks = [{"name": "a", "done": False}]
        assert complete_task(tasks, "x") is False
        assert tasks == [{"name": "a", "done": False}]

    def test_complete_idempotent(self):
        """已完成任務再次標記應仍回傳 True（冪等性）。"""
        tasks = [{"name": "a", "done": True}]
        assert complete_task(tasks, "a") is True
        assert tasks[0]["done"] is True


class TestListPending:
    """list_pending 的行為測試。"""

    def test_list_pending_all_pending(self):
        """全部未完成時，所有任務名稱應出現於回傳清單。"""
        tasks = [{"name": "a", "done": False}, {"name": "b", "done": False}]
        assert list_pending(tasks) == ["a", "b"]

    def test_list_pending_some_done(self):
        """部分已完成時，只有未完成任務的名稱出現。"""
        tasks = [{"name": "a", "done": True}, {"name": "b", "done": False}]
        assert list_pending(tasks) == ["b"]
