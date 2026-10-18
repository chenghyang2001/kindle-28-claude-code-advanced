"""故意互相矛盾的測試：任何實作都不可能全綠，用來證明「紅燈即停」護欄。"""
from src.parity import is_even


def test_two_is_even():
    assert is_even(2) is True


def test_two_is_not_even_trap():
    # 陷阱：與上一個測試矛盾
    assert is_even(2) is False
