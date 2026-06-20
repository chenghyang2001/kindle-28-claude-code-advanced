"""中文 GUI 語音播放器（say_ui.py）。

把文字用 edge-tts 合成語音，提供 tkinter GUI：播放/暫停、重播、變速、
循環、講稿顯示、離開。音訊引擎用 Windows Media Player COM（非阻塞播放，
tkinter mainloop 全程保持回應，因此不需要額外 threading）。

文字來源優先序：--file > --text > 系統剪貼簿。

與既有的 say.py 完全獨立，互不影響。
"""

# 版本資訊：初版 GUI 視為 1.00，本次新增音量控制 + 版本號顯示故升為 1.01。
# 放模組級常數，方便標題列顯示與外部 import 查版。
__version__ = "1.01"
__release_date__ = "2026-06-20"

# 標準庫
import argparse
import asyncio
import locale
import os
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

# 第三方：COM 相關。pythoncom 必須在主執行緒先 CoInitialize，
# 否則 win32com 建立 WMPlayer.OCX 會拋 com_error。
import pythoncom
import win32com.client

# 本地模組：純函式夾制邏輯抽到 audio_utils 便於獨立測試
from audio_utils import clamp_rate, clamp_volume

# 變速步進：每次「變慢／變快」按鈕的增減幅度（夾界常數已移至 audio_utils）。
RATE_STEP = 0.25

# 音量步進：每次「音量增大／減小」按鈕的增減幅度（夾界常數已移至 audio_utils）。
VOLUME_STEP = 10

# 預設語音
DEFAULT_VOICE = "zh-TW-HsiaoChenNeural"


def resource_path(relative):
    """解析資源檔在執行時的真實路徑，相容 PyInstaller onefile 與原始碼直跑。

    為什麼不能直接用相對路徑：PyInstaller 打包成 onefile exe 後，執行時會把
    內嵌資源解壓到一個隨機暫存資料夾並把路徑記在 sys._MEIPASS，而 exe 的「工作
    目錄」是使用者當前所在目錄（可能在任何地方），兩者不相等。若直接用相對路徑或
    __file__ 旁的路徑去找資源，打包後會抓不到檔案。因此這裡優先取 sys._MEIPASS
    當基底；取不到（代表是從原始碼 .py 直跑）時，退回本檔所在目錄。
    """
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


def parse_args():
    """解析命令列參數。"""
    parser = argparse.ArgumentParser(description="中文 GUI 語音播放器")
    parser.add_argument("-f", "--file", help="從 UTF-8 檔讀取講稿文字")
    parser.add_argument("--text", help="直接指定講稿文字")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="edge-tts 語音名稱")
    parser.add_argument("--autoplay", action="store_true", help="啟動後自動開始播放，免手動按播放")
    return parser.parse_args()


def read_clipboard(root):
    """讀取系統剪貼簿內容當講稿。

    優先用 tkinter clipboard_get（同進程、免外部呼叫）；剪貼簿無文字時會拋
    TclError，此時退到 PowerShell Get-Clipboard。subprocess 輸出的編碼依系統
    而定（cp950），故用 locale.getpreferredencoding 並對無法解碼字元 replace，
    避免因編碼錯誤崩潰。
    """
    try:
        return root.clipboard_get()
    except tk.TclError:
        # tkinter 取不到（剪貼簿非文字或為空）→ 改用 PowerShell
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                capture_output=True,
                check=True,
            )
        except (OSError, subprocess.SubprocessError):
            return ""
        encoding = locale.getpreferredencoding(False)
        return completed.stdout.decode(encoding, errors="replace").strip()


def resolve_text(args, root):
    """依優先序 file > text > clipboard 取得講稿文字。"""
    if args.file:
        # 明確指定 utf-8，不依賴系統預設編碼（cp950 會讀錯中文）
        with open(args.file, encoding="utf-8") as fh:
            return fh.read().strip()
    if args.text:
        return args.text.strip()
    return read_clipboard(root).strip()


