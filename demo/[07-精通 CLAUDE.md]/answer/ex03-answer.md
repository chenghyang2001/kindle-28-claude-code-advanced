# 練習 03 解答 — 綜合：把本專案臃腫的 CLAUDE.md 真的模組化

> capstone：把第七課學的 `@import` 模組化**動手套到本專案自己的 CLAUDE.md**。
> 安全做法：不動正在驅動本 session 的真實根檔，把成果產到 `answer/modular-demo/` 當示範。

## 一、現況診斷（原根檔 7 段混在一起）

| # | 段落 | 性質 | 去向 |
|---|------|------|------|
| 1 | 專案說明 | 短門面 | 留主檔 |
| 2 | 架構 | 短門面 | 留主檔 |
| 3 | 攜帶機制 | 短 | 留主檔 |
| 4 | 來源 | 短 | 留主檔 |
| 5 | 互動式教學模式（7 條） | **長、會增補** | 抽 → `interactive-teaching.md` |
| 6 | 🔊 語音播報（+一堆 caveat） | **又長又會增補** | 抽 → `voice-playback.md` |
| 7 | NotebookLM | 短 | 留主檔 |

判斷依據（第二題口訣）：**又長又會增補 → 抽出去；短門面 → 留主檔**。

## 二、產出結構

```
answer/modular-demo/
├─ CLAUDE.md                        # 薄主檔：5 段門面 + 2 行 @import（各附一句註解）
└─ instructions/
   ├─ interactive-teaching.md       # 第 5 段抽出
   └─ voice-playback.md             # 第 6 段抽出
```

主檔引入段：
```markdown
@instructions/interactive-teaching.md   <!-- 互動問答上課的 7 條規則 -->
@instructions/voice-playback.md         <!-- 每回合語音播報流程 + caveat -->
```

## 三、套用第七課三個重點

1. **放哪一層（按重用範圍切）**：這兩段是本 kindle 專案專屬、別專案用不到 → 放**專案自己的** `instructions/`，不是全域 `~/.claude/instructions/`。
2. **不過度拆（第三題代價①）**：`voice-playback.md` 混了「流程指令 + caveat」，日後 caveat 暴漲可再拆 `voice-playback-caveats.md`；現在一段一檔剛好，先不拆。
3. **主檔註解（第三題代價④）**：每個 `@import` 後補一句註解，讓人不打開子檔就知道它管什麼，補上間接層遮蔽的全貌。

## 四、效益對照

| 指標 | 原臃腫版 | 模組化後 |
|------|---------|---------|
| 主檔長度 | 7 段全展開、第 5/6 段佔一大半 | 5 段門面 + 2 行引入，一眼看完 |
| 改教學規則 | 在整個大檔裡撈 | 只開 `interactive-teaching.md` |
| 改語音 caveat | 同上 | 只開 `voice-playback.md`，git diff 乾淨 |
| **token / context** | — | **不變**（`@import` 載入時全展開合併，省的是維護不是 token） |

> 收尾印證第三題：模組化提升的是**維護性**，**不是省 token**。

## 驗收
- [x] 診斷真實臃腫 CLAUDE.md，標出哪幾段該抽
- [x] 實際產出薄主檔 + 2 個具名子檔（modular-demo/）
- [x] 套用三重點：重用範圍分層 / 不過度拆 / 主檔註解
- [x] 安全：不動正在驅動 session 的真實根檔，僅示範
