#!/bin/bash
set -euo pipefail
# Ralph 自主迴圈驅動腳本
# 為什麼存在：用 TASK.md 的清單驅動「每輪做下一個未完成項」的自主迴圈，
# 並用 5 道護欄防止 AI 自主迴圈最常見的失控（無限燒錢 / 空轉 / 跑飛）。
# 預設提供 --dry-run，可在「完全不呼叫 claude」的情況下驗證整條流程，
# 這是安全設計：先乾跑確認逐輪行為正確，才放心接上真正的 claude 呼叫。

# ---- 全域預設值（why：集中在頂端，方便調整且避免散落魔術數字）----
TASK_FILE="TASK.md"      # 任務清單檔，預設沿用 Ralph 慣例的 TASK.md
MAX_ITER=10              # backstop 上限：最壞情況也只跑這麼多輪，避免無限迴圈
# why：時間窗預設改成非零的 1800 秒（30 分鐘）作安全網。原本預設 0（不限時）
#      等於預設關閉這道護欄，夜間排程一旦卡住就會無限燒；非零預設才是「安全預設」。
#      真要不限時必須明確傳 --max-seconds 0。
MAX_SECONDS=1800
# why：單通 claude 呼叫的逾時上限（秒）。沒有逐通逾時，單一輪卡死會讓整體時間窗
#      與零進展護欄都無從觸發（因為迴圈根本回不來）；用 timeout 包住才救得了。
PER_CALL_TIMEOUT=300
DRY_RUN=0               # 乾跑開關：1 時不呼叫 claude，只模擬完成
DRY_RUN_NOOP=0         # 乾跑但「不打勾」：專供驗證零進展 exit 3 路徑（見 --dry-run-noop）

# why：放寬後的待辦正則 — 允許行首縮排與 - / * / + 三種 markdown 清單符號。
#      原本只認頂格 "- [ ]"，縮排或用 * + 的子項會被誤判成「沒有未完成項」而提早收斂。
TODO_RE='^[[:space:]]*[-*+] \[ \]'

# ---- 退出碼語意（why：讓呼叫端 / CI 能用 exit code 判斷停止原因）----
# 0 = 正常收斂（全部完成）
# 1 = 參數錯誤或環境缺失（如 --max 非數字、找不到 claude）
# 2 = 找不到 TASK 檔
# 3 = 零進展（偵測到空轉，主動停止）
# 4 = 撞上 backstop 上限或逾時

#######################################
# 印出用法說明
#######################################
usage() {
  cat <<'EOF'
用法：ralph_loop.sh [選項]

選項：
  --task FILE          任務清單檔（預設：TASK.md）
  --max N              最大迭代上限 backstop（預設：10）
  --max-seconds S      最大總執行秒數，0 表示不限（預設：1800）
  --per-call-timeout S 單通 claude 呼叫逾時秒數（預設：300）
  --dry-run            乾跑：不呼叫 claude，只印本輪將處理的項目並模擬打勾
  --dry-run-noop       乾跑但不打勾：不呼叫 claude、每輪不推進，用來驗證零進展護欄
  -h, --help           顯示此說明

退出碼：
  0  全部完成（收斂）
  1  參數錯誤或環境缺失
  2  找不到 TASK 檔
  3  偵測到零進展（空轉）而停止
  4  撞上迭代上限或逾時

範例：
  ralph_loop.sh --dry-run --task TASK.md --max 5
  ralph_loop.sh --max 20 --max-seconds 600 --per-call-timeout 120
  ralph_loop.sh --max-seconds 0            # 明確關閉時間窗護欄（不限時）
EOF
}

