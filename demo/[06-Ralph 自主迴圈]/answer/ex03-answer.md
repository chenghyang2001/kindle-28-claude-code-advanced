# 練習 03 解答 — 自主迴圈規格（TASK.md 驅動的 Ralph）

> 真實交付物：可跑的腳本 `skills/ralph_loop.sh`（已過 writer→qa→reviewer）。
> 為安全只寫不實跑（不讓無監督迴圈真的呼叫 claude），用 `--dry-run` 驗證流程。

## 一、迴圈目標
讀 `TASK.md` 清單，每輪用 `claude -p` 完成下一個未完成項並打勾，直到全部完成。

## 二、可量測收斂條件（程式可判定，非主觀）
- **收斂**：`grep -c -- '- [ ]' TASK.md == 0`（無未完成框）→ exit 0。

## 三、backstop（多重硬上限）
- **迭代上限** `--max`（預設 10）：跑滿即停 exit 4。
- **時間窗** `--max-seconds`（預設 1800，安全非零；傳 0 才關閉）：總時長超過即停。
- **單通逾時** `--per-call-timeout`（預設 300）：`timeout` 包住每通 claude，卡死那輪當失敗，不阻塞整支。

## 四、每輪檢查點（可回滾）
- git repo 內：`git add TASK.md && git commit -m "ralph: round i"`（commit 失敗只 warn）。
- 非 repo：append 一行到 `ralph_loop.log`。

## 五、護欄（各擋一種失控）
| 護欄 | 機制 | 擋掉什麼 |
|------|------|---------|
| 收斂偵測 | 無 `- [ ]` | 正常結束 |
| backstop 迭代 | `i > MAX` | 無限迴圈 |
| **零進展** | **未打勾框數未減少** `remaining >= prev_remaining` → exit 3 | 空轉燒錢（含 claude 亂動檔案/自增子任務） |
| 時間窗 + 單通逾時 | `SECONDS > MAX_SECONDS`；`timeout` 包 claude | 跑到天亮、單通卡死阻塞 |
| 檔案存在 | TASK 檔不存在 → exit 2 | 誤指空目標 |

退出碼：0 收斂 / 1 參數或環境 / 2 找不到檔 / 3 零進展 / 4 上限或逾時。

## 六、骨架（節選）
```bash
prev_remaining=$(count_remaining)        # 迴圈外先量基準（抓第 1 輪空轉）
for ((i=1; i<=MAX_ITER; i++)); do
  (( SECONDS > MAX_SECONDS )) && stop 4   # 時間窗
  next=$(find_next) || break              # 收斂：無未完成項
  run_claude "$next"                      # timeout 包住，逾時當該輪失敗
  checkpoint "$i"                         # git commit / log
  remaining=$(count_remaining)
  (( remaining >= prev_remaining )) && stop 3   # 零進展
  prev_remaining=$remaining
done
```

## 七、這題最大的學習（reviewer 抓到的活教材）
第一版零進展護欄比對**整檔雜湊** → claude 沒打勾卻亂動 TASK.md（重排版/自增子任務）就讓 bytes 變動、雜湊變、護欄永不觸發 → 對「壞掉但會亂動檔案的 claude」**形同虛設**。
改用**「未完成框數單調遞減」**當客觀進度信號後才真正擋得住。
→ 教訓：**護欄要擋的是「真跑時的失控」，不是 happy path**；進度信號不能拿「claude 自報的檔案狀態」當唯一真相。

## 驗收
- [x] 可量測收斂條件（未完成框數=0，程式可判定）
- [x] 最大迭代上限 backstop（+時間窗+單通逾時）
- [x] 每輪檢查點可回滾（git commit / log）
