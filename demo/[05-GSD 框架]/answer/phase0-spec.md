# Phase 0 規格／合約 — audio_utils.py

> GSD 綜合挑戰專案：把 `say_ui.py` 的純函式抽成獨立可測模組。
> 這份是 Phase 0 交付物，也是 Builder 必須遵守的合約。

## 目標
建立 `skills/audio_utils.py`，提供 WMP 倍速／音量的**邊界夾制純函式**，
讓 `say_ui.py` 改 import 它（移除原本的內嵌定義），達成關注點分離與可獨立測試。

## 對外 API（合約）

```python
# 常數
RATE_MIN = 0.5
RATE_MAX = 2.0
VOLUME_MIN = 0
VOLUME_MAX = 100

def clamp_rate(rate: float) -> float:
    """把倍速夾在 [RATE_MIN, RATE_MAX]，回傳實際值。"""

def clamp_volume(volume) -> int:
    """把音量轉 int 後夾在 [VOLUME_MIN, VOLUME_MAX]，回傳整數。"""
```

## 行為規格（輸入→輸出）
| 函式 | 輸入 | 輸出 |
|------|------|------|
| clamp_rate | 1.0 | 1.0 |
| clamp_rate | 5.0（超上界） | 2.0 |
| clamp_rate | 0.1（超下界） | 0.5 |
| clamp_volume | 50 | 50 |
| clamp_volume | 150（超上界） | 100 |
| clamp_volume | -10（超下界） | 0 |
| clamp_volume | 33.7（浮點） | 33（先 int 再夾） |

## 邊界 / 約束
- 純函式，**無 I/O、無 side-effect、無外部相依**（只用內建）。
- `clamp_volume` 必須先 `int()` 再夾界（WMP volume 只吃整數）。
- 不可改變既有夾制語意（與目前 say_ui.py 行為等價）。

## 整合要求（Phase 3）
- `say_ui.py` 移除內嵌 `RATE_MIN/RATE_MAX/VOLUME_MIN/VOLUME_MAX` 與 `clamp_rate/clamp_volume`，
  改 `from audio_utils import clamp_rate, clamp_volume`。
- 保留 `RATE_STEP / VOLUME_STEP / DEFAULT_VOICE`（UI 仍用）。
- 行為、UI、autoplay 全部不變。

## gate 條件
- Phase 0：本規格定案 ✅
- Phase 1：簽名/型別齊全、可 import
- Phase 2：單元測試全綠（涵蓋上表 7 個 case）
- Phase 3：say_ui.py 改用後可編譯 + exe 重打包後冒煙測試出聲
- Phase 4：MANIFEST 串起所有交付物
