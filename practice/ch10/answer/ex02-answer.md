# 練習 02 解答：對 itsdangerous 做一次小型 audit

- 對象：`vendor/itsdangerous`（commit `672971d`，`2.3.0.dev`），**只讀不改**。
- `檔案:行號` 皆相對於 `vendor/itsdangerous/src/itsdangerous/`。
- 佐證腳本：`scripts/ex02_audit_probe.py`（輸出存於 `scripts/ex02_output.txt`）；行號用 `grep -n` 逐檔確認。
- 基準：官方測試 `297 passed`（本專案 `.venv`，含 `freezegun`）。

> 前提說明：itsdangerous 是成熟、被 Flask 大量使用的函式庫，核心設計（先驗簽再反序列化、`hmac.compare_digest`）是對的。下面多數發現屬於「**誤用時會出事的設計**」或「**防禦深度不足**」，不是可直接被遠端利用的漏洞。分級以「使用者照文件正常使用時，出事的機率 × 影響」來判斷。

## 任務 1：audit 發現（10 項）

| # | 嚴重度 | 類別 | 位置 | 一句話 |
| --- | --- | --- | --- | --- |
| F1 | **高** | 安全（DoS） | serializer.py:389-393、url_safe.py:44-46 | `loads_unsafe` 對**未驗簽**資料做**無上限** zlib 解壓 |
| F2 | 中 | 正確性／API | timed.py:182-191 vs serializer.py:328-330 | `TimedSerializer.loads` 第 2 個位置參數是 `max_age` 不是 `salt` |
| F3 | 中 | 安全（輸入驗證） | signer.py:67-73、143、196 | 空字串 key 照收；空 list 到簽章時才 `IndexError` |
| F4 | 中 | 安全（危險預設可用） | signer.py:31-37、**init**.py:12 | `NoneAlgorithm` 是公開 API，用了就能零成本偽造 |
| F5 | 低 | 安全（演算法老舊） | signer.py:54、120 | 預設 HMAC-SHA1 |
| F6 | 低 | 安全（情境隔離） | serializer.py:193、signer.py:132 | 預設 salt 固定，不同用途共用時 token 可跨用途重放 |
| F7 | 低 | 正確性（吞例外） | signer.py:231、timed.py:114-115 | `except Exception` 吞掉後回 `False`／`pass` |
| F8 | 低 | 維護性 | signer.py:89-93、124-127 vs 210、213 | `"none"` 推導法沒寫進文件；未知推導法延遲到簽章才報錯，且型別用 `TypeError` |
| F9 | 低 | 維護性（重複邏輯） | timed.py:185-220 vs serializer.py:328-343 | `loads` 迴圈邏輯整段複製，有 `TODO` 與 `type: ignore[override]` |
| F10 | 低 | 正確性（時鐘偏差） | timed.py:148-153 | 簽章時間比現在晚 1 秒就判定過期，沒有容許誤差 |

### F1（高）`loads_unsafe` 解壓炸彈

- **位置**：`_loads_unsafe_impl` 在簽章驗證失敗後，仍拿 `e.payload` 去 `load_payload`（serializer.py:389-393）；URL-safe 版的 `load_payload` 對 `.` 開頭的 payload 直接 `zlib.decompress(json)`，**沒有輸出上限**（url_safe.py:44-46）。
- **為什麼是問題**：正常 `loads` 先驗簽，偽造的 token 在解壓前就被擋掉（serializer.py:339）；但 `loads_unsafe` 把「解壓 + JSON 解析」暴露給**任何人**都能做出來的 token。攻擊者只要送一小段壓縮過的超大 JSON，就能讓伺服器配置數百倍的記憶體。文件雖寫「僅供除錯」（serializer.py:359-361），但只警告 pickle，沒提到 URL-safe 版本的解壓問題，實務上常有人拿它來「先看看 token 內容再決定」。
- **實測**（`f1_zip_bomb`）：

  ```text
  F1 token 只有 27,216 bytes
     loads()        → BadSignature，5.7 ms，峰值 0.2 MB
     loads_unsafe() → ok=False, 解出 20,971,520 字元，51.9 ms，峰值 60.1 MB（放大 770x）
  ```

  token 27 KB → 峰值記憶體 60 MB；把 `BOMB_SIZE` 調大，放大倍數會線性成長（zlib 理論上限約 1000:1）。
