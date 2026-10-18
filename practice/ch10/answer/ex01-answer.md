# 練習 01 解答：30 分鐘 onboard itsdangerous

- 目標 repo：<https://github.com/pallets/itsdangerous>（`git clone --depth 1` 到 `./vendor/itsdangerous`，commit `672971d`，版本 `2.3.0.dev`）
- 限制：**只讀不改**。所有實驗都寫在本專案的 `scripts/`，用 `sys.path` 匯入 vendor 原始碼。
- 以下 `檔案:行號` 都是相對於 `vendor/itsdangerous/src/itsdangerous/`。

## 0. onboarding 指令流（實際執行）

```bash
git log --oneline -20                 # depth 1 只有 1 筆：672971d Merge branch 'stable'
git ls-files | sed 's@/[^/]*$@@' | sort -u
wc -l src/itsdangerous/*.py           # 8 檔、共 1176 行
PYTHONPATH=src .venv/Scripts/python -m pytest -q   # 297 passed in 1.13s
```

目錄概覽：`src/itsdangerous/`（程式）、`tests/test_itsdangerous/`（5 個測試檔，一個模組一檔）、`docs/`、`pyproject.toml`、`uv.lock`、`.github/workflows`。

> 第一次跑測試時 `test_timed.py`、`test_url_safe.py` 因缺 `freezegun` 收集失敗；在本專案 `.venv` 裝 `pytest freezegun` 後 297 個全過（沒有裝到全域）。

## 任務 1：模組地圖與資料流

### 模組地圖（依相依方向，由下往上）

```text
                        __init__.py  （公開 API：把下面所有類別 re-export）
                              │
        ┌─────────────────────┼──────────────────────────┐
        ▼                     ▼                          ▼
  url_safe.py            timed.py                   serializer.py
  URLSafeSerializer      TimestampSigner(Signer)    Serializer
  URLSafeTimedSerializer TimedSerializer(Serializer)  ├ dump_payload / load_payload（序列化）
  （zlib 壓縮 + base64）   （加時間戳、max_age 過期）  ├ make_signer / iter_unsigners（挑簽章器）
        │                     │                       └ dumps / loads / loads_unsafe
        └──────────┬──────────┴──────────────┬───────────┘
                   ▼                         ▼
              signer.py                   _json.py（緊湊 JSON）
              Signer：derive_key → get_signature → sign / unsign
              SigningAlgorithm ← HMACAlgorithm / NoneAlgorithm
                   │
                   ▼
   encoding.py（want_bytes、base64 編解碼、int↔bytes）   exc.py（例外階層）
```

例外階層（`exc.py`）：

```text
BadData
 ├─ BadSignature ─┬─ BadTimeSignature ── SignatureExpired
 │                └─ BadHeader
 └─ BadPayload
```

### 資料流：`URLSafeTimedSerializer("secret").dumps({"id": 1})`

```text
{"id":1}
  │ _CompactJSON.dumps（_json.py:15-18，去空白）
  ▼
b'{"id":1}'
  │ URLSafeSerializerMixin.dump_payload（url_safe.py:55-69）
  │   壓縮後若有變短才用壓縮版，並在前面加 '.'（url_safe.py:60-67）
  ▼
b'eyJpZCI6MX0'                         ← base64url payload
  │ TimestampSigner.sign（timed.py:45-51）
  │   value = payload + '.' + base64(int_to_bytes(now))
  │   簽章 = Signer.get_signature(value)（signer.py:215-220）
  │        = base64( HMAC-SHA1( derive_key(), value ) )
  │   derive_key 預設 django-concat = sha1(salt + b"signer" + key)（signer.py:202-205）
  ▼
'eyJpZCI6MX0.atRVYg.4OxgercsqGiGW2LyJbnXrdHGyWQ'
   └payload──┘ └ts──┘ └──────signature─────────┘
```

`loads()` 是反向：`iter_unsigners` 產生簽章器（serializer.py:287-307）→ `unsign` 驗簽（signer.py:244-256）→ 檢查時間（timed.py:137-153）→ `load_payload` 解 base64／解壓／JSON（url_safe.py:23-53 → serializer.py:243-269）。

**重點：驗簽一定發生在反序列化之前**（serializer.py:339 `self.load_payload(signer.unsign(s))`），這是整個函式庫安全性的核心。唯一的例外是 `loads_unsafe`（見練習 02 F1）。

### 先讀的 3 個關鍵檔

1. `signer.py`：安全核心（金鑰推導、HMAC、常數時間比較 `hmac.compare_digest` 在 signer.py:28）。
2. `serializer.py`：所有高階 API 的骨架，`loads`／`iter_unsigners` 決定驗證順序。
3. `timed.py`：最常用的 `URLSafeTimedSerializer` 的過期邏輯，例外處理最複雜的地方。

### `/init` 式 CLAUDE.md 草稿（因 vendor 只讀，草稿放這裡不寫進 vendor）

