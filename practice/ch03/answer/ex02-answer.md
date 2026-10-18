# 練習 02 解答 — 用 .claude/ 做 pre-setup

## 任務 1：最值得寫進 `.claude/` 或 CLAUDE.md 的 3 項脈絡

以練習 01 的 `cfgcli` 為真實專案：

| # | 類別 | 內容 | 放哪裡 | 為什麼值得寫 |
| --- | --- | --- | --- | --- |
| 1 | 慣用指令 | `PYTHONUTF8=1 python -m pytest -q`；手動跑要設 `CFGCLI_HOME=<暫存>` | CLAUDE.md＋`.claude/commands/test.md`（`/test`）＋`settings.local.json` 預先允許 | Windows cp950 環境沒加 `PYTHONUTF8=1` 會遇到編碼錯誤；沒設 `CFGCLI_HOME` 會寫到使用者的真實設定檔 |
| 2 | 目錄與分層 | `store.py` 只放設定檔讀寫、`cli.py` 一個子指令一個 `cmd_xxx`、新測試開新檔；回傳碼 0/1/2 的意義 | CLAUDE.md | 程式碼看得出「怎麼寫」，看不出「為什麼這樣分」。少了這段，Claude 容易把功能放錯層、或混用回傳碼 |
| 3 | 雷區 | 不改既有子指令的輸出格式；Git Bash 的 `/tmp` 路徑要先 `cygpath -w`；不要用 heredoc 產生 Python 原始碼 | CLAUDE.md | 全都是練習 01 實際踩過的坑（計畫 v1 想改 `list`、`-o /tmp/...` 寫錯地方、`"\n"` 被轉義） |

### 實際建立的 pre-setup

```text
k28-ch03-practice/
├── CLAUDE.md                     # 原有「本專案例外」＋新增「專案簡報：cfgcli」（目錄/慣用指令/慣例/雷區）
└── .claude/
    ├── settings.local.json       # 專案層設定（依本專案 CLAUDE.md 規定不用 settings.json；已 gitignore）
    └── commands/
        └── test.md               # /test：跑 pytest 並用繁中摘要
```

`.claude/settings.local.json`：

```json
{
  "permissions": {
    "allow": [
      "Bash(PYTHONUTF8=1 python -m pytest:*)",
      "Bash(python -m pytest:*)",
      "Bash(python -m cfgcli.cli:*)"
    ],
    "deny": ["Edit(tests/test_cli.py)"]
  },
  "env": { "PYTHONUTF8": "1" }
}
```

`/test` 驗證（`claude -p "/test"`，已清掉 `CLAUDE*` 環境變數）：

```text
8 個測試全部通過，0 個失敗，執行時間 0.10 秒。沒有修改任何檔案。
```

## 任務 2：有／沒有 pre-setup 的計畫比較

**同一個任務**（兩邊完全相同）：

```text
為這個 CLI 加一個 `import` 子指令，從一個 JSON 檔讀入設定並合併到目前設定。
先給我實作計畫（要改哪些檔、新增哪些函式、測試怎麼寫），等我說 ok 再寫。只輸出計畫，不要修改任何檔案。
```

| 對照組 | 執行位置 | 指令 |
| --- | --- | --- |
| 有 pre-setup | 專案根目錄（有 CLAUDE.md 專案簡報＋`.claude/`） | `claude -p --permission-mode plan --max-turns 20 "<任務>"` |
| 沒有 pre-setup | scratchpad 的 `clean-nopresetup/`（`git archive` 出的 `cfgcli/`＋`tests/`，沒有 CLAUDE.md、沒有 `.claude/`） | 同上 |

兩次都先 `env -u CLAUDE...` 清掉 13 個 `CLAUDE` 開頭的環境變數；兩邊都會載入全域 `~/.claude/CLAUDE.md`，這部分條件相同。原始輸出放在 `answer/ex02-plans/`。

### 比較結果

