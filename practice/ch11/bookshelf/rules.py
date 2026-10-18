"""純函式：ISBN 驗證、日期解析、罰金計算（單元測試的主要對象）。"""
from datetime import date

DAILY_FINE = 5      # 每逾期一天罰 5 元
FINE_CAP = 200      # 罰金上限，避免長期逾期罰到不合理


class ValidationError(ValueError):
    """輸入資料不合法。"""


def normalize_isbn(raw: str) -> str:
    """去掉連字號與空白，並轉大寫（ISBN-10 結尾可為 X）。"""
    if raw is None:
        raise ValidationError("ISBN 不可為空")
    return raw.replace("-", "").replace(" ", "").upper()


def is_valid_isbn(raw: str) -> bool:
    """驗證 ISBN-10 或 ISBN-13 的檢查碼。"""
    isbn = normalize_isbn(raw)
    if len(isbn) == 10:
        if not isbn[:9].isdigit() or not (isbn[9].isdigit() or isbn[9] == "X"):
            return False
        digits = [int(c) for c in isbn[:9]] + [10 if isbn[9] == "X" else int(isbn[9])]
        return sum((10 - i) * d for i, d in enumerate(digits)) % 11 == 0
    if len(isbn) == 13:
        if not isbn.isdigit():
            return False
        total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(isbn))
        return total % 10 == 0
    return False


def parse_date(text: str) -> date:
    """解析 YYYY-MM-DD，失敗時丟 ValidationError（讓 CLI 能顯示友善訊息）。"""
    try:
        return date.fromisoformat(text)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"日期格式錯誤：{text!r}（需 YYYY-MM-DD）") from exc


def calc_fine(due: date, returned: date) -> int:
    """逾期罰金：準時或提早為 0，之後每天 DAILY_FINE，最多 FINE_CAP。"""
    late_days = (returned - due).days
    if late_days <= 0:
        return 0
    return min(late_days * DAILY_FINE, FINE_CAP)
