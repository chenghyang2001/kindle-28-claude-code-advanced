"""設定檔讀寫（JSON 格式，存在 CFGCLI_HOME 或 ~/.cfgcli/config.json）。"""
import json
import os
from pathlib import Path


def config_path() -> Path:
    """取得設定檔路徑；測試時用 CFGCLI_HOME 指到暫存目錄，避免動到真實家目錄。"""
    home = os.environ.get("CFGCLI_HOME")
    base = Path(home) if home is not None else Path.home() / ".cfgcli"
    return base / "config.json"


def load_config() -> dict:
    path = config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"設定檔格式錯誤：{path}（{e}）") from e


def save_config(config: dict) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
