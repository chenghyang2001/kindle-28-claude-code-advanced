"""帳號系統的命令列介面：從 stdin 逐行讀取指令，每行指令輸出一行結果。

指令格式（以空白切分，段數必須精確）：
- register <帳號> <密碼>：輸出 auth.AuthStore.register 的回傳錯誤碼
- login <帳號> <密碼>：輸出 auth.AuthStore.login 的回傳錯誤碼
- quit：結束迴圈，不輸出任何東西

其他情況（未知指令、段數不對、空白行、無法解碼的行）一律輸出 E_BAD_COMMAND。
讀到 EOF 也會結束。整個程式執行期間共用同一個 AuthStore 實例，
因此前一行的 register 會影響後面的 login。
"""
import sys
from typing import Optional

from auth import AuthStore

# 格式錯誤的統一回應。沿用 auth.py 的字串錯誤碼風格，呼叫端可以直接比對。
E_BAD_COMMAND = "E_BAD_COMMAND"


def process_line(store: AuthStore, line: str) -> Optional[str]:
    """解析並執行一行指令，回傳要輸出的結果。

    回傳 None 代表收到 quit，呼叫端應該停止讀取。
    段數檢查放在這裡而不是交給 AuthStore，因為「格式錯誤」與「帳號密碼錯誤」
    是不同層級的問題，混在一起會讓呼叫端無法分辨使用者是打錯指令還是帳密不對。
    """
    parts = line.split()
    # 空白行或只有空白：沒有指令可執行，視為格式錯誤。
    if not parts:
        return E_BAD_COMMAND

    command = parts[0]
    if command == "quit":
        # quit 必須單獨一段；"quit xyz" 不是合法的結束指令，當成格式錯誤繼續讀。
        return None if len(parts) == 1 else E_BAD_COMMAND

    if command in ("register", "login"):
        # 帳號與密碼各佔一段，缺段或多段都代表格式錯誤，不猜測使用者意圖。
        if len(parts) != 3:
            return E_BAD_COMMAND
        username, password = parts[1], parts[2]
        if command == "register":
            return store.register(username, password)
        return store.login(username, password)

    return E_BAD_COMMAND


def main() -> int:
    """CLI 進入點：讀取 stdin 並逐行輸出結果，正常結束回傳 0。"""
    store = AuthStore()

    # 以 buffer 讀取並明確用 UTF-8 解碼，不依賴系統預設編碼（Windows 下可能是 cp950），
    # 含中文的帳號才不會被誤解碼。
    # 直接讀 buffer 並逐行解碼，而不是迭代 text 串流：
    # text 串流遇到解碼錯誤後無法保證能從下一行正確續讀，
    # 逐行解碼可以確保壞掉的那一行只影響它自己。
    # 使用 utf-8-sig 是為了吃掉記事本存檔時在首行加上的 BOM（EF BB BF），
    # 否則第一個指令會變成 "﻿register"，被誤判為 E_BAD_COMMAND。
    # 逐行解碼時只有首行開頭會有 BOM，其他行不受影響。
    for raw_line in sys.stdin.buffer:
        try:
            line = raw_line.decode("utf-8-sig")
        except UnicodeDecodeError:
            # 單行解碼失敗不應讓整個程式崩潰，印出格式錯誤後繼續處理下一行。
            print(E_BAD_COMMAND, flush=True)
            continue

        result = process_line(store, line)
        if result is None:
            break
        # 每行非 quit 指令都要恰好輸出一行，因此這裡不做任何過濾或合併。
        print(result, flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
