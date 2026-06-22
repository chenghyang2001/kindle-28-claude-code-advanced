"""app.py 函式的 pytest 測試（GSD YOLO 練習）。

task 已從純字串遷移為 dict{"name": str, "done": bool}。涵蓋
add_task / list_tasks / delete_task（既有 6 個，已對齊 dict 模型）
與 Status 階段新增的 complete_task / list_pending。
"""
import json

import pytest

from app import (
    add_task,
    complete_task,
    delete_task,
    list_pending,
    list_tasks,
    load_tasks,
    save_tasks,
)


class TestAddTask:
    """add_task：新增與空白名稱驗證。"""

    def test_add_happy_path(self):
        """正常新增一筆，存入後為 dict、name 已 strip、done 預設 False。"""
        tasks: list = []
        add_task(tasks, "  買牛奶  ")
        assert tasks == [{"name": "買牛奶", "done": False}]

    def test_add_empty_name_raises(self):
        """空字串與純空白都應拋 ValueError。"""
        tasks: list = []
        with pytest.raises(ValueError):
            add_task(tasks, "")
        with pytest.raises(ValueError):
            add_task(tasks, "   ")


class TestListTasks:
    """list_tasks：回傳內容與 copy 行為。"""

    def test_list_happy_path(self):
        """回傳的內容與目前儲存一致。"""
        tasks = [{"name": "a", "done": False}, {"name": "b", "done": False}]
        assert list_tasks(tasks) == [
            {"name": "a", "done": False},
            {"name": "b", "done": False},
        ]

    def test_list_returns_copy(self):
        """回傳的是淺層 copy，改動回傳值不影響原 list。"""
        tasks = [{"name": "a", "done": False}]
        returned = list_tasks(tasks)
        returned.append({"name": "b", "done": False})
        assert tasks == [{"name": "a", "done": False}]


class TestDeleteTask:
    """delete_task：刪除成功與找不到。"""

    def test_delete_happy_path(self):
        """刪除存在的 task 回傳 True 並移除（以 name 比對，含 strip）。"""
        tasks = [
            {"name": "買牛奶", "done": False},
            {"name": "寫程式", "done": False},
        ]
        assert delete_task(tasks, " 買牛奶 ") is True
        assert tasks == [{"name": "寫程式", "done": False}]

    def test_delete_non_existent_returns_false(self):
        """刪除不存在的 task 回傳 False，list 不變。"""
        tasks = [{"name": "買牛奶", "done": False}]
        assert delete_task(tasks, "不存在") is False
        assert tasks == [{"name": "買牛奶", "done": False}]


class TestCompleteTask:
    """complete_task：標記完成、strip、idempotent、找不到。"""

    def test_complete_happy_path(self):
        """標記未完成的 task → 回 True 且該 task done 變 True。"""
        tasks = [{"name": "買牛奶", "done": False}]
        assert complete_task(tasks, "買牛奶") is True
        assert tasks[0]["done"] is True

    def test_complete_strips_name(self):
        """name 前後帶空白仍能比對成功並標記完成。"""
        tasks = [{"name": "買牛奶", "done": False}]
        assert complete_task(tasks, "  買牛奶  ") is True
        assert tasks[0]["done"] is True

    def test_complete_idempotent(self):
        """對已完成的 task 再標記 → 仍回 True 且 done 維持 True。"""
        tasks = [{"name": "買牛奶", "done": True}]
        assert complete_task(tasks, "買牛奶") is True
        assert tasks[0]["done"] is True

    def test_complete_marks_only_first_match(self):
        """多個同名 task 只標記第一個相符者。"""
        tasks = [
            {"name": "買牛奶", "done": False},
            {"name": "買牛奶", "done": False},
        ]
        assert complete_task(tasks, "買牛奶") is True
        assert tasks[0]["done"] is True
        assert tasks[1]["done"] is False

    def test_complete_not_found_returns_false(self):
        """找不到 name → 回 False，tasks 完全不變。"""
        tasks = [{"name": "買牛奶", "done": False}]
        assert complete_task(tasks, "不存在") is False
        assert tasks == [{"name": "買牛奶", "done": False}]


class TestListPending:
    """list_pending：只回未完成、保序、空回 []、淺 copy。"""

    def test_pending_happy_path(self):
        """混合狀態時只回 done=False 的 task，並維持原插入順序。"""
        tasks = [
            {"name": "a", "done": False},
            {"name": "b", "done": True},
            {"name": "c", "done": False},
        ]
        pending = list_pending(tasks)
        assert pending == [
            {"name": "a", "done": False},
            {"name": "c", "done": False},
        ]

    def test_pending_all_done_returns_empty(self):
        """全部完成時回 []。"""
        tasks = [{"name": "a", "done": True}, {"name": "b", "done": True}]
        assert list_pending(tasks) == []

    def test_pending_empty_list_returns_empty(self):
        """空清單回 []。"""
        assert list_pending([]) == []

    def test_pending_returns_copy(self):
        """回傳為淺 copy，append 回傳值不改動原 tasks 長度。"""
        tasks = [{"name": "a", "done": False}]
        pending = list_pending(tasks)
        pending.append({"name": "b", "done": False})
        assert len(tasks) == 1


class TestPersistence:
    """save_tasks / load_tasks：round-trip 無損、空清單、缺檔、壞 JSON。"""

    def test_round_trip_lossless(self, tmp_path):
        """混合 done 狀態 + 多筆順序 + 中文 name，save→load 後完全相等（含順序）。"""
        path = str(tmp_path / "tasks.json")
        data = [
            {"name": "買牛奶", "done": True},
            {"name": "寫程式", "done": False},
            {"name": "睡覺", "done": True},
        ]
        save_tasks(data, path)
        assert load_tasks(path) == data

    def test_empty_list_round_trip(self, tmp_path):
        """空清單 save→load 回 []，不報錯。"""
        path = str(tmp_path / "tasks.json")
        save_tasks([], path)
        assert load_tasks(path) == []

    def test_missing_file_returns_empty(self, tmp_path):
        """檔案不存在時 load_tasks 回 []（不拋例外）。"""
        assert load_tasks(str(tmp_path / "missing.json")) == []

    def test_malformed_json_raises(self, tmp_path):
        """格式損壞的 JSON 檔讓 json.JSONDecodeError 自然往外拋（不被吞）。"""
        bad = tmp_path / "bad.json"
        bad.write_text("{壞 not json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_tasks(str(bad))