#######################################
# 解析命令列參數
# why：手寫 case 解析比 getopts 更好支援長選項（--max-seconds 這種）
#######################################
parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --task)
        # why：選項需要值，缺值時友善報錯而非讓 set -u 噴難懂訊息
        [ $# -ge 2 ] || { echo "錯誤：--task 需要一個檔名參數" >&2; exit 1; }
        TASK_FILE="$2"
        shift 2
        ;;
      --max)
        [ $# -ge 2 ] || { echo "錯誤：--max 需要一個數字參數" >&2; exit 1; }
        MAX_ITER="$2"
        shift 2
        ;;
      --max-seconds)
        [ $# -ge 2 ] || { echo "錯誤：--max-seconds 需要一個數字參數" >&2; exit 1; }
        MAX_SECONDS="$2"
        shift 2
        ;;
      --per-call-timeout)
        [ $# -ge 2 ] || { echo "錯誤：--per-call-timeout 需要一個數字參數" >&2; exit 1; }
        PER_CALL_TIMEOUT="$2"
        shift 2
        ;;
      --dry-run)
        DRY_RUN=1
        shift
        ;;
      --dry-run-noop)
        # why：行為同 --dry-run（不呼叫 claude），但刻意不打勾，
        #      讓 remaining 不下降以驗證零進展（exit 3）路徑確實會觸發。
        DRY_RUN=1
        DRY_RUN_NOOP=1
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "錯誤：未知選項 '$1'（用 --help 看用法）" >&2
        exit 1
        ;;
    esac
  done

  # why：MAX_ITER / MAX_SECONDS / PER_CALL_TIMEOUT 之後都要做數值比較，
  # 非數字會讓比較整段炸掉，先驗證可避免 set -e 下出現難以理解的算術錯誤。
  case "$MAX_ITER" in
    ''|*[!0-9]*) echo "錯誤：--max 必須是非負整數，收到 '$MAX_ITER'" >&2; exit 1 ;;
  esac
  case "$MAX_SECONDS" in
    ''|*[!0-9]*) echo "錯誤：--max-seconds 必須是非負整數，收到 '$MAX_SECONDS'" >&2; exit 1 ;;
  esac
  case "$PER_CALL_TIMEOUT" in
    ''|*[!0-9]*) echo "錯誤：--per-call-timeout 必須是非負整數，收到 '$PER_CALL_TIMEOUT'" >&2; exit 1 ;;
  esac
}

#######################################
# 計算 TASK 檔的雜湊值（輔助用途，已非零進展主信號）
# why：零進展偵測改用「未完成項數量單調遞減」後，本函式不再當主信號，
#      僅保留作為日後除錯／落地軌跡的輔助工具（例如想記錄檔案指紋時可用）。
#      偵測能力擇一：sha256sum / md5sum / cksum，跨平台保底。
# 輸出：雜湊字串到 stdout
#######################################
hash_task() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$TASK_FILE" | awk '{print $1}'
  elif command -v md5sum >/dev/null 2>&1; then
    md5sum "$TASK_FILE" | awk '{print $1}'
  else
    # cksum 幾乎所有 POSIX 系統都有，作為最後保底
    cksum "$TASK_FILE" | awk '{print $1}'
  fi
}

#######################################
# 計算 TASK 檔中還有幾個未完成項（"- [ ]" 類）
# why：零進展偵測的主信號 — 比對「未打勾框數」是否單調遞減。
#      grep -c 在找不到匹配時 exit 1 但仍會印出 0，用 "|| true" 吸收非零退出，
#      避免 set -e 把「剛好沒有未完成項」誤當成致命錯誤。
# 輸出：整數（未完成項數量）到 stdout
#######################################
count_remaining() {
  grep -c -E "$TODO_RE" "$TASK_FILE" 2>/dev/null || true
}

#######################################
# 找出第一個未完成項
# why：Ralph 模式核心 — 只認 markdown 待辦語法，每輪取最上面那筆。
#      用放寬正則 TODO_RE 以支援縮排與 - / * / + 符號。
# 輸出：該行文字到 stdout；找不到則輸出空字串
#######################################
find_next() {
  # grep 找第一個符合待辦語法的行；-m1 只取第一筆。
  # why：用 "|| true" 吞掉 grep 找不到時的 exit 1，避免 set -e 直接中止，
  #      「找不到」是正常的收斂訊號，不是錯誤。
  grep -m1 -E "$TODO_RE" "$TASK_FILE" 2>/dev/null || true
}

