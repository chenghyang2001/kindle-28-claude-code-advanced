from src.textkit import word_count


def test_word_count_basic_example():
    # 基本案例：大小寫視為同一單字，標點被當作分隔符號
    assert word_count("Hello, hello World!") == {"hello": 2, "world": 1}


def test_word_count_splits_on_non_alnum():
    # 非英數字元（空白、連字號、底線等）都應切分單字
    assert word_count("a-b_c d") == {"a": 1, "b": 1, "c": 1, "d": 1}
    assert word_count("the the THE") == {"the": 3}


def test_word_count_boundary_empty_string():
    # 邊界案例：空字串與只含符號的字串都回傳空 dict
    assert word_count("") == {}
    assert word_count("!!! ???") == {}
