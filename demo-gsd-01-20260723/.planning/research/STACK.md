# Stack Research

**Domain:** 純 Python 標準庫 CLI（新增任務完成狀態欄位）
**Researched:** 2026-07-23
**Confidence:** HIGH

## 結論先講：不需要任何新依賴

這次要加的是「完成任務」功能——本質上是**在既有資料上多一個布林欄位**，不是新增子系統。stdlib 已經提供三種可以直接拿來用的資料結構寫法（`dataclasses`、`typing.NamedTuple`、`dict`），全部免安裝、Python 3.14 內建。`requirements.txt` 維持只有 `pytest` 一行即可，**不需要加 `attrs`、`pydantic`、`msgspec` 或任何第三方資料類別庫**——那些是給「需要驗證/序列化/大量欄位」的場景，這裡是 12 個測試、單檔案、in-memory 的練習專案，用第三方庫是殺雞用牛刀，也違反本專案「維持極簡」的既定 constraint。

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python `dataclasses`（stdlib） | 隨 Python 3.14 內建，無版本可選 | 定義 `Task` 資料結構（name + done 狀態） | 自動產生 `__init__`/`__eq__`/`__repr__`，讓 `Task("買牛奶")` 這種建構式和 `assert task == Task("買牛奶", done=True)` 這種斷言都「開箱即用」，不用手寫比較邏輯；預設可變（不像 NamedTuple），可以直接 `task.done = True` 原地修改，貼合本專案既有的「functional core, imperative shell」設計（`complete_task(tasks, name)` 回傳新 list，但 list 內的物件用屬性賦值更新） |
| `pytest` | 目前最新穩定版 9.1.1（2026-06-19 發布，PyPI） | 既有測試框架，延續使用 | 專案已用；`capsys` fixture（HIGH confidence，官方文件確認）可直接驗證 CLI 印出 `✓` 的行為，不需額外測試工具 |

### Supporting Libraries

本次功能**沒有**需要新增的 supporting library。以下列出「considered but not needed」以避免之後誤加：

| Library | 是否需要 | 原因 |
| --------- | --------- | ------ |
| `attrs` / `pydantic` | 不需要 | 只需 2 個欄位（name, done），無需驗證/序列化/巢狀結構，`dataclasses` 已足夠且零安裝成本 |
| `enum`（stdlib） | 不需要，但可留意 | 若未來狀態從「done: bool」擴增為「pending/done/archived」三態以上，才值得換 `enum.Enum`；目前二元狀態用 `bool` 最直覺，過度設計反而增加測試複雜度 |
| `colorama` | 不需要 | `✓` 用純文字 Unicode 字元即可達成「一眼看到打勾」的需求，不需要終端機顏色渲染；且 colorama 會增加 Windows 終端機相容性的額外變因 |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `pytest` + `capsys` fixture | 驗證 `list` 指令印出的文字（含 `✓` 標記） | `capsys.readouterr()` 回傳 text 字串（非 bytes），比對時直接用 `in` 或 `==` 檢查輸出字串是否含 `✓`，不用擔心終端機編碼——`capsys` 捕捉的是 Python 內部字串物件，發生在「印到真實終端機」之前，因此**測試本身不受 Windows cp950 影響**（HIGH confidence，官方文件驗證） |
| `PYTHONUTF8=1`（環境變數，非套件） | 讓 `python app.py` 手動執行時，`print("✓")` 不會在 Windows cp950 終端機噴 `UnicodeEncodeError` | 本專案 `GSD-PRACTICE.md` 已建立此慣例（`PYTHONUTF8=1 pytest test_app.py -v`），新功能延續即可，不用另立規則 |

## Installation

```bash
# 無新增依賴，requirements.txt 維持原樣
# pytest 已在既有 requirements.txt，若要對齊最新版可選擇性執行：
python -m pip install --upgrade pytest

# 執行既有 + 新增測試（Windows 務必加 PYTHONUTF8=1）
PYTHONUTF8=1 pytest test_app.py -v
```

不需要 `pip install` 任何新套件；本節只是重申既有安裝方式。

## Data-Structure Options（純 Python，供 roadmap/plan-phase 決策參考）

這是本次功能真正的技術決策點（PROJECT.md 已標記為 Pending）。四個候選方案比較：

