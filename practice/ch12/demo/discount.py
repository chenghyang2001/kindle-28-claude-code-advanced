"""示範用：計算折扣後價格（給 CI review 乾跑當審查對象）。"""


def apply_discount(price: float, percent: float) -> float:
    """回傳打折後價格；percent 必須介於 0~100。"""
    if not 0 <= percent <= 100:
        raise ValueError("percent 必須介於 0~100")
    return round(price * (100 - percent) / 100, 2)


if __name__ == "__main__":
    assert apply_discount(100, 20) == 80.0
    print("ok")
