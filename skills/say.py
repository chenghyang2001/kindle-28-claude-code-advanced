"""say.py — 中文文字轉語音 CLI 工具。

把一段繁體中文文字用 edge-tts 轉成 MP3 語音並在 Windows 上播放。
這是從一段已驗證可行的手動流程固化而成的可重用工具。

用法範例：
    python say.py "你好，世界"
    python say.py -f input.txt --voice zh-TW-YunJheNeural
    python say.py "只想存檔不播放" --no-play --out hello.mp3
"""
import argparse
import asyncio
import locale
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# 預設語音：實測 zh-TW-HsiaoChenNeural 念繁體中文最自然
DEFAULT_VOICE = "zh-TW-HsiaoChenNeural"

# 取不到音檔長度時的保底播放秒數，避免 PowerShell 永遠等不到結束
FALLBACK_PLAY_SECONDS = 60


def parse_args() -> argparse.Namespace:
    """解析 CLI 參數。"""
    parser = argparse.ArgumentParser(
        description="把中文文字用 edge-tts 轉成 MP3 並播放（Windows）。"
    )
    parser.add_argument("text", nargs="?", help="要念的文字（與 --file 二擇一）")
    parser.add_argument("-f", "--file", help="從檔案讀取文字（UTF-8 編碼）")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="語音名稱")
    parser.add_argument("--out", help="輸出 MP3 路徑（未指定則輸出到暫存檔）")
    parser.add_argument(
        "--no-play", action="store_true", help="只產生 MP3 不播放"
    )
    return parser.parse_args()


def resolve_text(args: argparse.Namespace) -> str:
    """從 positional 或 --file 取得要念的文字，並驗證非空。"""
    # 必須提供 text 或 --file 其一
    if not args.text and not args.file:
        print("錯誤：請提供要念的文字，或用 --file 指定文字檔。", file=sys.stderr)
        sys.exit(1)

    if args.file:
        try:
            # 一律 UTF-8 讀檔，不依賴系統預設 cp950
            text = Path(args.file).read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"錯誤：找不到檔案 {args.file}", file=sys.stderr)
            sys.exit(1)
        except UnicodeDecodeError as exc:
            print(f"錯誤：檔案非 UTF-8 編碼：{exc}", file=sys.stderr)
            sys.exit(1)
        except OSError as exc:
            print(f"錯誤：讀取檔案失敗：{exc}", file=sys.stderr)
            sys.exit(1)
    else:
        text = args.text

    # 空字串（含純空白）視為無效輸入
    if not text.strip():
        print("錯誤：文字內容為空。", file=sys.stderr)
        sys.exit(1)
    return text


def generate_mp3(text: str, voice: str, out_path: str) -> None:
    """用 edge-tts 把文字轉成 MP3 存到 out_path。"""
    try:
        # edge_tts 可能未安裝，單獨 catch 給友善提示
        import edge_tts
    except ImportError:
        print(
            "錯誤：缺少 edge-tts 套件，請執行：pip install edge-tts",
            file=sys.stderr,
        )
        sys.exit(1)

    async def _run() -> None:
        # edge_tts 原生輸出 MP3，save() 直接寫檔
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(out_path)

    try:
        asyncio.run(_run())
    except Exception as exc:  # noqa: BLE001 - edge_tts 例外型別多樣，統一回報
        print(f"錯誤：TTS 產生失敗：{exc}", file=sys.stderr)
        sys.exit(1)


