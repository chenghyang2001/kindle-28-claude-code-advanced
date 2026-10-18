"""overdue() 與 sorted_items() 測試"""
import copy
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from todo import TodoStore  # noqa: E402

SAMPLE = ROOT / "data" / "sample-todos.json"
TODAY = date(2026, 10, 18)


@pytest.fixture
def sample_store(tmp_path):
    # 複製到 tmp_path，確保測試絕不會寫回 data/
    target = tmp_path / "sample.json"
    shutil.copy(SAMPLE, target)
    return TodoStore(target)


def make_store(tmp_path, items):
    store = TodoStore(tmp_path / "t.json")
    store.items = items
    return store


def item(item_id, priority=3, due=None, done=False):
    return {"id": item_id, "title": f"t{item_id}", "priority": priority, "due": due, "done": done}


# ---------- happy ----------
def test_overdue_sample(sample_store):
    assert [i["id"] for i in sample_store.overdue(TODAY)] == [1]


def test_sorted_items_sample(sample_store):
    # id1 與 id4 同為 priority 1，依合約「due 早者優先」，10-15 的 id1 排在 10-18 的 id4 之前
    assert [i["id"] for i in sample_store.sorted_items()] == [1, 4, 2, 3]


def test_overdue_accepts_datetime(sample_store):
    assert [i["id"] for i in sample_store.overdue(datetime(2026, 10, 18, 23, 59))] == [1]


# ---------- edge ----------
def test_empty_store(tmp_path):
    store = TodoStore(tmp_path / "empty.json")
    assert store.overdue(TODAY) == []
    assert store.sorted_items() == []


def test_due_equal_today_not_overdue(tmp_path):
    store = make_store(tmp_path, [item(1, due="2026-10-18")])
    assert store.overdue(TODAY) == []


def test_due_none_not_overdue_and_sorted_last(tmp_path):
    store = make_store(tmp_path, [item(1, priority=1, due=None), item(2, priority=1, due="2030-01-01")])
    assert store.overdue(TODAY) == []
    assert [i["id"] for i in store.sorted_items()] == [2, 1]


def test_done_items_excluded(tmp_path):
    store = make_store(tmp_path, [item(1, due="2020-01-01", done=True)])
    assert store.overdue(TODAY) == []


def test_tie_broken_by_id(tmp_path):
    store = make_store(tmp_path, [item(3, 2, "2026-11-01"), item(1, 2, "2026-11-01"), item(2, 2, "2026-11-01")])
    assert [i["id"] for i in store.sorted_items()] == [1, 2, 3]


def test_overdue_sorted_by_id(tmp_path):
    store = make_store(tmp_path, [item(5, due="2026-01-01"), item(2, due="2026-02-01")])
    assert [i["id"] for i in store.overdue(TODAY)] == [2, 5]


def test_sorted_items_does_not_mutate(sample_store):
    before = copy.deepcopy(sample_store.items)
    result = sample_store.sorted_items()
    assert sample_store.items == before
    assert result is not sample_store.items


# ---------- error ----------
def test_invalid_due_raises_with_id(tmp_path):
    store = make_store(tmp_path, [item(1, due="2026-10-01"), item(7, due="2026/10/01")])
    with pytest.raises(ValueError, match="id=7"):
        store.overdue(TODAY)
    with pytest.raises(ValueError, match="id=7"):
        store.sorted_items()


def test_today_string_raises_type_error(sample_store):
    with pytest.raises(TypeError):
        sample_store.overdue("2026-10-18")


# ---------- priority 驗證（04-debate 結論） ----------
def test_add_priority_none_stored_as_default(tmp_path):
    # 決定：add() 遇到 None 直接把 priority 存成 3（而非留 None 到排序時才補）
    store = TodoStore(tmp_path / "t.json")
    assert store.add("x", priority=None)["priority"] == 3
    assert store.items[0]["priority"] == 3


@pytest.mark.parametrize("bad", ["1", 1.0, True, 0, -1])
def test_add_invalid_priority_raises_and_items_unchanged(tmp_path, bad):
    store = TodoStore(tmp_path / "t.json")
    store.add("先放一筆", priority=2)
    before = copy.deepcopy(store.items)
    with pytest.raises(ValueError, match="id=2"):
        store.add("壞資料", priority=bad)
    assert store.items == before


def test_sorted_items_loaded_string_priority_raises(tmp_path):
    # 模擬 JSON 檔被手動改壞：priority 為字串 "1"
    path = tmp_path / "t.json"
    path.write_text('[{"id": 9, "title": "t", "priority": "1", "due": null, "done": false}]',
                    encoding="utf-8")
    store = TodoStore(path)
    with pytest.raises(ValueError) as exc_info:
        store.sorted_items()
    msg = str(exc_info.value)
    assert "id=9" in msg
    assert "'1'" not in msg and '"1"' not in msg
    assert "str" in msg


def test_invalid_due_message_hides_raw_value(tmp_path):
    store = make_store(tmp_path, [item(7, due="2026/10/01")])
    with pytest.raises(ValueError) as exc_info:
        store.overdue(TODAY)
    msg = str(exc_info.value)
    assert "id=7" in msg
    assert "2026/10/01" not in msg
