---
description: 把章節 .m4a 一鍵轉錄成繁中摘要筆記，放進對應 demo-chNN 目錄
argument-hint: <章節號，如 9> 或 <完整 m4a 檔名>　[--quality 用 medium 模型]
---

# /chapter-audio — 章節語音轉摘要

輸入：`$ARGUMENTS`

依下列步驟執行（每一步先確認上一步成功；任何步驟失敗就停下回報，附完整錯誤訊息）：

## 1. 找音檔

- 若參數是純數字 N：在 `~/Downloads` 找檔名含「第0N章」或「第N章」的 `.m4a`（用 `ls ~/Downloads/*.m4a` 比對，章節號補零兩位優先）。
- 若參數是檔名：直接用該檔。
- 找不到 → 列出 `~/Downloads/*.m4a` 清單請使用者指定，停。

## 2. 轉 WAV（避開 ffmpeg /tmp 坑）

ffmpeg 是 Windows 程式，**不可**用 `/tmp` 路徑，輸出寫 `~/Downloads`：

```
cd ~/Downloads && ~/Downloads/ffmpeg/bin/ffmpeg -y -i "<m4a>" -ar 16000 -ac 1 -c:a pcm_s16le "chNN.wav"
```

## 3. faster-whisper 轉錄（背景跑，輪詢等完成）

- 預設用 `small` 模型求快；參數含 `--quality` 才用 `medium`。
- `PYTHONUTF8=1`、`language='zh'`、`vad_filter=True`，輸出 `chNN_transcript.txt`（UTF-8）。
- 用 `run_in_background` + 輪詢 output 檔等 `DONE`（medium 可能 20–40 分鐘、small 約 3–6 分鐘）。

```python
from faster_whisper import WhisperModel
m = WhisperModel('small', device='cpu', compute_type='int8')   # --quality 時改 'medium'
segs, info = m.transcribe('chNN.wav', language='zh', beam_size=1, vad_filter=True)
with open('chNN_transcript.txt','w',encoding='utf-8') as f:
    for s in segs: f.write(s.text.strip()+'\n')
print('DONE')
```

## 4. 讀全文 → 產摘要

讀 `chNN_transcript.txt`，用繁體中文寫結構化摘要 `第NN章-摘要筆記.md`：
含「核心主旨 / 重點分節（表格佳）/ 關鍵警告或鐵律 / 一句話總結」，並在開頭註明來源音檔與「轉錄全文見同目錄 ch NN_transcript.txt」。

## 5. 歸位

- 找對應 `demo-chNN-*/` 目錄；不存在則 `mkdir -p demo-chNN`。
- 把 `第NN章-摘要筆記.md` 與 `chNN_transcript.txt` 複製進去。
- 回報兩檔最終路徑 + 大小。

## 注意

- 摘要 `.md` 不觸發 writer/QA 鐵律（純文件）。
- 不硬編碼路徑：一律 `~/Downloads`、`~/workspace/...`。