def _build_powershell_script(ascii_path: str) -> str:
    """組出播放 MP3 並等播完的 PowerShell 腳本。"""
    # PowerShell 單引號字串中，內含的單引號要用兩個單引號（''）跳脫成一個 '。
    # Windows 帳號名允許含單引號（如 O'Brien），tempfile 產生的暫存路徑會帶入該帳號名，
    # 不跳脫會讓字串提前閉合、後段被當成程式碼執行（路徑注入 / 破圖）。
    safe_path = ascii_path.replace("'", "''")
    # $ErrorActionPreference='Stop' + try/catch：任何 cmdlet 錯誤都拋出並以 exit 1 反映到 returncode。
    # MediaFailed 是非同步事件，掛 handler 用 synchronized hashtable 設旗標；
    # 開檔/播放失敗時設旗標 → throw → exit 1，否則腳本仍 returncode=0 會把真失敗當成功（偽陰性）。
    # 結束前必須 Get-EventSubscriber | Unregister-Event + Get-Job | Remove-Job -Force：
    # Register-ObjectEvent 會在背景留下 event subscriber 與對應 job，若不清掉，runspace
    # 拆除時 PowerShell 會以非 0（實測 exit 2）退出，Python 端「只看 returncode != 0」就把
    # 完全成功的播放誤判為失敗（偽陰性）。實機隔離：清理後可穩定 exit 0。
    # catch 區塊不用 Write-Error：在 $ErrorActionPreference='Stop' 下 Write-Error 本身是
    # terminating，後面的 exit 1 跑不到、stderr 也可能空。改用 [Console]::Error.WriteLine
    # 直接寫 stderr，再明確 exit 1，確保失敗訊息與 returncode 都正確傳回。
    return (
        "$ErrorActionPreference='Stop'; "
        "try { "
        "Add-Type -AssemblyName presentationCore; "
        "$state = [hashtable]::Synchronized(@{Failed=$false}); "
        "$player = New-Object System.Windows.Media.MediaPlayer; "
        "Register-ObjectEvent -InputObject $player -EventName MediaFailed "
        "-MessageData $state -Action { $Event.MessageData.Failed = $true } | Out-Null; "
        f"$player.Open([uri]'{safe_path}'); "
        "$player.Play(); "
        "$waited = 0; "
        "while (-not $player.NaturalDuration.HasTimeSpan -and -not $state.Failed -and $waited -lt 50) "
        "{ Start-Sleep -Milliseconds 100; $waited++ }; "
        "if ($state.Failed) { throw 'MediaFailed：開檔或播放失敗' }; "
        "if ($player.NaturalDuration.HasTimeSpan) "
        "{ $dur = $player.NaturalDuration.TimeSpan.TotalSeconds } "
        f"else {{ $dur = {FALLBACK_PLAY_SECONDS} }}; "
        "Start-Sleep -Seconds ([int]$dur + 1); "
        "if ($state.Failed) { throw 'MediaFailed：開檔或播放失敗' }; "
        "$player.Stop(); $player.Close(); "
        "Get-EventSubscriber | Unregister-Event; Get-Job | Remove-Job -Force; "
        "exit 0 "
        "} catch { [Console]::Error.WriteLine('播放失敗：' + $_.Exception.Message); exit 1 }"
    )


def play_mp3(mp3_path: str) -> None:
    """在 Windows 上用 PowerShell MediaPlayer 播放 MP3 並等播完。"""
    # 非 Windows 平台沒有這套 PowerShell，僅提示不視為錯誤
    if os.name != "nt":
        print(f"目前播放僅支援 Windows，已產出 MP3：{mp3_path}")
        return

    # 重大坑：PowerShell 子行程不繼承 Git Bash 的 CWD，且含中文/方括號
    # 的路徑（如 [03-計畫模式]）傳進 PowerShell 會被編碼搞壞，導致開檔失敗。
    # 解法：先複製到 ASCII-only 的暫存路徑，再用絕對 ASCII 路徑餵給 PowerShell。
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    ascii_path = tmp.name
    tmp.close()
    try:
        shutil.copyfile(mp3_path, ascii_path)
        script = _build_powershell_script(ascii_path)
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True,
                text=True,
                # 為什麼不用 encoding="utf-8"：Windows PowerShell 5.1 的錯誤/警告訊息（常含中文）
                # 以「主控台 codepage」輸出，台灣機器系統預設是 cp950，不是 UTF-8。若硬用 utf-8 解碼，
                # 一旦 stderr 出現中文位元組就丟 UnicodeDecodeError 直接 traceback，反而在「PowerShell
                # 真的報錯」時把要回報的失敗訊息吃掉。改用系統預設編碼 + errors="replace"：解碼絕不崩潰，
                # 最壞只是少數無法對應的字元變成 �，失敗訊息仍讀得到。
                encoding=locale.getpreferredencoding(False),
                errors="replace",
            )
        except FileNotFoundError:
            print("錯誤：找不到 powershell，無法播放。", file=sys.stderr)
            sys.exit(1)

        # 只用 returncode 判定失敗：PowerShell 正常播放時也可能往 stderr 印 verbose/deprecation
        # 雜訊（若據此判失敗會偽陽性）；而真正的失敗已由腳本端 try/catch + MediaFailed → exit 1
        # 反映到 returncode（解決偽陰性）。stderr 一律只當 warning 印出，不據以 sys.exit。
        if result.returncode != 0:
            stderr_summary = (result.stderr or "").strip()[:300]
            print(f"錯誤：播放失敗：{stderr_summary}", file=sys.stderr)
            sys.exit(1)
        if result.stderr and result.stderr.strip():
            # 非致命：僅提示，不中斷流程（避免把 verbose/deprecation 雜訊誤判為失敗）
            print(f"提醒：PowerShell stderr：{result.stderr.strip()[:300]}", file=sys.stderr)
    finally:
        # 暫存複本用完即刪，避免堆積在系統暫存目錄
        try:
            os.unlink(ascii_path)
        except OSError:
            pass


def main() -> None:
    """CLI 進入點：取得文字 → 產 MP3 →（視情況）播放。"""
    args = parse_args()
    text = resolve_text(args)

    # 未指定 --out 時輸出到暫存檔，仍是合法 MP3 路徑
    if args.out:
        out_path = args.out
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        out_path = tmp.name
        tmp.close()

    generate_mp3(text, args.voice, out_path)
    print(f"已產出 MP3：{out_path}")

    if args.no_play:
        print("（--no-play 指定，未播放）")
        return

    play_mp3(out_path)
    print("播放完成。")


if __name__ == "__main__":
    main()