def enlarge_fonts(root, delta=3):
    """把 Tk 具名字型在現有大小上加 delta，讓整個 GUI 字體變大。

    用具名字型（TkDefaultFont 等）統一放大，按鈕/標籤/講稿一起生效，
    不必逐一 widget 設 font。Tk 字型 size 為負代表像素、為正代表點數，
    兩者「絕對值越大字越大」，故依正負號決定加減方向，確保一律變大。
    """
    import tkinter.font as tkfont
    for name in ("TkDefaultFont", "TkTextFont", "TkFixedFont",
                 "TkMenuFont", "TkHeadingFont", "TkTooltipFont"):
        try:
            f = tkfont.nametofont(name)
        except tk.TclError:
            continue
        size = f.cget("size")
        if size < 0:
            f.configure(size=size - delta)  # 像素：更負=更大
        else:
            f.configure(size=size + delta)  # 點數：更大


def synth_to_mp3(text, voice):
    """用 edge-tts 把文字合成 MP3，回傳暫存檔路徑。

    暫存路徑用 tempfile 產生（不硬編碼使用者路徑）。檔名本身雖可能含使用者名，
    但 NamedTemporaryFile 產生的是 ASCII 安全字元，避免 WMP 載入含非 ASCII
    路徑時偶發的載入失敗。delete=False 讓檔案在 with 區塊外仍存在供播放，
    由 on_close 負責清除。
    """
    import edge_tts  # 延遲 import：缺套件時於 main 統一處理，給友善提示

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        mp3_path = tmp.name

    async def _run():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(mp3_path)

    asyncio.run(_run())
    return mp3_path


class WmpAudio:
    """封裝 Windows Media Player COM 物件，提供非阻塞播放控制。

    WMP playState 數字意義（controls.currentItem 播放狀態）：
      1 = Stopped, 2 = Paused, 3 = Playing。is_playing 以 3 判斷。
    """

    def __init__(self):
        # autoStart=False：載入 URL 後不自動播放，等使用者按「播放」才出聲
        self._player = win32com.client.Dispatch("WMPlayer.OCX")
        self._player.settings.autoStart = False
        self._rate = 1.0

    def load(self, path):
        """載入音檔（不自動播放）。"""
        self._player.URL = path

    def play(self):
        """開始/繼續播放。"""
        self._player.controls.play()

    def pause(self):
        """暫停播放。"""
        self._player.controls.pause()

    def is_playing(self):
        """目前是否正在播放（playState == 3）。"""
        return self._player.playState == 3

    def toggle(self):
        """播放/暫停切換，回傳切換後是否正在播放。"""
        if self.is_playing():
            self.pause()
            return False
        self.play()
        return True

    def replay(self):
        """從頭重播：先把播放位置歸零再 play。"""
        self._player.controls.currentPosition = 0
        self.play()

    def set_rate(self, rate):
        """設定倍速（內部 clamp 後套用到 settings.rate），回傳實際值。"""
        actual = clamp_rate(rate)
        self._player.settings.rate = actual
        self._rate = actual
        return actual

    @property
    def rate(self):
        """目前倍速。"""
        return self._rate

    def set_loop(self, flag):
        """設定循環播放。"""
        self._player.settings.setMode("loop", bool(flag))

    def set_volume(self, volume):
        """設定音量（內部 clamp 後套用到 settings.volume），回傳實際值。"""
        actual = clamp_volume(volume)
        self._player.settings.volume = actual
        return actual

    def get_volume(self):
        """讀取目前音量（整數 0~100）。"""
        return self._player.settings.volume

    def change_volume(self, delta):
        """在目前音量上 ±delta 後 set_volume，回傳新音量。供增大/減小按鈕使用。"""
        return self.set_volume(self.get_volume() + delta)

    def toggle_mute(self):
        """切換靜音狀態，回傳切換後的 mute（True=靜音中）。

        用 settings.mute 而非把 volume 歸零，是為了保留原音量值，
        取消靜音時音量自動回復，不必另存先前數值。
        """
        new_mute = not self._player.settings.mute
        self._player.settings.mute = new_mute
        return new_mute

    def close(self):
        """停止播放並釋放 COM 物件。"""
        try:
            self._player.controls.stop()
        except pythoncom.com_error:
            # 物件可能已失效，忽略停止失敗
            pass
        self._player = None