- **建議修法**：見任務 2。

### F2（中）`TimedSerializer.loads` 位置參數陷阱

- **位置**：`Serializer.loads(self, s, salt=None, **kwargs)`（serializer.py:328-330）；`TimedSerializer.loads(self, s, max_age=None, return_timestamp=False, salt=None)`（timed.py:185-191），作者自己在 timed.py:182-183 留了 `TODO: Signature is incompatible`，並用 `# type: ignore[override]` 壓掉型別警告。
- **為什麼是問題**：違反里氏替換原則。同一行 `s.loads(token, "ctx")` 換了 serializer 類別行為就變。
- **實測**（`f2_positional_salt`）：

  ```text
  F2 同樣寫法 loads(token, 'ctx')：Serializer 成功、TimedSerializer → BadTimeSignature
     預設 salt 的 token 則爆未包裝的 TypeError：'>' not supported between instances of 'int' and 'str'
  ```

  第二種情況更糟：`TypeError` 不是 `BadData` 子類別，呼叫端的 `except BadSignature` 接不到，會變成 500 錯誤。（Pyright 對這行有報 `reportArgumentType`，有跑型別檢查的專案能提早發現。）
- **建議修法**：下個大版把 `max_age`、`return_timestamp` 改成 keyword-only（`def loads(self, s, salt=None, *, max_age=None, return_timestamp=False)`）；過渡期在 `max_age` 不是 `int | None` 時發 `DeprecationWarning` 並當成 salt 處理。

### F3（中）沒驗證 secret key

- **位置**：`_make_keys_list` 只做型別轉換，不檢查長度或是否為空（signer.py:67-73），建構子直接收下（signer.py:143）；`derive_key` 用 `self.secret_keys[-1]`（signer.py:196），空 list 時才炸。
- **實測**（`f3_weak_keys`）：

  ```text
  F3 Signer('') 可簽：b'admin.SvypXjgS-1GbQKhUTunmvKLGGJI'（任何人都能用空 key 重算）
     Signer([]) 建構成功，sign 時才 IndexError：list index out of range
  ```

  常見事故：`SECRET_KEY = os.environ.get("SECRET_KEY", "")` 忘了設環境變數 → 所有 token 都能被任何人偽造，而且**完全不會報錯**。
- **建議修法**：建構子裡 `if not self.secret_keys or any(len(k) == 0 for k in self.secret_keys): raise ValueError(...)`；長度 < 16 bytes 發 `UserWarning`。

### F4（中）`NoneAlgorithm` 是公開 API

- **位置**：`NoneAlgorithm.get_signature` 永遠回 `b""`（signer.py:31-37），並從套件頂層匯出（**init**.py:12）。
- **實測**（`f4_none_algorithm`）：`Signer("k", algorithm=NoneAlgorithm()).unsign(b"role=admin.")` → `b'role=admin'`，任何人都能偽造。這和 JWT 史上著名的 `alg: none` 問題同型。
- **建議修法**：移出頂層 `__init__`（僅供測試用），或在建構時發 `UserWarning("NoneAlgorithm 不做任何簽章")`。

### F5（低）預設 HMAC-SHA1