#######################################
# 把第一個未完成項的 "[ ]" 改成 "[x]"（只改第一筆）
# why：dry-run 要模擬「完成一項」才能讓迴圈推進並讓零進展偵測有效。
#      選用 awk 寫到暫存檔再覆蓋的可攜做法，而非 sed -i：
#      sed -i 在 GNU 與 BSD 語法不同（BSD 需要 -i ''），awk + 暫存檔跨平台最穩。
#######################################
mark_first_done() {
  local tmp
  # why：用 mktemp 產生暫存檔，避免固定檔名在並行或殘留時互相覆蓋
  tmp="$(mktemp 2>/dev/null || echo "${TASK_FILE}.tmp.$$")"
  # why：函式不論從哪條路徑返回都清掉暫存檔，避免中途失敗留下垃圾檔
  trap 'rm -f "$tmp"' RETURN
  # awk：用 done 旗標確保「只替換第一個」匹配，其餘行原樣輸出。
  # why：比對用放寬正則（允許縮排與 *、+ 符號），但只把該行的 "[ ]" 翻成 "[x]"，
  #      保留原本的清單符號（- / * / +），不破壞縮排與符號風格。
  awk '
    !done && /^[[:space:]]*[-*+] \[ \]/ {
      sub(/\[ \]/, "[x]")
      done = 1
    }
    { print }
  ' "$TASK_FILE" > "$tmp" || { echo "錯誤：改寫 TASK 檔失敗" >&2; exit 1; }
  mv "$tmp" "$TASK_FILE" || { echo "錯誤：覆蓋 TASK 檔失敗" >&2; exit 1; }
}

#######################################
# 檢查點：盡量把每輪進度落地（git commit 或寫 log）
# why：Ralph 長時間自主跑，需要可回溯的軌跡；有 git 就 commit，沒有就寫 log。
#      commit 失敗（例如沒有變更）只 warn 不中斷整個迴圈，避免單輪小狀況拖垮全程。
# 參數：$1 = 當前輪次
#######################################
checkpoint() {
  local round="$1"
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # 在 git repo 內：commit 該 TASK 檔的變更
    git add "$TASK_FILE" 2>/dev/null || true
    if ! git commit -m "ralph: round ${round}" >/dev/null 2>&1; then
      # why：沒有實際變更或 hook 擋下時 commit 會非 0，這在迴圈中是可容忍的
      echo "警告：第 ${round} 輪 git commit 未成功（可能無變更），略過" >&2
    fi
  else
    # 非 git 環境：退而求其次留一行 log，至少有時間軸可查
    echo "$(date '+%Y-%m-%d %H:%M:%S') ralph round ${round} done" >> ralph_loop.log \
      || echo "警告：寫入 ralph_loop.log 失敗" >&2
  fi
}

#######################################
# 呼叫 claude 完成下一個未完成項（含逐通逾時保護）
# why：抽成函式讓主迴圈乾淨。逾時（timeout 124）與一般非零退出都「不中止整支」，
#      改交給零進展 / 上限機制接手，符合「單輪失敗 = 該輪無進展」的設計。
# 參數：$1 = 當前輪次（純為訊息可讀性）
#######################################
run_claude() {
  local round="$1"
  local prompt="讀 ${TASK_FILE}，完成下一個未完成項並打勾"
  local rc=0

  if command -v timeout >/dev/null 2>&1; then
    # why：用 timeout 包住，逾時回傳 124；"|| rc=$?" 吸收非零避免 set -e 直接終止整支，
    #      讓零進展 / 上限護欄有機會接手判斷是否該停。
    timeout "$PER_CALL_TIMEOUT" claude -p "$prompt" || rc=$?
    if [ "$rc" -eq 124 ]; then
      echo "警告：第 ${round} 輪 claude 呼叫超過 ${PER_CALL_TIMEOUT} 秒逾時，當作本輪無進展" >&2
    elif [ "$rc" -ne 0 ]; then
      echo "警告：第 ${round} 輪 claude 呼叫回傳非零（rc=${rc}），仍續跑由護欄把關" >&2
    fi
  else
    # why：系統沒有 timeout 指令時退回直接呼叫，明確告知少了逐通逾時保護，
    #      避免使用者誤以為單輪卡死也有上限保護。
    echo "警告：系統無 timeout 指令，本輪無逐通逾時保護" >&2
    claude -p "$prompt" || rc=$?
    if [ "$rc" -ne 0 ]; then
      echo "警告：第 ${round} 輪 claude 呼叫回傳非零（rc=${rc}），仍續跑由護欄把關" >&2
    fi
  fi
}

