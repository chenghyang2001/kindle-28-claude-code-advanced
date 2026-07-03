"""farewell.py — 簡易道別語產生器

提供 farewell() 函式，依輸入的姓名產生繁體中文道別語；
若姓名為空字串、None 或純空白字串，則回傳預設的「陌生人」道別語，
避免呼叫端因忘記檢查空值而產生不友善的輸出（例如「再見，！」）。
"""


def farewell(name: str) -> str:
    """回傳繁體中文道別語。

    Args:
        name: 要道別的對象名稱。若為 None 或空字串（含全空白字串），
            視為未提供有效姓名。

    Returns:
        若 name 為有效字串，回傳 "再見，<name>！"；
        若 name 為 None、空字串或全空白字串，回傳 "再見，陌生人！"。
    """
    # 用 strip() 判斷是否為「有意義的空值」，避免 "   " 這種
    # 純空白字串被誤判為有效姓名而印出「再見，   ！」這種怪異輸出。
    if name is None or name.strip() == "":
        return "再見，陌生人！"
    return f"再見，{name}！"


if __name__ == "__main__":
    # 冒煙測試：正常輸入、空字串、None 三種情況皆須通過，確保基本行為正確。
    assert farewell("小明") == "再見，小明！"
    assert farewell("") == "再見，陌生人！"
    assert farewell(None) == "再見，陌生人！"

    print("farewell.py 冒煙測試通過")
