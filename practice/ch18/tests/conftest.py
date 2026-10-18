"""pytest 設定：把專案根目錄（tests 的上一層）加進 sys.path，讓 `import todo` 可用。"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
