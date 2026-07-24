# AI 短影音工具研究 — 如何做出 Dr Julie 風格的 YouTube Shorts

> 研究日期：2026-07-24
> 參照影片：<https://www.youtube.com/shorts/C_lm5Si34XU（Dr> Julie「How To Master Your Emotions」）

## 目標影片格式

Dr Julie（英國臨床心理師 Julie Smith）的 Shorts 是短影音心理科普經典模板：
**真人對鏡頭講話（talking head）+ 大字幕 + 快節奏剪接 + 9:16 豎屏 + 60 秒內講完一個觀點**。

用 AI 重現的關鍵是「願意投入多少真人成分」，分三條路線。

## 路線 A：願意露臉拍，AI 只做後製（最像原片）

| 工具 | 做什麼 |
| --- | --- |
| **Captions** | 首選：自動大字幕、眼神接觸修正（唸稿眼神飄自動修成看鏡頭）、自動 jump cut、配音修復 |
| CapCut | 免費備選：自動字幕 + 模板，效果略陽春 |

## 路線 B：拍一次建數位分身，之後打字就出片（效率最高）

| 工具 | 做什麼 |
| --- | --- |
| **Argil** | 上傳 2 分鐘自拍建分身，之後打字稿即生成你講話的豎屏短片（含字幕 + B-roll）。定位「每天想發片但討厭上鏡」，最貼近 Dr Julie 使用場景 |
| **HeyGen** | 更全能：600+ 虛擬人、175 語言、腳本→影片→字幕→B-roll 一站式，可把長片自動剪成 Shorts。缺點：成品偏企業簡報感 |

## 路線 C：完全不露臉，純 AI 生成

| 工具 | 做什麼 |
| --- | --- |
| **OmniHuman 1.5** | 一張照片 + 一段音檔 → 會講話的 talking head（搭 ElevenLabs 或 edge-tts 做旁白） |
| **Veo 3.x**（Google） | 原生生成帶對白 + 自動對嘴的影片，直接 prompt 出講者 |
| **Sora 2 + n8n** | n8n 有現成 faceless Shorts 自動發布 workflow 模板，生成→發布全自動 |
| Fliki / ElevenLabs Video | 組裝層：AI 影片 + 配音 + 字幕 + 音樂打包成品 |

## 建議

1. **最像原片** → 路線 B 的 **Argil**：此格式核心是「同一張可信的臉持續出現」，分身路線才能複製；純生成每支影片人臉不一致，觀眾黏著度差。
2. **最貼現有工具鏈** → 路線 C 的 **n8n Sora 2 workflow**：已有 n8n Cloud + Blotato 六平台發布 + edge-tts + NotebookLM 語音摘要，管線後半段已建好，只缺影片生成節點。
3. **提醒**：專家科普類內容用 AI 分身記得標註 AI 生成，且不可克隆他人（包括 Dr Julie 本人）的臉或聲音，只能用自己的或平台授權虛擬人。

## 參考來源

- HeyGen: Best AI Video Tools for YouTube Creators in 2026 — <https://www.heygen.com/blog/best-ai-video-tools-youtube-creators-2026>
- Pixo: 7 HeyGen Alternatives in 2026 — <https://pixo.video/blog/heygen-alternatives>
- Venture Harbour: Best AI Avatar Video Generators Head-to-Head — <https://ventureharbour.com/best-ai-avatar-software/>
- n8n workflow: Generate & publish AI faceless videos to YouTube Shorts using Sora 2 — <https://n8n.io/workflows/10455-generate-and-publish-ai-faceless-videos-to-youtube-shorts-using-sora-2/>
- ElevenLabs Video Generation Guide 2026 — <https://elevenlabsmagazine.com/elevenlabs-video-generation-guide-2026/>
- Fliki AI Video Generator — <https://fliki.ai/features/ai-video-generator>
- Powtoon: Veo 3 vs. Sora Side-by-Side 2026 — <https://www.powtoon.com/blog/veo-3-vs-sora/>
