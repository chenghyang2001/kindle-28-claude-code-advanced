# NOTES — K28 第 1 章練習（快速 demo 模式）

## 做了什麼

| 練習 | 動作 | 產物 |
| --- | --- | --- |
| 共用 | 建範例資料 `fixtures/notes/`（含陷阱）、`fixtures/data/sales.csv`（含缺值） | `fixtures/` |
| 共用 | 寫 `scripts/run-prompt.sh`：複製資料到 `runs/<run>/` 沙盒、清掉 `CLAUDE*` 環境變數、跑 `claude -p --output-format json` | `scripts/run-prompt.sh` |
| 01 | 實跑模糊版、結構化版各一次，模糊版再用 `--resume` 補一個返工回合 | `runs/ex01-*`、`prompts/ex01-*.txt` |
| 01 | 寫 `scripts/check_merged.py` 依規格獨立驗證 merged.txt（含 `--selftest`） | `scripts/check_merged.py` |
| 02 | 列出脈絡清單、寫強化版 one-shot prompt，連同書上骨架各跑一次 | `runs/ex02-*`、`prompts/ex02-*.txt` |
| 02 | 寫 `scripts/check_summary.py` 用獨立計算核對平均值與表格格式 | `scripts/check_summary.py` |
| 共用 | 抽出 5 次執行的指標 | `runs/METRICS.md` |
| 解答 | | `answer/ex01-answer.md`、`answer/ex02-answer.md` |

## 驗證結果

- 5 次 `claude -p` 全部 `is_error=False`，沒有任何一次中途反問。
- 練習一：`check_merged.py` 兩份產物都通過 UTF-8／無 BOM／檔數／排除子目錄／內容完整；排序上模糊版是自然排序、結構化版是字串排序（prompt 的「依檔名排序」有歧義）。模糊版輸出位置不符預期，返工 1 次。
- 練習一量化：模糊版 2 回合、87.2 秒、US$1.65；結構化版 1 回合、34.1 秒、US$0.76。
- 練習二：`check_summary.py` 兩份 summary.md 都 OVERALL PASS（2341.43 / 2.14 / 2574.29，與手算一致）；Claude 產生的兩支程式都已重跑，輸出一致。
- 輔助腳本：`check_merged.py --selftest` OK；`check_summary.py` 找不到檔時正確回傳 exit 1。

## 與題目要求的差異

1. **「問了你幾個回合」量不到真正的反問**：題目假設互動模式；這裡用 `claude -p`（非互動），加上本專案 CLAUDE.md 規定「不要停下來問」，所以 Claude 一律自己猜。改用「使用者需要下幾次指令」＋「Claude 自行做了幾個假設」當替代指標。
2. **「真實 CSV」改用自建模擬資料**：沒有可公開的真實資料，自建 `sales.csv` 並刻意放入缺值與中文欄位。
3. **範例資料有洩漏**：`archive/old.txt` 內容寫著「不應被合併」，等於提示了模糊版，讓模糊版結果偏好。解答中已註明，未重跑（每次約 US$0.8）。
4. **每種 prompt 只跑一次**：樣本數 1，LLM 輸出有隨機性，數字只能看趨勢。
5. **成本數字是 API 計價估算**：`total_cost_usd` 由 CLI 回報；本機走訂閱，實際不一定扣這筆錢。約 US$0.75 是每次固定的載入成本（系統提示＋全域設定），所以兩版差距主要來自回合數。
6. **練習二多做一個對照組**（書上骨架原文），題目只要求跑自己寫的 one-shot。
7. 沒有用到外部帳號、token、MCP、plugin、worktree、GSD／Ralph；沒有修改 `~/.claude/`，沒有建 GitHub repo、沒有 push。
8. 快速模式：未經 code-qa／code-reviewer 審查。原始 `_result.json`（含 session ID）與沙盒內 `.claude/` 已用 `.gitignore` 排除。

## 重跑方式

```bash
bash scripts/run-prompt.sh ex01-structured prompts/ex01-structured.txt notes
PYTHONUTF8=1 python scripts/check_merged.py runs/ex01-structured/notes runs/ex01-structured/out/merged.txt
bash scripts/run-prompt.sh ex02-oneshot prompts/ex02-oneshot.txt data
PYTHONUTF8=1 python scripts/check_summary.py runs/ex02-oneshot/data/sales.csv runs/ex02-oneshot/out/summary.md
```