| 方案 | 可變性 | 與既有 12 個測試的相容成本 | 建議 |
| ------ | -------- | -------------------------- | ------ |
| **`dataclass`**（推薦） | 可變（field 可直接賦值） | 中——舊測試 `assert tasks == ["買牛奶"]` 要改成 `assert tasks == [Task("買牛奶")]`（需定義 `Task.__eq__`，dataclass 自動生成），改法一致、可批次處理 | ✅ 首選：型別清楚（`task.name`、`task.done`），IDE 補全友善，`__repr__` 讓測試失敗訊息可讀（`Task(name='買牛奶', done=True)` 比 `{'name': '買牛奶', 'done': True}` 好讀） |
| `dict`（如 `{"name": ..., "done": False}`） | 可變 | 中——同上，但斷言要改成 `{"name": "買牛奶", "done": False}` | 可行備案：零 import，但欄位名是字串鍵，容易打錯字（`tsk["dnoe"]` 這種 typo 不會被任何工具抓到），且 `list` 顯示邏輯要多寫 `task["name"]` 而非 `task.name`，可讀性略遜於 dataclass |
| `typing.NamedTuple` | **不可變**（immutable tuple） | 高——完成任務要用 `tasks[i] = tasks[i]._replace(done=True)` 整個換新 tuple，語意比「原地標記完成」繞；且與「in-memory 可變 list」的既有心智模型（`delete` 直接從 list 移除）不一致 | 不推薦：不可變性在這裡沒有帶來實質好處（不需要 hashable、不需要當 dict key），反而讓「標記完成」這個核心動作變得不直覺 |
| 平行雙 list（`tasks: list[str]` + `done_flags: list[bool]`，靠 index 對應） | 可變 | 低（表面上不用碰舊測試的元素型別） | ❌ 反面教材：兩個 list 靠 index 同步，一旦 `delete_task` 造成 index 位移，`done_flags` 立刻對不上——這是最容易產生「刪除後標記串掉」這類隱藏 bug 的寫法，即使 PROJECT.md 沒有明講也應主動排除 |

**建議寫法（HIGH confidence，純 stdlib 語法驗證）：**

```python
from dataclasses import dataclass

@dataclass
class Task:
    """一筆待辦任務：名稱 + 完成狀態。"""
    name: str
    done: bool = False
```

- 不需要 `frozen=True`（需要原地改 `done`）
- 不需要 `slots=True`（Python 3.14 對 `slots=True` + 默認值/繼承有已知 regression，見 CPython issue #135228、#142214；專案規模小、無效能瓶頸，加 `slots` 純屬過度優化且目前版本有雷，明確建議**不要加**）
- 保留預設 `__eq__`（dataclass 自動產生逐欄位比較），讓測試可以直接寫 `assert tasks == [Task("買牛奶", done=True)]`

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
| ------------- | ------------- | -------------------------- |
| `dataclasses.dataclass`（可變、無 slots） | `dict` | 若團隊/課程刻意要示範「不用匯入任何東西、連 `dataclasses` 都不 import」的最小教學版本，`dict` 是唯一比 dataclass 更「零依賴」的選項；但要接受欄位名是字串、無 IDE 型別檢查的代價 |
| `dataclass(done=False 預設)` | `dataclass(frozen=True)` + `_replace`-style 手寫 replace 函式 | 若之後這個專案要往「不可變資料流」方向走（例如引入 undo/redo，需要保留歷史快照），frozen dataclass 配合 `dataclasses.replace()` 會更適合——但本次 PROJECT.md 明確排除 undo，所以現在不需要 |

## What NOT to Use

| Avoid | Why | Use Instead |
| ------- | ----- | -------------- |
| 平行雙 list（`tasks` + `done_flags` 靠 index 對應） | `delete_task` 造成 index 位移時，兩個 list 會不同步，產生「刪除某任務後，另一個任務被誤標記完成」的隱藏 bug；且測試要同時斷言兩個 list，維護成本更高 | 用單一 `Task` 物件（dataclass 或 dict）把 name 和 done 綁在一起，資料一致性靠物件本身保證，不靠人工同步兩個 list |
| `attrs` / `pydantic` 等第三方資料類別庫 | 專案 constraint 明講「無框架、無第三方依賴，維持極簡」；這兩者主要價值在欄位驗證/序列化，這裡完全用不到，只會多一條 `requirements.txt` 依賴且拖慢學習焦點 | stdlib `dataclasses`，兩個欄位的場景已經完全夠用 |
| `dataclass(slots=True)`（在 Python 3.14 上） | CPython 3.14 有已知 regression：slotted dataclass 在某些繼承/`init=False` 組合下行為異常（cpython#135228、#142214），且本專案規模完全不需要 `__slots__` 帶來的記憶體優化 | 用預設（無 `slots` 參數）的 `@dataclass` |
| 用 `colorama` 或 ANSI escape code 讓完成任務變綠色 | 需求只要求「打勾標記」（✓），沒有要求顏色；加終端機顏色套件會多一層 Windows 終端機相容性風險（cp950 環境下 ANSI code 支援不一） | 純文字 Unicode 字元 `✓`（U+2713），搭配既有 `PYTHONUTF8=1` 慣例即可達成視覺區隔 |

## Windows Unicode（✓ 輸出）注意事項

**這是本次唯一真正需要留意的「非資料結構」技術細節**（HIGH confidence，延續本專案既有已驗證慣例）：

