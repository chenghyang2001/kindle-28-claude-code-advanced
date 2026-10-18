"""特徵測試：legacy_order.calc 的輸出快照。"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from cases import CASES  # noqa: E402
import legacy_order  # noqa: E402

SNAPSHOT = ROOT / "tests" / "snapshot.json"


class TestCharacterization(unittest.TestCase):
    def test_snapshot_matches(self):
        expected = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        actual = [legacy_order.calc(o, t) for o, t in CASES]
        self.assertEqual(actual, expected)

    def test_bad_qty_raises(self):
        with self.assertRaises(ValueError):
            legacy_order.calc({"items": [{"price": 1, "qty": 0}]})


if __name__ == "__main__":
    unittest.main()