def _make_transcript_widget(root, text):
    """建立唯讀講稿顯示區（ScrolledText）。"""
    box = ScrolledText(root, wrap=tk.WORD, height=12, width=50)
    box.insert(tk.END, text)
    # 設 disabled 讓使用者不能編輯，但仍可選取；編輯不影響已合成的播放內容
    box.configure(state=tk.DISABLED)
    box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
    return box


def build_ui(root, text, audio, autoplay=False):
    """建立所有 widget、callback、狀態更新並綁定關閉事件。

    刻意不呼叫 mainloop，讓 QA 能建立 UI 而不阻塞測試。
    """
    root.title(f"中文語音播放器 v{__version__}（{__release_date__}）")
    # 預設視窗尺寸放大，配合字型 +3 後較大的控制列與講稿區，避免內容被擠壓
    root.geometry("1040x600")

    # 設定標題列自訂 icon（取代 Tk 預設羽毛圖示）。
    # 用 try/except 防呆：icon 只是裝飾，ico 檔缺失或格式不符時 iconbitmap 會拋
    # tk.TclError，此時直接略過、沿用預設圖示，絕不可因裝飾性問題讓整個 GUI 崩潰。
    try:
        root.iconbitmap(resource_path("app_icon.ico"))
    except tk.TclError:
        pass

    state = {"rate": audio.rate}

    _make_transcript_widget(root, text)

    status_var = tk.StringVar(value="狀態：就緒")
    rate_var = tk.StringVar(value=f"速度 {audio.rate:.2f}x")
    loop_var = tk.BooleanVar(value=False)
    # 初始即讀目前音量顯示，讓 label 與 WMP 實際音量一致
    volume_var = tk.StringVar(value=f"音量 {audio.get_volume()}")

    def set_status(label):
        status_var.set(f"狀態：{label}")

    def on_toggle():
        playing = audio.toggle()
        play_btn.configure(text="⏸ 暫停" if playing else "▶ 播放")
        set_status("播放中" if playing else "已暫停")

    def on_replay():
        audio.replay()
        play_btn.configure(text="⏸ 暫停")
        set_status("播放中")

    def apply_rate(new_rate):
        actual = audio.set_rate(new_rate)
        state["rate"] = actual
        rate_var.set(f"速度 {actual:.2f}x")

    def on_slower():
        apply_rate(state["rate"] - RATE_STEP)

    def on_faster():
        apply_rate(state["rate"] + RATE_STEP)

    def on_loop_toggle():
        audio.set_loop(loop_var.get())

    def on_volume_up():
        volume_var.set(f"音量 {audio.change_volume(VOLUME_STEP)}")

    def on_volume_down():
        volume_var.set(f"音量 {audio.change_volume(-VOLUME_STEP)}")

    def on_mute_toggle():
        # toggle_mute 回傳 True 代表現在靜音中，故按鈕文字提供「取消靜音」操作
        muted = audio.toggle_mute()
        mute_btn.configure(text="取消靜音" if muted else "靜音")

    def on_close():
        # 停止播放 → 釋放 COM → 刪暫存檔。任何一步失敗都不該讓關閉崩潰。
        try:
            audio.close()
        except pythoncom.com_error:
            pass
        mp3_path = getattr(root, "_mp3_path", None)
        if mp3_path:
            try:
                os.unlink(mp3_path)
            except OSError:
                pass
        root.destroy()

    # 控制按鈕列
    controls = tk.Frame(root)
    controls.pack(fill=tk.X, padx=8, pady=4)

    play_btn = tk.Button(controls, text="▶ 播放", width=8, command=on_toggle)
    play_btn.pack(side=tk.LEFT, padx=2)
    tk.Button(controls, text="↻ 重播", width=8, command=on_replay).pack(side=tk.LEFT, padx=2)
    tk.Button(controls, text="− 變慢", width=8, command=on_slower).pack(side=tk.LEFT, padx=2)
    tk.Button(controls, text="＋ 變快", width=8, command=on_faster).pack(side=tk.LEFT, padx=2)
    tk.Label(controls, textvariable=rate_var, width=12).pack(side=tk.LEFT, padx=4)

    # 音量控制列：順序固定為 增大 → 減小 → 靜音，後接音量數值 label
    volume_bar = tk.Frame(root)
    volume_bar.pack(fill=tk.X, padx=8, pady=4)
    tk.Button(
        volume_bar, text="音量增大", width=8, command=on_volume_up
    ).pack(side=tk.LEFT, padx=2)
    tk.Button(
        volume_bar, text="音量減小", width=8, command=on_volume_down
    ).pack(side=tk.LEFT, padx=2)
    mute_btn = tk.Button(volume_bar, text="靜音", width=8, command=on_mute_toggle)
    mute_btn.pack(side=tk.LEFT, padx=2)
    tk.Label(volume_bar, textvariable=volume_var, width=12).pack(side=tk.LEFT, padx=4)

    # 循環 + 離開列
    bottom = tk.Frame(root)
    bottom.pack(fill=tk.X, padx=8, pady=4)
    tk.Checkbutton(
        bottom, text="循環播放", variable=loop_var, command=on_loop_toggle
    ).pack(side=tk.LEFT, padx=2)
    tk.Button(bottom, text="離開", width=8, command=on_close).pack(side=tk.RIGHT, padx=2)

    # 狀態列
    tk.Label(root, textvariable=status_var, anchor=tk.W, relief=tk.SUNKEN).pack(
        fill=tk.X, side=tk.BOTTOM
    )

    # 右上角 X 也走同一個關閉流程
    root.protocol("WM_DELETE_WINDOW", on_close)

    # 自動播放：若指定 --autoplay，啟動即觸發一次播放（沿用 on_toggle 讓按鈕文字/狀態同步）
    if autoplay:
        on_toggle()