- **位置**：signer.py:54、120（`default_digest_method = staticmethod(_lazy_sha1)`）。
- **為什麼列為低**：HMAC-SHA1 目前**沒有**實用的偽造攻擊（SHA1 的碰撞攻擊不直接適用於 HMAC），文件也說明了這點（signer.py:96-97）。但很多合規稽核（FIPS、公司資安政策）會直接標紅 SHA1；`_lazy_sha1` 的註解（signer.py:41-44）也承認 FIPS 環境可能沒有 SHA1。
- **實測**：`f5_sha1_default` 印出 `_lazy_sha1`、簽章長度 27 字元（20 bytes）。
- **建議修法**：新專案自行傳 `signer_kwargs={"digest_method": hashlib.sha256}`；函式庫端可在大版改預設並保留 SHA1 為 `fallback_signers`（serializer.py:297-307 已支援平滑遷移）。

### F6（低）預設 salt 固定

- **位置**：`Serializer` 預設 `salt=b"itsdangerous"`（serializer.py:193），`Signer` 預設 `b"itsdangerous.Signer"`（signer.py:132）。
- **實測**（`f6_default_salt`）：「退訂」用的 token 直接被「重設密碼」用的 serializer 接受 → `{'user': 42}`。
- **為什麼列為低**：文件有明確要求不同用途用不同 salt（signer.py:80-82），屬使用者責任；但預設值讓「沒讀文件」的人默默踩坑。
- **建議修法**：使用端每個用途都給 salt；函式庫可考慮把 salt 改成必填（不給就警告）。

### F7（低）吞例外

- **位置**：`verify_signature` 裡 `except Exception: return False`（signer.py:229-232）；`TimestampSigner.unsign` 裡 `except Exception: pass`（timed.py:112-115）。
- **為什麼是問題**：base64 解碼只會丟 `BadData`（encoding.py:35-38），這裡用 `Exception` 太寬，會把程式 bug（例如 `AttributeError`）也悄悄變成「簽章無效」，除錯困難。
- **佐證**：`grep -n "except Exception" src/itsdangerous/*.py` → signer.py:231、timed.py:114（另外 serializer.py:264、url_safe.py:38/47 也是寬捕捉，但有用 `raise ... from e` 保留原因，可接受）。
- **建議修法**：改成 `except BadData:`（timed.py 則是 `except (BadData, struct.error):`）。

### F8（低）文件與實作不一致、錯誤延遲

- **位置**：docstring 只列 `concat`、`django-concat`、`hmac`（signer.py:89-93、124-127），實作卻多一個 `"none"`（signer.py:210-211，直接把原始 key 當 HMAC key）；未知名稱到 `derive_key` 才 `raise TypeError`（signer.py:213），建構時不檢查。
- **實測**（`f8_lazy_derivation_error`）：`Signer("k", key_derivation="bogus")` 建構成功，`sign()` 才丟 `TypeError: Unknown key derivation method`；應該是 `ValueError`（值錯，不是型別錯）。
- **建議修法**：建構子用集合檢查並丟 `ValueError`；docstring 補上 `none`。

### F9（低）`loads` 邏輯重複

- **位置**：timed.py:199-220 與 serializer.py:334-343 幾乎是同一個「逐個 signer 嘗試、記住最後例外」的迴圈，只差多了 `SignatureExpired` 的提早中止與時間戳回傳。
- **為什麼是問題**：之後修 bug（例如 F2 的參數調整）要改兩處，容易漏。
- **建議修法**：在 `Serializer` 抽出 `_try_unsigners(s, salt, unsign_kwargs, stop_on=())`，兩個 `loads` 都呼叫它。

### F10（低）無時鐘誤差容忍

- **位置**：`if age < 0: raise SignatureExpired(...)`（timed.py:148-153）。
- **實測**（`f10_clock_skew`）：簽章機時鐘快 2 秒 → `SignatureExpired: Signature age -2 < 0 seconds`。多台伺服器、NTP 偏差時會出現偶發失敗。另外例外名稱是「過期」，實際是「來自未來」，訊息也容易誤導。
- **建議修法**：加 `leeway` 參數（例如預設 0，可設 5 秒），`if age < -leeway`。

## 任務 2：最嚴重項（F1）的具體修補方向

### 修法

