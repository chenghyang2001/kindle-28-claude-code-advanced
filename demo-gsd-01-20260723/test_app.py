"""demo-gsd-01-20260630 — 基底測試套件（12 個測試，字串型態）"""
import pytest
from app import add_task, list_tasks, delete_task


class TestAddTask:
    def test_add_single_task_happy_path(self):
        tasks = []
        add_task(tasks, "買牛奶")
        assert tasks == ["買牛奶"]

    def test_add_multiple_tasks_preserves_order(self):
        tasks = []
        add_task(tasks, "任務A")
        add_task(tasks, "任務B")
        assert tasks == ["任務A", "任務B"]

    def test_add_empty_name_raises_value_error(self):
        tasks = []
        with pytest.raises(ValueError):
            add_task(tasks, "")

    def test_add_whitespace_only_raises_value_error(self):
        tasks = []
        with pytest.raises(ValueError):
            add_task(tasks, "   ")

    def test_add_task_strips_whitespace(self):
        tasks = []
        add_task(tasks, "  買牛奶  ")
        assert tasks == ["買牛奶"]


class TestListTasks:
    def test_list_tasks_returns_copy(self):
        tasks = ["任務A"]
        result = list_tasks(tasks)
        result.append("任務B")
        assert tasks == ["任務A"]

    def test_list_tasks_empty_list(self):
        assert list_tasks([]) == []

    def test_list_tasks_returns_same_items(self):
        tasks = ["任務A", "任務B"]
        assert list_tasks(tasks) == ["任務A", "任務B"]


class TestDeleteTask:
    def test_delete_existing_task_returns_true(self):
        tasks = ["任務A"]
        assert delete_task(tasks, "任務A") is True
        assert tasks == []

    def test_delete_nonexistent_task_returns_false(self):
        tasks = ["任務A"]
        assert delete_task(tasks, "不存在") is False
        assert tasks == ["任務A"]

    def test_delete_from_empty_list_returns_false(self):
        assert delete_task([], "任務A") is False

    def test_delete_only_first_occurrence(self):
        tasks = ["任務A", "任務A"]
        delete_task(tasks, "任務A")
        assert tasks == ["任務A"]
