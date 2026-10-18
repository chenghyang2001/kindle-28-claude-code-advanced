| 任務 | model | 實際 model ID | total_cost_usd | duration_ms | 輸出 tokens | cache 建立 / 讀取 tokens | 相對 Haiku |
|---|---|---|---:|---:|---:|---:|---:|
| format | haiku | claude-haiku-5-5 | 0.00276 | 2530 | 215 | 12428 / 16672 | 1.0x |
| format | sonnet | claude-sonnet-5-5 | 0.04855 | 1720 | 27 | 11651 / 16672 | 17.6x |
| format | opus | claude-opus-5-5 | 0.09724 | 2105 | 41 | 11645 / 16279 | 35.2x |
| analysis | haiku | claude-haiku-5-5 | 0.00227 | 2192 | 202 | 9902 / 19247 | 1.0x |
| analysis | sonnet | claude-sonnet-5-5 | 0.04245 | 2591 | 98 | 9905 / 18467 | 18.7x |
| analysis | opus | claude-opus-5-5 | 0.08701 | 4890 | 210 | 9899 / 18074 | 38.3x |
| reasoning | haiku | claude-haiku-5-5 | 0.00237 | 3200 | 397 | 9888 / 19247 | 1.0x |
| reasoning | sonnet | claude-sonnet-5-5 | 0.04324 | 2754 | 183 | 9891 / 18467 | 18.3x |
| reasoning | opus | claude-opus-5-5 | 0.08718 | 4593 | 224 | 9885 / 18074 | 36.8x |
