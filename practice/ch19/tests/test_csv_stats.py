"""依 SPEC.md 合約撰寫的 csv_stats 測試（不依賴目前實作細節）。"""
import json
from pathlib import Path

import pytest

import csv_stats

SALES_CSV = Path(__file__).resolve().parent.parent / "data" / "sales.csv"


@pytest.fixture
def sales_rows():
    return csv_stats.read_rows(SALES_CSV)


def write_csv(tmp_path, text, name="t.csv"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


# ---------- SPEC §1 中位數 ----------

def test_median_odd_count():
    rows = [{"v": "3"}, {"v": "1"}, {"v": "2"}]
    assert csv_stats.column_stats(rows, "v")["median"] == pytest.approx(2)


def test_median_even_count_averages_middle_two():
    rows = [{"v": "4"}, {"v": "1"}, {"v": "3"}, {"v": "2"}]
    assert csv_stats.column_stats(rows, "v")["median"] == pytest.approx(2.5)


def test_median_ignores_missing_values():
    rows = [{"v": "1"}, {"v": ""}, {"v": "5"}]
    stats = csv_stats.column_stats(rows, "v")
    assert stats["count"] == 2
    assert stats["median"] == pytest.approx(3)


def test_median_none_when_no_values():
    rows = [{"v": ""}, {"v": "  "}]
    stats = csv_stats.column_stats(rows, "v")
    assert stats["count"] == 0
    assert stats["median"] is None


# ---------- SPEC §5 範例資料預期值 ----------

def test_overall_units_on_sales(sales_rows):
    units = csv_stats.compute_stats(sales_rows)["units"]
    assert units["count"] == 9
    assert units["sum"] == pytest.approx(64)
    assert units["median"] == pytest.approx(7)


def test_grouped_sales_expected_values(sales_rows):
    result = csv_stats.compute_grouped_stats(sales_rows, "region")
    north = result["North"]["units"]
    assert north["count"] == 4
    assert north["sum"] == pytest.approx(28)
    assert north["mean"] == pytest.approx(7)
    assert north["median"] == pytest.approx(7)

    south = result["South"]["units"]
    assert south["count"] == 2
    assert south["median"] == pytest.approx(6)

    assert result["East"]["price"]["median"] == pytest.approx(3.5)


# ---------- SPEC §2 分組統計 ----------

def test_grouped_keys_sorted_alphabetically(sales_rows):
    result = csv_stats.compute_grouped_stats(sales_rows, "region")
    assert list(result.keys()) == ["East", "North", "South"]


def test_grouped_excludes_group_by_and_non_numeric(sales_rows):
    result = csv_stats.compute_grouped_stats(sales_rows, "region")
    for group_stats in result.values():
        assert set(group_stats.keys()) == {"units", "price"}


def test_grouped_excludes_group_by_even_if_numeric(sales_rows):
    result = csv_stats.compute_grouped_stats(sales_rows, "units")
    for group_stats in result.values():
        assert "units" not in group_stats
        assert "price" in group_stats


def test_grouped_empty_group_value_goes_to_placeholder(tmp_path):
    path = write_csv(tmp_path, "g,v\nA,1\n,2\n,4\n")
    result = csv_stats.compute_grouped_stats(csv_stats.read_rows(path), "g")
    assert "(空)" in result
    assert "" not in result
    assert result["(空)"]["v"]["count"] == 2
    assert result["(空)"]["v"]["median"] == pytest.approx(3)
    assert result["A"]["v"]["count"] == 1


def test_grouped_numeric_detection_uses_all_rows(tmp_path):
    # B 組的 x 全空，但 x 以全體判定為數值欄位 → B 組仍要有 x（count 0、median None）
    path = write_csv(tmp_path, "g,x\nA,1\nA,3\nB,\n")
    result = csv_stats.compute_grouped_stats(csv_stats.read_rows(path), "g")
    assert result["B"]["x"]["count"] == 0
    assert result["B"]["x"]["median"] is None
    assert result["A"]["x"]["median"] == pytest.approx(2)


def test_grouped_missing_group_by_raises_keyerror(sales_rows):
    with pytest.raises(KeyError):
        csv_stats.compute_grouped_stats(sales_rows, "no_such_col")


# ---------- SPEC §3 欄位篩選 ----------

def test_compute_stats_columns_order_follows_input(sales_rows):
    result = csv_stats.compute_stats(sales_rows, columns=["price", "units"])
    assert list(result.keys()) == ["price", "units"]


def test_compute_stats_columns_subset(sales_rows):
    result = csv_stats.compute_stats(sales_rows, columns=["price"])
    assert list(result.keys()) == ["price"]


def test_compute_stats_columns_none_means_all_numeric(sales_rows):
    result = csv_stats.compute_stats(sales_rows, columns=None)
    assert set(result.keys()) == {"units", "price"}


def test_compute_stats_unknown_column_raises_keyerror(sales_rows):
    with pytest.raises(KeyError):
        csv_stats.compute_stats(sales_rows, columns=["nope"])


def test_compute_stats_non_numeric_column_raises_valueerror(sales_rows):
    with pytest.raises(ValueError):
        csv_stats.compute_stats(sales_rows, columns=["product"])


def test_grouped_columns_filter_and_order(sales_rows):
    result = csv_stats.compute_grouped_stats(sales_rows, "region", columns=["price", "units"])
    for group_stats in result.values():
        assert list(group_stats.keys()) == ["price", "units"]


def test_grouped_unknown_column_raises_keyerror(sales_rows):
    with pytest.raises(KeyError):
        csv_stats.compute_grouped_stats(sales_rows, "region", columns=["nope"])


def test_grouped_non_numeric_column_raises_valueerror(sales_rows):
    with pytest.raises(ValueError):
        csv_stats.compute_grouped_stats(sales_rows, "region", columns=["product"])


# ---------- SPEC §6 向下相容 ----------

def test_compute_stats_backward_compatible_positional(sales_rows):
    result = csv_stats.compute_stats(sales_rows)
    assert set(result.keys()) == {"units", "price"}
    for key in ("count", "sum", "mean", "min", "max", "median"):
        assert key in result["units"]


# ---------- SPEC §4 CLI ----------

def test_cli_plain_returns_0_and_valid_json(capsys):
    assert csv_stats.main([str(SALES_CSV)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["units"]["count"] == 9
    assert data["units"]["median"] == pytest.approx(7)


def test_cli_group_by_and_columns(capsys):
    code = csv_stats.main([str(SALES_CSV), "--group-by", "region", "--columns", "units"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert list(data.keys()) == ["East", "North", "South"]
    assert list(data["North"].keys()) == ["units"]
    assert data["North"]["units"]["sum"] == pytest.approx(28)


@pytest.mark.parametrize(
    "extra_args",
    [
        ["--group-by", "no_such_col"],   # KeyError
        ["--columns", "nope"],           # KeyError
        ["--columns", "product"],        # ValueError
    ],
)
def test_cli_contract_errors_return_1(capsys, extra_args):
    assert csv_stats.main([str(SALES_CSV), *extra_args]) == 1
    captured = capsys.readouterr()
    assert "錯誤" in captured.err
    assert "Traceback" not in captured.err


def test_cli_missing_file_returns_1(capsys, tmp_path):
    assert csv_stats.main([str(tmp_path / "missing.csv")]) == 1
    captured = capsys.readouterr()
    assert "錯誤" in captured.err
    assert "Traceback" not in captured.err
