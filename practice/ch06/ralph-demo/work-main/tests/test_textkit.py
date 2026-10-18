from src.textkit import slugify


def test_slugify_basic_example():
    # 題目範例：標點與空白換成 `-`，結果為小寫
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_merges_and_trims_separators():
    # 連續分隔符合併為單一 `-`，頭尾多餘的 `-` 被去除
    assert slugify("  --Foo!!  Bar--  ") == "foo-bar"
    assert slugify("a___b") == "a-b"


def test_slugify_boundary_empty_and_only_symbols():
    # 邊界案例：空字串與全為非英數字元時皆回傳空字串
    assert slugify("") == ""
    assert slugify("!!!") == ""
