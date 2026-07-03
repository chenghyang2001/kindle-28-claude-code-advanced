"""greet.py — 簡易問候語產生器

提供 greet() 函式，依輸入的姓名產生繁體中文問候語；
若姓名為空字串或 None，則回傳預設的「陌生人」問候語，
避免呼叫端因忘記檢查空值而產生不友善的輸出（例如「你好，！」）。
"""


def greet(name: str) -> str:
    """回傳繁體中文問候語。

    Args:
        name: 要問候的對象名稱。若為 None 或空字串（含全空白字串），
            視為未提供有效姓名。

    Returns:
        若 name 為有效字串，回傳 "你好，<name>！"；
        若 name 為 None、空字串或全空白字串，回傳 "你好，陌生人！"。
    """
    # 用 strip() 判斷是否為「有意義的空值」，避免 "   " 這種
    # 純空白字串被誤判為有效姓名而印出「你好，   ！」這種怪異輸出。
    if name is None or name.strip() == "":
        return "你好，陌生人！"
    return f"你好，{name}！"


if __name__ == "__main__":
    # 冒煙測試：正常輸入與空字串輸入皆須通過，確保基本行為正確。
    assert greet("小明") == "你好，小明！"
    assert greet("") == "你好，陌生人！"
    assert greet(None) == "你好，陌生人！"
    assert greet("   ") == "你好，陌生人！"

    print("greet.py 冒煙測試通過")
