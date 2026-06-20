"""WMP 倍速／音量的邊界夾制純函式（從 say_ui.py 抽出，便於獨立測試）。

純函式、無 I/O、無 side-effect、只用內建。clamp_volume 先 int() 再夾界，
因為 WMP settings.volume 只吃整數 0~100。
"""

# 倍速範圍：WMP settings.rate 在 0.5~2.0 外播放品質劣化甚至無聲，故統一夾此區間。
RATE_MIN = 0.5
RATE_MAX = 2.0

# 音量範圍：WMP settings.volume 僅接受整數 0~100，超界會被忽略或拋錯，故夾此區間。
VOLUME_MIN = 0
VOLUME_MAX = 100


def clamp_rate(rate: float) -> float:
    """把倍速夾在 [RATE_MIN, RATE_MAX]，回傳實際值。"""
    return max(RATE_MIN, min(RATE_MAX, rate))


def clamp_volume(volume) -> int:
    """把音量先轉 int 再夾在 [VOLUME_MIN, VOLUME_MAX]，回傳整數。"""
    return max(VOLUME_MIN, min(VOLUME_MAX, int(volume)))


if __name__ == "__main__":
    # 冒煙測試：邊界值
    assert clamp_rate(1.0) == 1.0
    assert clamp_rate(5.0) == RATE_MAX
    assert clamp_rate(0.1) == RATE_MIN
    assert clamp_volume(50) == 50
    assert clamp_volume(150) == VOLUME_MAX
    assert clamp_volume(-10) == VOLUME_MIN
    assert clamp_volume(33.7) == 33
    print("audio_utils 冒煙測試通過")