```markdown
# itsdangerous
用 HMAC 簽章資料，讓資料可安全地交給不受信任的環境再拿回來驗證（例如 Flask session、重設密碼連結）。
- 原始碼：src/itsdangerous/（8 檔，約 1.2k 行，無第三方相依）
- 測試：tests/test_itsdangerous/（pytest + freezegun）；執行 `pytest`
- 分層：encoding → signer → serializer → timed → url_safe；exc 為例外階層
- 不變式：loads 必須先驗簽再反序列化；loads_unsafe 是唯一例外（僅除錯用）
- Python >= 3.10（pyproject.toml）
```

## 任務 2：3 個看不懂的地方 → 自問自答（附證據 + 實驗）

驗證腳本：`scripts/ex01_probe.py`，輸出存於 `scripts/ex01_output.txt`，5 題全部通過。

### Q1：`secret_key` 可以傳 list，簽章到底用哪一把？驗證又用哪幾把？

- `_make_keys_list` 把字串或 list 統一成 `list[bytes]`（signer.py:67-73、143）。
- **簽章**用最後一把：`derive_key()` 沒給參數時取 `self.secret_keys[-1]`（signer.py:196）。
- **驗證**從最新到最舊逐把試：`for secret_key in reversed(self.secret_keys)`（signer.py:236）。
- 所以 key 輪替的做法是「新 key 加在 list 最後；舊 key 留到舊 token 全部過期再移除」。
- 實驗：`Signer(["old-key","new-key"])` 能驗證舊 key 簽的 token，且新簽章等於 `Signer("new-key")` 的結果 → **Q1 OK**。

### Q2：簽章是怎麼算出來的？能自己手算嗎？

- 預設 `key_derivation="django-concat"`（signer.py:127），推導金鑰 = `sha1(salt + b"signer" + key)`（signer.py:202-205）。
- 預設 salt 是 `b"itsdangerous.Signer"`（signer.py:132），預設 digest 是 SHA1（signer.py:120，透過 `_lazy_sha1` 在 signer.py:40 延遲取用，避免 FIPS 環境匯入就失敗）。
- 簽章 = `HMAC(推導金鑰, value, sha1)`（signer.py:62-64），再做 base64url 並去掉 `=`（encoding.py:20-25）。
- 實驗：用 `hashlib`＋`hmac` 手算出 `7KTthSs1fJgtbigPvFpQH1bpoGA`，與 `Signer(b"secret").get_signature(b"hello")` 完全相同 → **Q2 OK**。

### Q3：token 的三段是什麼？有些 token 為什麼以 `.` 開頭？

- 格式：`payload.timestamp.signature`。時間戳是 `int_to_bytes(秒數)` 去掉前導 0 後的 base64（timed.py:48、encoding.py:49-50）。
- 開頭的 `.` 是**壓縮旗標**：`dump_payload` 只有在 zlib 壓縮後真的變短才採用，並在前面加 `.`（url_safe.py:58-67）；`load_payload` 看到 `.` 開頭就先解壓（url_safe.py:32-34、44-46）。
- `.` 能當旗標又能當分隔符，是因為分隔符被禁止出現在 base64 字母表內（encoding.py:42、signer.py:146），而 `.` 不在字母表裡，不會和 payload 內容混淆。
- 實驗：`{"id":1}` 的 token 是 `eyJpZCI6MX0.atRVYg.4Oxg…`，payload 解回 `{"id":1}`、時間戳解回 `1792300386`；500 個 `a` 的 token 以 `.` 開頭、只有 70 字 → **Q3 OK**。

### Q4：過期和簽章錯誤有差嗎？為什麼過期時不再試下一個簽章器？

- `TimestampSigner.unsign` 先驗簽，驗簽失敗包成 `BadTimeSignature`（timed.py:119-130）；**簽章正確**但太舊才是 `SignatureExpired`（timed.py:138-146）。
- `TimedSerializer.loads` 遇到 `SignatureExpired` 直接往外丟、不試下一個 fallback 簽章器（timed.py:213-216）。原因：能判斷過期代表簽章已經驗過、是真的 token，再試其他 key 沒有意義，也避免把「過期」誤報成「簽章錯誤」。
- 實驗：100 秒前簽、`max_age=10` → `SignatureExpired`，且帶 `date_signed`；換錯的 key → `BadTimeSignature` 而非過期 → **Q4 OK**。

### Q5：payload 自己就含 `.` 時，切割會不會切錯？

- `unsign` 用 `rsplit(self.sep, 1)`，**只從右邊切一刀**（signer.py:251）；簽章是 base64，不會含分隔符，所以最後一段一定是簽章。
- 時間版再從右邊切一次拿出時間戳（timed.py:108）。
- 實驗：`Signer("k").sign(b"a.b.c")` 能正確 `unsign` 回 `b"a.b.c"`；`Signer("k", sep="a")` 直接 `ValueError` → **Q5 OK**。

## 驗收

- [x] 有一張高階架構／資料流圖（模組地圖 + dumps 資料流 + 例外階層）
- [x] 至少 3 個疑點被追問釐清（5 題，每題附檔案:行號，並用 `scripts/ex01_probe.py` 實際驗證）
