"""todo 基本行為測試"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from todo import TodoStore  # noqa: E402


def test_add_and_done(tmp_path):
    store = TodoStore(tmp_path / "t.json")
    item = store.add("買牛奶", priority=1)
    assert item["id"] == 1
    store.done(1)
    assert store.items[0]["done"] is True


def test_empty_title(tmp_path):
    with pytest.raises(ValueError):
        TodoStore(tmp_path / "t.json").add("  ")


def test_save_roundtrip(tmp_path):
    p = tmp_path / "t.json"
    store = TodoStore(p)
    store.add("寫報告", due="2026-10-20")
    store.save()
    assert TodoStore(p).items[0]["title"] == "寫報告"
