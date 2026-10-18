"""讓 repo 根目錄可被 import（tests/ 內直接 import csv_stats）。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