#######################################
# 主迴圈
#######################################
main() {
  parse_args "$@"

  # ---- 護欄 5：檔案存在護欄 ----
  # why：TASK 檔是整個流程的輸入，不存在就沒得跑，提早給友善訊息比中途炸好。
  if [ ! -f "$TASK_FILE" ]; then
    echo "錯誤：找不到任務檔 '$TASK_FILE'（用 --task 指定，或先建立 TASK.md）" >&2
    exit 2
  fi

  # 非 dry-run 模式才需要 claude；先檢查存在性，缺了就直接停。
  # why：與其每輪呼叫才失敗，不如進迴圈前一次驗證，錯誤訊息更清楚。
  if [ "$DRY_RUN" -eq 0 ] && ! command -v claude >/dev/null 2>&1; then
    echo "錯誤：找不到 claude 指令；請安裝 Claude Code CLI，或改用 --dry-run 乾跑" >&2
    exit 1
  fi

  # ---- 護欄 3（初始化）：零進展偵測改用「未完成項數單調遞減」 ----
  # why：進迴圈前先量一次未完成項基準。這樣即使第 1 輪就完全沒推進
  #      （claude 沒打勾 / 反而新增子任務讓數量變多），下一輪比對時也能立刻抓到。
  local prev_remaining
  prev_remaining="$(count_remaining)"
  local i=1

  # ---- 護欄 1：backstop 上限 ----
  # why：用 while 限制最多 MAX_ITER 輪，是最後一道「再怎樣都不會無限跑」的保險。
  while [ "$i" -le "$MAX_ITER" ]; do

    # ---- 護欄 4：時間窗 ----
    # why：SECONDS 是 bash 內建、腳本啟動以來的秒數；超過上限即停，
    #      防止整體跑超過可接受時間（例如夜間排程預算）。預設 1800 秒，
    #      傳 --max-seconds 0 才關閉這道護欄。
    if [ "$MAX_SECONDS" -gt 0 ] && [ "$SECONDS" -ge "$MAX_SECONDS" ]; then
      echo "已達時間上限 ${MAX_SECONDS} 秒（實際 ${SECONDS} 秒），停止。" >&2
      exit 4
    fi

    # ---- 護欄 2：收斂偵測 ----
    # why：沒有任何未完成項代表清單全部打勾，這是「成功完成」而非錯誤，正常退出 0。
    local next_item
    next_item="$(find_next)"
    if [ -z "$next_item" ]; then
      echo "已收斂，全部完成（共執行 $((i - 1)) 輪）。"
      exit 0
    fi

    echo "===== 第 ${i} 輪 ====="

    if [ "$DRY_RUN" -eq 1 ]; then
      # 乾跑：不呼叫 claude，只印本輪將處理的項目。
      # why：一般 --dry-run 會模擬打勾推進迴圈，讓收斂護欄能觸發；
      #      --dry-run-noop 則刻意不打勾，讓 remaining 不變以驗證零進展（exit 3）。
      echo "[DRY] 本輪將處理：${next_item}"
      if [ "$DRY_RUN_NOOP" -eq 0 ]; then
        mark_first_done
      fi
    else
      # 真實模式：交給 claude 完成下一個未完成項並自行打勾（含逐通逾時保護）。
      run_claude "$i"
    fi

    # 落地本輪進度（git commit 或 log）
    checkpoint "$i"

    # ---- 護欄 3：零進展偵測（未完成項數未減少即停止）----
    # why：改用「未打勾框數」而非整檔雜湊，是因為雜湊只要任何位元變動就算「有進展」，
    #      會把 claude 亂改一行卻沒真正完成任務當成推進。改看未完成項是否確實變少，
    #      才能抓到「claude 新增子任務使其變多」或「原地打轉沒打勾」這類假進展。
    local remaining
    remaining="$(count_remaining)"
    if [ "$remaining" -ge "$prev_remaining" ]; then
      echo "偵測到零進展（未完成項未減少：${prev_remaining} -> ${remaining}），停止避免空轉。" >&2
      exit 3
    fi
    prev_remaining="$remaining"

    i=$((i + 1))
  done

  # ---- 護欄 1（續）：跑完 while 仍未收斂，代表撞到 backstop 上限 ----
  echo "已達迭代上限 ${MAX_ITER} 輪仍未完成，停止（請檢查 TASK 是否過大或卡住）。" >&2
  exit 4
}

main "$@"
