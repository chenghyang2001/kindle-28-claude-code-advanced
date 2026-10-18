import re


def slugify(text):
    """將文字轉為 URL 友善的 slug：轉小寫、非英數字元換成 `-`、合併連續 `-`、去除頭尾 `-`。"""
    lowered = text.lower()
    # 連續的非英數字元（含 `-`）一次替換成單一 `-`
    replaced = re.sub(r"[^a-z0-9]+", "-", lowered)
    return replaced.strip("-")


def is_palindrome(s):
    """判斷字串是否為回文：忽略大小寫與非英數字元。空字串視為回文。"""
    # 先轉小寫並移除所有非英數字元，再與反向字串比較
    cleaned = re.sub(r"[^a-z0-9]", "", s.lower())
    return cleaned == cleaned[::-1]


def word_count(text):
    """統計單字出現次數：以非英數字元切分、轉小寫後計數。空字串回傳空 dict。"""
    # 連續的英數字元視為一個單字，其餘字元都當作分隔符號
    words = re.findall(r"[a-z0-9]+", text.lower())
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def fizzbuzz(n):
    """回傳 1..n 的 FizzBuzz 字串 list：3 的倍數為 "Fizz"、5 的倍數為 "Buzz"、兩者皆是為 "FizzBuzz"。n<=0 回傳空 list。"""
    result = []
    for i in range(1, n + 1):
        # 同時是 3 與 5 的倍數時優先判斷，避免只輸出 Fizz 或 Buzz
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result
