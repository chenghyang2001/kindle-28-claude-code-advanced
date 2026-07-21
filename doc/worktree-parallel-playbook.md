# Git Worktree 平行化實戰手冊

> 依據《平行化：AI 開發的最大生產力倍增器》（Anthropic 風格手冊）+ 本專案 `demo/parallel-worktree/parallel-worktree-demo.sh` 的實跑經驗整理。
> 用途：開新任務時的隨手參照——如何把「玩具 demo」的 worktree 平行化，安全套到「真實 repo」上。

---

## 0. 核心觀念

- **平行化 = 一個共用的 `.git`「大腦」+ 多支物理隔離的 worktree「手臂」**，每支手臂有自己的資料夾與分支，互不踩踏。
- **為什麼不只用 branch**：branch 只是指標，所有分支共用同一個工作目錄，兩個 AI 同時改同一檔會互相覆寫（stomping）。要平行必須用**物理隔離的獨立目錄**。
- **平行化真正的瓶頸不是工具，是「任務能不能切成互不碰的獨立塊」**。切得好 → 零衝突並行 3–4 倍；切不好 → merge 地獄。這是人要動腦的地方。

---

## 1. Demo → 真實專案：8 個必改點（⚠️ 危險）

| 面向 | Demo（拋棄式） | 真實專案 |
| --- | --- | --- |
| Phase 0 | `rm -rf` 建臨時 repo | ⚠️ **絕對不要 `rm -rf`**；直接用現有 repo |
| 分支起點 | 空 init 的本地 HEAD | 先 `git fetch`，從 `origin/main` 長出（起點乾淨） |
| worktree 落點 | 臨時根目錄下 | 兄弟目錄 `../<repo>-<task>`（⚠️ 別放 repo 內，會被 git 追蹤／IDE 誤判） |
| 任務切分 | 各寫全新檔（天生無衝突） | **要真的規劃**：每軌碰不同檔／模組；重疊處先講好介面 |
| 執行模式 | headless `-p --acceptEdits` | 多數用**互動 `claude`**（要 review）；明確可自動驗證的才 headless |
| 驗收 | 冒煙測試 | 真的跑 test suite + lint 綠才算完成 |
| 合併 | 直接 `git merge` | 個人 → 直接 merge；團隊 → `git push` + PR |
| 清理 | `worktree remove` + `branch -d` | 同；但 `branch -d` 前**先 push**（未 merge 進本地會拒刪） |

---

## 2. 合併決策規則

**看 repo 是不是只有你一個人 push：**

- **個人 repo（`chenghyang2001` / `workspace/` 專案）→ 直接 `git merge`**（最快、無 PR 開銷）。
- **團隊 repo／想讓 CI 把關／要留審查痕跡 → `git push` + PR**。
- **鐵則（不分場景）：`wt-analysis` 唯讀軌永遠不 merge**（只查碼、不產出）。

---

## 3. 混合執行模式（推薦）

**N 條實作軌用互動、＋1 條 analysis 軌用 headless 唯讀**（黃金法則②：永遠留一個 `wt-analysis`）。

```
                 origin/main（共同乾淨起點）
                        │
      ┌─────────────────┼─────────────────┬──────────────────┐
   ../repo-featA     ../repo-featB      ../repo-analysis   (主目錄 repo 不動)
  feature/featA     feature/featB       main（唯讀）
  互動 claude       互動 claude         headless claude -p
  你逐步 review     你逐步 review       查碼/查 log → 查完即棄，不改碼
        └──── 測試綠 → git merge 回 main ────┘
```

- **實作軌互動、analysis 軌 headless** 是黃金組合：改碼盯著（安全），查碼雜事丟給拋棄式 headless（不污染主工作區）。
- analysis 軌從 `main` 建、**不建新分支**（`git worktree add ../repo-analysis main`），查完 `worktree remove` 即可。

---

## 4. 劇本 A — 全新 repo（greenfield）

```bash
# ① 建 repo + 空 commit + push → 得到共同起點 origin/main
gh repo create chenghyang2001/<repo> --public --clone && cd <repo>
git commit --allow-empty -m "init" && git push -u origin main

# ② 盤點 3-5 個彼此獨立的初始模組（碰不同資料夾）
#    例：feature/api（api/）、feature/web（web/）、feature/schema（db/）

# ③ 每個模組一條 worktree（兄弟目錄，從 origin/main 長出）
git worktree add -b feature/api  ../<repo>-api  origin/main
git worktree add -b feature/web  ../<repo>-web  origin/main
git worktree add    ../<repo>-analysis main       # analysis 軌，唯讀不建分支

# ④ 混合啟動
#    分頁1: cd ../<repo>-api && claude          # 互動
#    分頁2: cd ../<repo>-web && claude          # 互動
#    需要時: cd ../<repo>-analysis && claude -p "web 和 api 有沒有重複定義的型別？"

# ⑤ 各軌測試綠 → 回主線依序 merge（個人 repo 直接 merge）
cd ~/workspace/<repo>
git merge feature/api
git merge feature/web

# ⑥ 清理（閱後即焚；branch -d 前若沒 merge 進本地要先 push）
git worktree remove ../<repo>-api ; git branch -d feature/api
git worktree remove ../<repo>-web ; git branch -d feature/web
git worktree remove ../<repo>-analysis            # 唯讀軌無分支可刪
```

