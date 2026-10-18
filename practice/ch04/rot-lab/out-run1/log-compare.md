# ORCA-7

# E202 次數比較

比較對象：`data/big-log-1.txt`、`data/big-log-2.txt`（各 1800 行）

| 檔案 | E202 次數 | 該檔 ERROR 總數 |
| --- | ---: | ---: |
| big-log-1.txt | 41 | 196 |
| big-log-2.txt | 52 | 202 |

結論：`big-log-2.txt` 的 E202 較多，共 52 筆；`big-log-1.txt` 共 41 筆，相差 11 筆。

計數方式：以 grep 搜尋 `ERROR code=E202` 對整個檔案計數。