1. **在 `URLSafeSerializerMixin.load_payload` 加解壓上限**（url_safe.py:44-51）：

   ```python
   max_decompressed_size: int = 10 * 1024 * 1024  # 類別屬性，可被子類別覆寫

   if decompress:
       d = zlib.decompressobj()
       try:
           json = d.decompress(json, self.max_decompressed_size)
       except zlib.error as e:
           raise BadPayload("Could not zlib decompress the payload", original_error=e) from e
       if d.unconsumed_tail or not d.eof:
           raise BadPayload("Decompressed payload exceeds max_decompressed_size")
   ```

   用 `decompressobj().decompress(data, max_length)` 是 zlib 標準的防炸彈寫法：輸出到上限就停，剩下的留在 `unconsumed_tail`。

2. **`loads_unsafe` 的 docstring**（serializer.py:352-361）補一句：「URL-safe serializer 會在驗簽前解壓，請勿用於不受信任的輸入」。

3. **測試**（加到 `tests/test_itsdangerous/test_url_safe.py`）：
   - 正常：2,000 字的 payload 壓縮後仍可 `dumps` → `loads` 往返。
   - 邊界：解壓後剛好等於上限 → 成功；上限 + 1 → `BadPayload`。
   - 攻擊：20 MB 炸彈丟給 `loads_unsafe` → 回 `(False, None)`，且 `tracemalloc` 峰值 < 上限的 2 倍。

### 已驗證這個方向可行

`scripts/ex02_audit_probe.py` 裡的 `BoundedURLSafeSerializer` 用**子類別**（不改 vendor）實作了上面的第 1 點，上限設 1 MB：

```text
修補後 loads_unsafe → ok=False, value=None，3.6 ms，峰值 2.1 MB
修補後正常壓縮 token 仍可往返（回歸測試 OK）
```

峰值記憶體從 60.1 MB 降到 2.1 MB，正常 token 不受影響。

### 使用端在函式庫修好之前的權宜做法

- 不要對外部輸入呼叫 `loads_unsafe`；需要「看內容」時先 `loads`，在 `except BadSignature` 裡只記錄 log、不解析 payload。
- 或在 Web 層限制 token 長度（例如 cookie／query string 超過 4 KB 直接拒絕），能大幅壓低放大後的上限。

## 延伸思考：onboard 陌生專案時先讀什麼？順序為什麼重要？

這次實際用的順序與花費：

| 順序 | 讀什麼 | 為什麼放這個位置 |
| --- | --- | --- |
| 1 | `pyproject.toml`、目錄結構、`wc -l` | 1 分鐘知道規模（8 檔 1.2k 行）、Python 版本、相依，決定要不要全讀 |
| 2 | `__init__.py` | 公開 API 清單，就是「這個專案對外承諾什麼」，也是後續 audit 的攻擊面清單（F4 就是從這裡發現的） |
| 3 | 先跑測試 | 確認環境可跑、建立基準（297 passed），之後的實驗結果才可信 |
| 4 | 依相依方向**由下往上**讀：`encoding` → `signer` → `serializer` → `timed` → `url_safe` | 讀上層時下層的名詞都已認識，不用來回跳 |
| 5 | 寫小腳本驗證理解（ex01 的 5 題） | 把「我以為」變成「我確認」，也順便變成 audit 的佐證工具 |

順序重要的原因：

- **先廣後深**：先有地圖，才知道哪些細節值得深挖；直接從最長的檔案讀起，容易在不重要的型別 overload 上浪費時間（serializer.py 前 180 行大半是 `@t.overload`）。
- **先建立可執行的基準**：測試先跑過，之後任何「好像怪怪的」都能馬上用腳本證實或推翻，audit 發現才附得出證據，而不是猜測。
- **onboard 的產物可以直接接 audit**：練習 01 弄懂「驗簽一定在反序列化之前」這條不變式後，練習 02 只要找「哪裡破壞了這條不變式」，就直接找到 F1。
