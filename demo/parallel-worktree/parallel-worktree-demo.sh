#!/usr/bin/env bash
# =============================================================
# parallel-worktree-demo.sh
# 對照《平行化：AI 開發的最大生產力倍增器》的 5 階段生命週期，
# 用 2 條 track 示範：git worktree ×2 + 兩個 headless Claude 平行 + 合併。
# 全程在「用完即焚」的臨時 repo 內，不碰真實專案。
# 用法：./parallel-worktree-demo.sh [DEMO_ROOT]
#   DEMO_ROOT 預設 $HOME/wt-parallel-demo（名稱須含 demo，否則拒跑）
#   環境變數 CLAUDE_BIN 可覆蓋 claude CLI 路徑
# =============================================================
set -euo pipefail

# ---- 可調參數（零硬編碼路徑）----
DEMO_ROOT="${1:-$HOME/wt-parallel-demo}"
CLAUDE_BIN="${CLAUDE_BIN:-claude}"
# headless 要能自主寫檔 → 必須跳過互動式權限詢問（無 TTY 不能跳權限視窗）。
# ⚠️ acceptEdits 會「無人工把關自動接受檔案編輯」，只可在此類拋棄式沙盒目錄跑；
#    且 headless 無 TTY，模型若改用 bash（如跑 python 驗證）會因無法互動授權被自動拒絕，該軌可能失敗。
CLAUDE_FLAGS="-p --permission-mode acceptEdits"

log() { printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }
die() { printf '\n\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# ---- 破壞性防呆：DEMO_ROOT 稍後會被 rm -rf，先擋掉危險值 ----
# 拒絕空 / 根 / 家目錄本身；並要求名稱含 demo，避免誤刪一般目錄
case "$DEMO_ROOT" in
  "" | "/" | "$HOME" | "$HOME/") die "危險的 DEMO_ROOT，拒絕執行：'$DEMO_ROOT'" ;;
esac
[[ "$DEMO_ROOT" == *demo* ]] || die "DEMO_ROOT 名稱須含 'demo'（防止誤刪一般目錄）：'$DEMO_ROOT'"

# 前置檢查：claude CLI 要在（否則整個 demo 無意義）
command -v "$CLAUDE_BIN" >/dev/null 2>&1 || die "找不到 claude CLI（可設 CLAUDE_BIN 覆蓋）"

# ---- 路徑佈局：主 checkout 與兩個 worktree 全收在 DEMO_ROOT 之下 ----
# 好處：任何中途失敗的殘骸都落在同一個可整包刪除的根，不外洩到 $HOME
MAIN_DIR="$DEMO_ROOT/main"
WT_A="$DEMO_ROOT/wt-a"   # 絕對路徑：供 shell cd / 檔案檢查用
WT_B="$DEMO_ROOT/wt-b"
# ⚠️ Git for Windows 對 `git worktree add/remove` 的「POSIX 絕對路徑」會誤轉（/c/… → C:/c/…），
#    MSYS_NO_PATHCONV 也救不了（git.exe 內部轉換）。故 git worktree 一律用「相對於 MAIN_DIR」的相對路徑。
WT_A_REL="../wt-a"
WT_B_REL="../wt-b"

# ---- 失敗自癒：退出時盡力移除殘留 worktree 註冊（成功時已被 Phase 5 清掉，此處冪等）----
cleanup() {
  { [ -d "$MAIN_DIR/.git" ] || [ -f "$MAIN_DIR/.git" ]; } || return 0
  ( cd "$MAIN_DIR" && git worktree remove --force "$WT_A_REL" ) 2>/dev/null || true
  ( cd "$MAIN_DIR" && git worktree remove --force "$WT_B_REL" ) 2>/dev/null || true
}
trap cleanup EXIT

