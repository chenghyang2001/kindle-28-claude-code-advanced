# ORCA-7

# E202 次數比較

比較來源：`data/big-log-1.txt`、`data/big-log-2.txt`（兩檔各 1800 行）

| 檔案 | E202 次數 |
| --- | ---: |
| big-log-1.txt | 41 |
| big-log-2.txt | 52 |

結論：`big-log-2.txt` 的 E202 較多，多出 11 筆（52 - 41）。

計數方式：以 Grep 搜尋 `ERROR code=E202` 的完整比對，未逐行人工閱讀。
