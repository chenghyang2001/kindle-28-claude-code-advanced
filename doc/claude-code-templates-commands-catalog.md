# claude-code-templates 指令目錄探勘摘要（5 個相關分類）

> 來源：`davila7/claude-code-templates`（29.8k⭐）`cli-tool/components/commands/`
> 探勘日期：2026-07-23。全 repo 共 25 個分類，本摘要只展開與現有工作流相關的 5 個。

## 各分類指令清單

### documentation（10 個）

| 指令 | 大小 | 方向 |
| --- | --- | --- |
| troubleshooting-guide | 9.6K | 疑難排解文件生成（已撈回改造成本專案 `/pitfall-guide`） |
| migration-guide | 8.1K | 遷移指南生成 |
| doc-api | 7.6K | API 文件 |
| interactive-documentation | 5.4K | 互動式文件 |
| docs-maintenance | 4.9K | 文件維護（過時偵測） |
| generate-api-documentation | 4.4K | API 文件（另一版本） |
| update-docs | 4.4K | 文件更新 |
| create-architecture-documentation | 4.4K | 架構文件 |
| create-onboarding-guide | 4.1K | 新人上手指南 |
| load-llms-txt | 1.3K | 載入 llms.txt |

### git-workflow（14 個）

| 指令 | 大小 | 方向 |
| --- | --- | --- |
| gemini-review | 10.8K | 用 Gemini 做 code review（跨 AI 交叉審查） |
| commit | 7.9K | 智慧 commit |
| git-bisect-helper | 7.7K | 二分搜尋找壞 commit |
| branch-cleanup | 6.0K | 分支清理 |
| create-worktrees | 5.2K | 建 worktree |
| create-pull-request | 4.2K | 建 PR（完整版） |
| worktree-cleanup | 4.0K | worktree 清理 |
| worktree-deliver | 4.0K | worktree 完工交付 |
| pr-review | 3.8K | PR 審查 |
| worktree-init | 3.1K | worktree 初始化 |
| worktree-check | 2.1K | worktree 狀態檢查 |
| create-pr | 0.8K | 建 PR（精簡版） |
| fix-github-issue | 0.5K | 修 GitHub issue |
| update-branch-name | 0.4K | 改分支名 |

### orchestration（15 個）— 一整套任務管理系統，指令互相依賴，不適合單撈

archive (11.0K) / optimize (9.4K) / log (7.1K) / resume (6.9K) / feature-dev (6.8K) /
remove (6.5K) / report (6.4K) / sync (6.3K) / commit (6.2K) / find (5.1K) /
move (4.8K) / status (4.8K) / start (4.4K) / feature-pipeline (3.2K) / feature-analyzer (0.8K)

### testing（14 個）

| 指令 | 大小 | 方向 |
| --- | --- | --- |
| webapp-testing | 3.3K | Web 應用測試 |
| generate-tests | 2.7K | 測試生成 |
| add-mutation-testing | 2.6K | 變異測試（驗證測試本身的品質） |
| setup-visual-testing | 2.5K | 視覺回歸測試 |
| test-automation-orchestrator | 2.4K | 測試自動化編排 |
| test-coverage | 2.4K | 覆蓋率分析 |
| add-property-based-testing | 2.4K | 屬性測試（Hypothesis 類） |
| setup-load-testing | 2.4K | 負載測試 |
| setup-comprehensive-testing | 2.4K | 完整測試環境 |
| test-quality-analyzer | 2.4K | 測試品質分析 |
| generate-test-cases | 2.3K | 測試案例生成 |
| testing_plan_integration | 2.3K | 測試計畫整合 |
| test-changelog-automation | 2.3K | changelog 自動化 |
| write-tests | 2.2K | 寫測試 |

### automation（5 個）

| 指令 | 大小 | 方向 |
| --- | --- | --- |
| workflow-orchestrator | 13.5K | 工作流編排 |
| ci-pipeline | 8.8K | CI 管線生成 |
| szamlazz | 3.9K | 匈牙利發票系統整合（公司貢獻的冷門範例） |
| husky | 3.8K | husky pre-commit hook 設定 |
| act | 1.4K | 本地跑 GitHub Actions（act 工具） |

## 挑選結論（對照本機現有工具）

### 值得撈的 3 個

1. **git-workflow/git-bisect-helper（7.7K）**：工具箱沒有 bisect 類工具，抓 regression 實用，與 debug-expert agent 互補。
2. **testing/add-mutation-testing（2.6K）**：code-qa 流程驗「測試有沒有過」，變異測試驗「測試本身有沒有用」，是現有 QA 體系缺的一塊。
3. **git-workflow/gemini-review（10.8K）**：跨 AI 交叉審查思路，已有 codex-rescue 做第二意見，可撈骨架改成呼叫 codex。

### 看似有用但已有更好的（跳過）

- worktree 五件套 → 已有 `/code-session`、`/wt-feature`、worktree-builder
- commit / create-pr → 已有 commit-commands 外掛
- pr-review → 已有 pr-review-toolkit 整組
- ci-pipeline → 已有 cicd-pipeline-architect agent

### 直接跳過

- orchestration 整組（與 GSD 完全重疊，且 15 指令綁定無法單撈）
- szamlazz（匈牙利發票）

## 心得

25 個分類 58 個指令（5 分類合計）翻完，真正值得撈的只有 3 個——再次驗證「食譜庫挑著撈」原則：命中率約 5%，但撈到的都是現有體系的真空地帶。
