from src.textkit import is_palindrome


def test_is_palindrome_basic_example():
    # 題目範例：忽略大小寫與標點後為回文
    assert is_palindrome("A man, a plan, a canal: Panama") is True


def test_is_palindrome_non_palindrome():
    # 非回文字串應回傳 False
    assert is_palindrome("hello") is False
    assert is_palindrome("Race a car") is False


def test_is_palindrome_boundary_empty_string():
    # 邊界案例：空字串視為回文，只有符號的字串同樣清理後為空
    assert is_palindrome("") is True
    assert is_palindrome("!!!") is True
