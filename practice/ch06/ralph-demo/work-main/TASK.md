# TASK：文字小工具（src/textkit.py）

- [x] slugify(text)：轉小寫，非英數字元換成 `-`，連續 `-` 合併、去頭尾 `-`。例：`"Hello, World!"` → `"hello-world"`
- [x] is_palindrome(s)：忽略大小寫與非英數字元判斷回文。例：`"A man, a plan, a canal: Panama"` → True；空字串 → True
- [x] word_count(text)：回傳 dict，key 為小寫單字（以非英數字元切分），value 為次數。空字串 → `{}`
- [x] fizzbuzz(n)：回傳 1..n 的字串 list，3 的倍數為 "Fizz"、5 的倍數為 "Buzz"、兩者皆是為 "FizzBuzz"；n<=0 回傳 `[]`