---

## 5. 劇本 B — 現有 repo 發新功能（brownfield，最常見）

**具體例子**：加「資料匯出」功能，拆成 3 條互不碰的軌：

- `feature/export-api`（只動 `api/export.py`）
- `feature/export-ui`（只動 `web/ExportButton.tsx`）
- `feature/export-fmt`（只動 `lib/formats.py`）

```bash
cd ~/workspace/<你的 repo>
git fetch origin                                      # ① 起點取最新 origin/main

# ② 拆子任務（上面 3 條，各碰不同檔 → 天生無衝突）

# ③ 建 worktree（從 origin/main 長出，兄弟目錄）
git worktree add -b feature/export-api ../<repo>-export-api origin/main
git worktree add -b feature/export-ui  ../<repo>-export-ui  origin/main
git worktree add -b feature/export-fmt ../<repo>-export-fmt origin/main
git worktree add    ../<repo>-analysis main            # analysis 唯讀軌

# ④ 混合啟動：3 個終端機分頁各跑互動 claude；analysis 軌 headless 隨查
#    各軌一句明確任務，例：「實作 export-api，只動 api/export.py，完成後跑該模組 pytest 確認綠」

# ⑤ 每軌測試綠 → merge（個人）或 push+PR（團隊）
cd ~/workspace/<repo>
git merge feature/export-api
git merge feature/export-ui
git merge feature/export-fmt

# ⑥ 清理
for t in export-api export-ui export-fmt; do
  git worktree remove ../<repo>-$t && git branch -d feature/$t
done
git worktree remove ../<repo>-analysis
```

---

## 6. 護欄（黃金法則）

1. **3–5 軌是甜蜜點**：再多人腦顧不過來，反而慢。
2. **每軌碰不同檔**：零衝突的前提。重疊處先抽介面／或先做完一個再做下一個。
3. **永遠留 `wt-analysis` 唯讀軌**：查碼/查 log 用它，別污染正在改的主工作區。
4. **閱後即焚**：合併完立刻 `worktree remove` + `branch -d`，別讓 worktree 永遠殘留。
5. ⚠️ **Git Bash 路徑地雷**（本機實測，見 memory `git-for-windows-worktree-abspath-gotcha`）：
   - `git worktree add <POSIX絕對路徑>` 會誤轉 `/c/…` → `C:/c/…` → 改**相對路徑**（先 `cd` 主 checkout，用 `../wt-x`）。
   - `git -C <POSIX絕對路徑>` 直接 fail → 改 `( cd "$DIR" && git … )`。
   - `MSYS_NO_PATHCONV=1` 救不了（git.exe 內部轉換）。

---

## 7. 現成工具對照（不用重造輪子）

| 你要做的 | 用這個 |
| --- | --- |
| 單一 feature 開一條 worktree（劇本 B 的一軌） | `/code-session <task>`（自動建 `feature/<task>`＋兄弟目錄＋從 origin 長出） |
| 派 subagent 在 worktree 裡實作、只回報座標不 merge | `worktree-builder` subagent |
| 一鍵看整套平行化流程跑一遍（教學） | `/parallel-demo` |
| 非程式任務（文件/研究）常駐 worktree | `/docs-session` |

**多軌並行 = 對每條軌跑一次 `/code-session <task>`**（各開終端機），再人工把測試綠的 merge 回來。

---

## 8. 選型決策樹（該用哪種平行化武器）

| 任務性質 | 用什麼 |
| --- | --- |
| 3-5 個明確、各自獨立的功能開發 | Claude Native `--worktree`／本手冊劇本（手動掌控的經典平行軌） |
| 想測多種解法／實驗性重構 | Subagents + `isolation:"worktree"`（用完即棄的無痕隔離） |
| 跨數十個檔的重複性修改（架構遷移） | `/batch` 指令（系統級大規模並行） |
| 子代理之間要互相溝通、團隊協作 | ⚠️ 別用 worktree 隔離，改用 Agent Teams 架構 |

---

## 參考

- 原始手冊：`~/Downloads/Parallel_AI_Productivity.pdf`（16 頁視覺手冊）
- 可跑 demo：`demo/parallel-worktree/parallel-worktree-demo.sh`（三代理人 + 4 輪 QA 驗過）
- 一鍵觸發：`/parallel-demo [DEMO_ROOT]`
- 相關 memory：`worktree-skill-subagent-binding`、`git-for-windows-worktree-abspath-gotcha`