1. **問題根源**：Windows 終端機預設用 cp950（繁體中文編碼），`print("✓")` 若在未設定 UTF-8 模式的終端機執行，會拋出 `UnicodeEncodeError: 'cp950' codec can't encode character '✓'`。
2. **既有解法（延續使用，不用重新設計）**：本專案 `GSD-PRACTICE.md` 已建立 `PYTHONUTF8=1` 慣例（`PYTHONUTF8=1 pytest test_app.py -v`）。新功能執行時比照辦理：`PYTHONUTF8=1 python app.py`。
3. **測試不受影響**：`pytest` 的 `capsys` fixture 攔截的是 Python 內部的字串輸出（發生在寫到真實終端機之前），因此**測試斷言 `✓` 字元不需要額外處理 encoding**，即使不加 `PYTHONUTF8=1` 執行 `pytest` 本身也不會因為終端機編碼而失敗（官方文件確認 `capsys` 回傳純文字字串）。只有「真的手動跑 `python app.py` 並在互動式終端機看到 print 結果」才會踩到 cp950 問題。
4. **建議加一道防線（可選，不是必須）**：若想讓使用者忘記設定 `PYTHONUTF8=1` 時也不會直接當機，可以在 `app.py` 開頭加：

   ```python
   import sys
   if sys.platform == "win32":
       sys.stdout.reconfigure(encoding="utf-8", errors="replace")
   ```

   這樣即使沒設環境變數，`✓` 印不出來時最多顯示替代字元而不是整個程式崩潰。是否加入屬於 plan-phase 的取捨（多一行防禦碼 vs. 維持「靠慣例、不加額外程式碼」的極簡風格），本研究只指出這個選項存在。

## pytest 測試撰寫建議（延續既有測試風格）

既有 12 個測試已用 `assert tasks == [...]` 這種「直接比較整個 list」的風格，新增 `complete_task` 測試建議延續同樣模式，並額外用到：

- **一般案例**：`complete_task(tasks, "買牛奶")` 後，斷言該任務的 `done` 為 `True`（若採 dataclass：`assert tasks[0].done is True`；若採 dict：`assert tasks[0]["done"] is True`）
- **邊界案例（找不到）**：`complete_task(tasks, "不存在的任務")` 應回報「找不到任務」且不拋例外、不改動 `tasks`
- **邊界案例（重複完成）**：對已經 `done=True` 的任務再次呼叫 `complete_task`，應回報「已經完成過」，且 `done` 狀態不變（不切回 `False`，因為 v1 明確不做 undo）
- **CLI 輸出驗證**：用 `capsys` 驗證 `list` 指令印出的字串包含 `✓`（已完成任務）且未完成任務不含 `✓`，範例：

  ```python
  def test_list_shows_checkmark_for_done_task(capsys):
      tasks = [Task("買牛奶", done=True), Task("洗衣服", done=False)]
      list_tasks(tasks)  # 假設既有 CLI 顯示函式
      captured = capsys.readouterr()
      assert "✓" in captured.out
      assert "買牛奶" in captured.out
  ```

  （HIGH confidence，`capsys.readouterr()` API 為官方文件確認的標準用法）

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Python 3.14（本機環境） | `dataclasses`（stdlib，無獨立版本） | 內建於 3.14，無需考慮版本相容性；唯一要避開的是 `slots=True` 參數（見上方 CPython regression 說明），其餘 dataclass 語法（field 預設值、`__eq__`/`__repr__` 自動生成）行為穩定 |
| pytest 9.1.1（PyPI 最新，2026-06-19） | Python 3.14 | pytest 9.x 系列支援 Python 3.9+，與本機 3.14 環境相容；既有 `.pytest_cache/` 顯示上次實際執行版本為 8.4.2，升級到 9.1.1 不影響 `capsys`/斷言語法，屬非破壞性升級（MEDIUM confidence——未逐條核對 pytest 8→9 changelog 的所有 breaking change，但 `capsys` 為長期穩定 API，不在近期 changelog 的破壞性變更清單中） |

## Sources

- [pytest 官方文件 — capsys fixture 用法](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html) — 已用 WebFetch 驗證 `readouterr()` API 與文字/位元組行為（HIGH confidence）
- WebSearch: "pytest latest version 2026 pypi" — 確認 pytest 最新穩定版為 9.1.1（2026-06-19 發布），來源 PyPI release tracking（MEDIUM confidence，未逐一核對官方 changelog 全文）
- WebSearch: "Python 3.14 release dataclasses slots frozen default" — 確認 `dataclasses` 模組於 Python 3.14 的預設行為（`slots=False`、`frozen=False`、`kw_only=False`），並發現 `slots=True` 在 3.14 的已知 regression（[cpython#135228](https://github.com/python/cpython/issues/135228)、[cpython#142214](https://github.com/python/cpython/issues/142214)）（MEDIUM confidence，GitHub issue 為社群回報，非官方 release note，但與官方文件描述的預設行為一致）
- 專案既有檔案：`.planning/PROJECT.md`、`.planning/codebase/STACK.md` — 既有 stack 現況與本次新增需求的邊界（HIGH confidence，直接讀取專案檔案）

---
*Stack research for: Python stdlib todo CLI — complete-task feature*
*Researched: 2026-07-23*