def main():
    """組裝參數、合成、UI 並進入 mainloop。"""
    # COM 必須在主執行緒初始化，否則後續 Dispatch 會失敗
    pythoncom.CoInitialize()

    args = parse_args()
    root = tk.Tk()
    # 在隱藏前先放大具名字型，讓後續 build_ui 建立的所有 widget 都吃到大字體
    enlarge_fonts(root, delta=7)
    root.withdraw()  # 先隱藏，等內容備妥再顯示，避免空白視窗閃現

    try:
        text = resolve_text(args, root)
    except OSError as exc:
        messagebox.showerror("讀取失敗", f"無法讀取檔案：{exc}")
        root.destroy()
        sys.exit(1)

    if not text:
        messagebox.showerror("沒有文字", "沒有可念的文字（剪貼簿為空或檔案為空）")
        root.destroy()
        sys.exit(1)

    try:
        mp3_path = synth_to_mp3(text, args.voice)
    except ImportError:
        messagebox.showerror("缺少套件", "找不到 edge-tts，請先執行：pip install edge-tts")
        root.destroy()
        sys.exit(1)
    except Exception as exc:  # edge-tts 網路/合成錯誤，統一給可讀提示
        messagebox.showerror("合成失敗", f"語音合成失敗：{exc}")
        root.destroy()
        sys.exit(1)

    try:
        audio = WmpAudio()
        audio.load(mp3_path)
    except pythoncom.com_error as exc:
        messagebox.showerror("音訊引擎錯誤", f"無法初始化播放器：{exc}")
        # 引擎建不起來也要清掉剛合成的暫存檔
        try:
            os.unlink(mp3_path)
        except OSError:
            pass
        root.destroy()
        sys.exit(1)

    # 把暫存路徑掛到 root 供 on_close 清理
    root._mp3_path = mp3_path
    build_ui(root, text, audio, autoplay=args.autoplay)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
