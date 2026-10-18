## Git 工作流
- commit message 使用繁體中文，格式「動詞 + 簡短說明」，動詞限：新增／修復／重構／更新／移除。
- 本專案 commit 前綴固定為 `[notestat]`，例：`[notestat] 新增 --json 輸出`。
- 功能分支命名 `feat/<簡短英文>`，修 bug 用 `fix/<簡短英文>`。
- 不 force push、不 `--no-verify`、不 amend 已推送的 commit。
- 發版時 tag 格式 `ns-v<主>.<次>.<修>`，例如 `ns-v0.1.0`。
- 本練習 repo 不建 GitHub repo、不 push。

