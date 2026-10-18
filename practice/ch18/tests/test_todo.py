"""todo.py 契約測試：只依 PLAN.md「介面合約」撰寫，不依賴實作細節。"""
import json

import pytest

import todo


@pytest.fixture
def db(tmp_path, monkeypatch):
    """每個測試獨立的存檔路徑；清掉 TODO_DB 避免外部環境干擾。"""
    monkeypatch.delenv("TODO_DB", raising=False)
    return tmp_path / "todo.json"


# ---------- 函式層 ----------

def test_load_missing_file_returns_empty(db):
    assert todo.load_tasks(db) == []


def test_load_broken_json_raises_value_error(db):
    db.write_text("{ 這不是 JSON", encoding="utf-8")
    with pytest.raises(ValueError):
        todo.load_tasks(db)


def test_add_ids_increment_from_one(db):
    first = todo.add_task(db, "買牛奶")
    second = todo.add_task(db, "寫報告")
    assert first == {"id": 1, "title": "買牛奶", "done": False}
    assert second["id"] == 2


def test_add_strips_whitespace(db):
    task = todo.add_task(db, "   買牛奶  \t")
    assert task["title"] == "買牛奶"
    assert todo.load_tasks(db)[0]["title"] == "買牛奶"


@pytest.mark.parametrize("title", ["", "   ", "\t\n"])
def test_add_blank_title_raises_value_error(db, title):
    with pytest.raises(ValueError):
        todo.add_task(db, title)


def test_list_sorted_by_id(db):
    # 故意以亂序存檔，確認 list_tasks 會依 id 排序
    todo.save_tasks(db, [
        {"id": 3, "title": "c", "done": False},
        {"id": 1, "title": "a", "done": True},
        {"id": 2, "title": "b", "done": False},
    ])
    assert [t["id"] for t in todo.list_tasks(db)] == [1, 2, 3]


def test_mark_done_sets_done_true(db):
    todo.add_task(db, "買牛奶")
    task = todo.mark_done(db, 1)
    assert task["done"] is True
    assert todo.load_tasks(db)[0]["done"] is True


def test_mark_done_missing_id_raises_key_error(db):
    todo.add_task(db, "買牛奶")
    with pytest.raises(KeyError):
        todo.mark_done(db, 99)


def test_mark_done_twice_is_ok(db):
    todo.add_task(db, "買牛奶")
    todo.mark_done(db, 1)
    task = todo.mark_done(db, 1)
    assert task["done"] is True


def test_chinese_saved_without_unicode_escape(db):
    todo.add_task(db, "買牛奶")
    raw_text = db.read_text(encoding="utf-8")
    assert "買牛奶" in raw_text
    assert "\\u" not in raw_text
    # 仍須是合法 JSON
    assert json.loads(raw_text)[0]["title"] == "買牛奶"


def test_next_id_is_max_plus_one_after_gap(db):
    # 模擬刪除中間任務 #2 後的資料：下一個 id 應為 3+1，而非 len+1
    todo.save_tasks(db, [
        {"id": 1, "title": "a", "done": False},
        {"id": 3, "title": "c", "done": False},
    ])
    assert todo.add_task(db, "d")["id"] == 4


# ---------- CLI 層 ----------

def test_cli_add_list_done_flow(db, capsys):
    assert todo.main(["--db", str(db), "add", "買", "牛奶"]) == 0
    assert "已新增 #1：買 牛奶" in capsys.readouterr().out

    assert todo.main(["--db", str(db), "list"]) == 0
    assert "[ ] #1 買 牛奶" in capsys.readouterr().out

    assert todo.main(["--db", str(db), "done", "1"]) == 0
    assert "已完成 #1：買 牛奶" in capsys.readouterr().out

    assert todo.main(["--db", str(db), "list"]) == 0
    assert "[x] #1 買 牛奶" in capsys.readouterr().out


def test_cli_list_empty(db, capsys):
    assert todo.main(["--db", str(db), "list"]) == 0
    assert "（沒有待辦事項）" in capsys.readouterr().out


def test_cli_done_missing_id_returns_1_stderr(db, capsys):
    todo.add_task(db, "買牛奶")
    assert todo.main(["--db", str(db), "done", "99"]) == 1
    captured = capsys.readouterr()
    assert captured.err.strip() != ""
    assert "已完成" not in captured.out


def test_cli_done_non_numeric_returns_1(db, capsys):
    todo.add_task(db, "買牛奶")
    assert todo.main(["--db", str(db), "done", "abc"]) == 1
    assert capsys.readouterr().err.strip() != ""


def test_cli_db_option_overrides_env(tmp_path, monkeypatch, capsys):
    env_db = tmp_path / "env.json"
    opt_db = tmp_path / "opt.json"
    monkeypatch.setenv("TODO_DB", str(env_db))
    assert todo.main(["--db", str(opt_db), "add", "買牛奶"]) == 0
    assert opt_db.exists()
    assert not env_db.exists()


# ---------- review 後補的情境 ----------

@pytest.mark.parametrize("content", [
    "{}",                                         # 不是陣列
    "[1, 2]",                                     # 元素不是 dict
    '[{"title": "x", "done": false}]',            # 少了 id
    '[{"id": true, "title": "x", "done": false}]',  # id 是 bool
    '[{"id": "1", "title": "x", "done": false}]',   # id 是字串
])
def test_load_invalid_task_raises_value_error(db, content):
    db.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        todo.load_tasks(db)


def test_load_accepts_utf8_bom(db):
    db.write_text('[{"id": 1, "title": "買牛奶", "done": false}]', encoding="utf-8-sig")
    assert todo.load_tasks(db)[0]["title"] == "買牛奶"


def test_save_leaves_no_tmp_file(db):
    todo.add_task(db, "買牛奶")
    assert [p.name for p in db.parent.iterdir()] == ["todo.json"]


def test_cli_invalid_task_file_returns_1(db, capsys):
    db.write_text("[1, 2]", encoding="utf-8")
    assert todo.main(["--db", str(db), "list"]) == 1
    assert "錯誤" in capsys.readouterr().err


def test_cli_db_is_directory_returns_1(tmp_path, capsys):
    assert todo.main(["--db", str(tmp_path), "add", "買牛奶"]) == 1
    assert "錯誤" in capsys.readouterr().err


def test_cli_blank_title_returns_1(db, capsys):
    assert todo.main(["--db", str(db), "add", "   "]) == 1
    assert capsys.readouterr().err.strip() != ""


def test_cli_uses_todo_db_env(tmp_path, monkeypatch):
    env_db = tmp_path / "env.json"
    monkeypatch.setenv("TODO_DB", str(env_db))
    assert todo.main(["add", "買牛奶"]) == 0
    assert env_db.exists()