# ---- Phase 0：建乾淨 demo repo（閱後即焚；rm -rf 一次清掉上一輪所有殘骸）----
log "Phase 0｜建立臨時 demo repo：$DEMO_ROOT"
rm -rf "$DEMO_ROOT"; mkdir -p "$MAIN_DIR"; cd "$MAIN_DIR"
git init -q
git commit -q --allow-empty -m "init: 空專案起點"
DEFAULT_BRANCH="$(git symbolic-ref --short HEAD)"  # main/master 皆相容

# ---- Phase 1：Plan — 盤點 2 個各自獨立的任務 ----
# 關鍵：兩條 track 各寫「不同檔案」→ 從根本上避免 merge 衝突
log "Phase 1｜Plan：track-a 產 greet.py、track-b 產 farewell.py（互不踩踏）"

# ---- Phase 2：Create — 先循序建好兩個 worktree（避開 .git/index.lock 競爭）----
# 注意：在 MAIN_DIR 內用相對路徑呼叫（規避上述 Git for Windows 路徑誤轉）
log "Phase 2｜Create：從乾淨主線長出 2 個獨立工作樹 + 分支"
git worktree add -q -b feature/a "$WT_A_REL" "$DEFAULT_BRANCH"
git worktree add -q -b feature/b "$WT_B_REL" "$DEFAULT_BRANCH"

# ---- Phase 3：Execute — 兩個 headless Claude 背景平行開工 ----
exec_track() {                     # $1=worktree絕對路徑  $2=track名  $3=給 Claude 的 prompt
  local wt="$1" name="$2" prompt="$3"
  ( cd "$wt" \
      && $CLAUDE_BIN $CLAUDE_FLAGS "$prompt" \
      && git add -A \
      && git commit -q -m "feat($name): headless Claude 產出" \
  ) > "$DEMO_ROOT/.log-$name.txt" 2>&1
}
log "Phase 3｜Execute：兩個 Claude 實例平行跑（各自 Session／各自目錄）…"
exec_track "$WT_A" a '在此資料夾新增 greet.py：函式 greet(name) 回傳「你好，<name>」，含 None/空字串防禦與 if __name__ 冒煙測試。只新增這一個檔案。' &
PID_A=$!
exec_track "$WT_B" b '在此資料夾新增 farewell.py：函式 farewell(name) 回傳「再見，<name>」，含 None/空字串防禦與 if __name__ 冒煙測試。只新增這一個檔案。' &
PID_B=$!

# ---- Phase 3.5：Wait — 等兩軌都收工 ----
log "Phase 3.5｜Wait：等 track-a(pid $PID_A) 與 track-b(pid $PID_B)"
FAIL=0
wait "$PID_A" || { echo "track-a 失敗，見 $DEMO_ROOT/.log-a.txt"; FAIL=1; }
wait "$PID_B" || { echo "track-b 失敗，見 $DEMO_ROOT/.log-b.txt"; FAIL=1; }
[ "$FAIL" -eq 0 ] || die "有 track 失敗，中止合併（殘留在 $DEMO_ROOT 供查，重跑會自動清）"

# ---- Phase 4：Merge — 回主線依序合併 ----
log "Phase 4｜Merge：回主工作區合併兩條分支"
cd "$MAIN_DIR"
git merge -q feature/a -m "merge: track-a greet.py" \
  || die "合併 feature/a 失敗，請查 $MAIN_DIR（重跑會自動清）"   # 通常 fast-forward
git merge -q feature/b -m "merge: track-b farewell.py" \
  || die "合併 feature/b 失敗，請查 $MAIN_DIR（重跑會自動清）"   # 3-way merge（不同檔→無衝突）

# ---- Phase 5：Clean — 用完即焚（worktree remove 亦用相對路徑）----
log "Phase 5｜Clean：移除 worktree + 刪分支"
git worktree remove "$WT_A_REL"
git worktree remove "$WT_B_REL"
git branch -q -d feature/a feature/b   # 已 merge 進 HEAD，-d 可安全刪

log "完成！主線最終檔案（$MAIN_DIR）："; ls -1
echo; echo "git log："; git log --oneline --graph