| 面向 | 沒有 pre-setup | 有 pre-setup |
| --- | --- | --- |
| 讀現有程式碼 | ✅ 讀了 cli/store/兩個測試檔，自己推出慣例 | ✅ 同樣讀了，**而且每個決策都對照 CLAUDE.md 說明理由** |
| 函式放哪一層 | 全放 `cli.py`（沒說原因） | 全放 `cli.py`，並說明「依 CLAUDE.md，store 只管設定檔本身」 |
| **回傳碼語意** | 匯入檔是壞的 JSON → **回 2**（和「目前設定檔損壞」混在一起） | 匯入檔是壞的 JSON → **回 1**（使用者錯誤）；只有目前設定檔損壞才回 2。還**主動點出陷阱**：`JSONDecodeError` 是 `ValueError` 的子類別，不在 `cmd_import` 裡攔下就會被 `main()` 誤判成 2 |
| 不動既有輸出 | 沒提 | 明確寫「不動 set/get/list/export 任何輸出格式」（對應雷區） |
| 測試數 | 約 9 個 | 11 個；多了「沒有設定檔時匯入」、「設定檔損壞 → 2」、「中文檔無 `\u`」 |
| 冒煙測試路徑 | `python -m cfgcli.cli import sample.json`（沒處理 Windows 路徑） | 用 `cygpath -w` 轉暫存路徑（對應雷區） |
| 文件同步 | 沒提 | 計畫第 3 步：更新 CLAUDE.md 的子指令清單 |
| 會不會停下來問 | 結尾說核准後**還要先問「快速 demo 還是完整三 agent 模式」**（沒有專案 CLAUDE.md 的豁免，全域鐵律生效） | 不問，直接進實作（專案 CLAUDE.md 已宣告快速模式） |
| 兩邊都做到 | `utf-8-sig` 讀 BOM、先驗證再寫入（原子性）、`export → import` 來回測試 |

**結論**：沒有 pre-setup 的計畫其實已經不錯（這個專案很小，Claude 從程式碼就能推出大部分慣例）。差距在**看程式碼推不出來的東西**：

1. **回傳碼的語意**（1 和 2 的差別）——程式碼裡只看得到數字，看不到「1 = 使用者錯誤、2 = 設定檔損壞」這條規則。這是唯一一個會造成**行為差異**的地方。
2. **雷區**（不改輸出格式、Windows 路徑）——全是踩過才知道的經驗。
3. **流程設定**（快速模式豁免）——少了這條，一個本來可以一次到位的計畫會多一輪來回。

也就是說：pre-setup 最值得寫的，是**理由與禁忌**，而不是程式碼本身就看得出來的結構。

### 對照實驗的干擾因素（誠實記錄）

- 乾淨資料夾在 scratchpad 底下，路徑含 `k28-ch03-practice` 字樣，所以沒有 pre-setup 的那一次也從路徑猜出「這是練習」。
- 有 pre-setup 那次的**最終訊息**被全域 Stop hook（「有未 commit 變更」提醒）蓋掉，計畫本體存在它的計畫檔裡（已複製成 `plan-with-presetup.md`）。教訓：**pre-setup 要先 commit 再跑對照**，否則 hook 會搶走輸出。
- 樣本數只有各 1 次，LLM 輸出有隨機性；結論是方向性的，不是統計結果。

## 延伸思考：計畫模式什麼時候是浪費、什麼時候必要？

| 浪費（殺雞用牛刀） | 必要 |
| --- | --- |
| 改 typo、改一個常數、加一行 log | 有「順便」誘惑的任務（練習 01 的 v1 就想順便改 `list`）——計畫階段刪掉越界步驟最便宜 |
| 需求已經精確到函式簽名，沒有設計空間 | 有多種合理做法、而且會影響外部行為的（回傳碼、輸出格式、合併策略） |
| 一次性腳本、丟掉也不心疼的 demo | 跨 3 個以上檔案，或會碰到既有測試、公開介面 |
| 純查詢／研究（直接問就好） | 不熟的 codebase，或錯了很難回復（資料遷移、刪檔、部署） |

判斷方式：**「寫錯了重來的成本」比「讀一份計畫的成本」高嗎？**高就開計畫模式。另外，pre-setup 做得越完整，計畫模式的價值越高——計畫會直接引用專案規則，審查時更容易看出哪裡偏離。
