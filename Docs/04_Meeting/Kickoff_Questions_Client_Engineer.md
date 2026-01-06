# Code Converter - Kick-off Meeting 問題清單

> **角色**：Client Side Engineer (iOS / Android / WAP)  
> **會議對象**：PM, Backend Engineer  
> **目的**：釐清 Phase 1 (Code2Code) 實作細節

---

## 🔴 高優先度問題（阻擋開發）

### 📋 問 PM 的問題

| # | 問題 | PRD 敘述 |
|---|------|----------|
| 1 | 轉換成功後，是**自動跳轉** Betslip 還是顯示 **CTA 按鈕**讓使用者點擊？ | PRD 寫：「App：顯示成功訊息：『已轉換為 Fcom 投注碼 AF1234』、**自動開啟 Betslip** 並載入選項」及「生成的 Fcom Booking Code 會**自動載入** Fcom Betslip」 |
| 2 | PARTIAL 狀態時，使用者可以繼續投注已成功的選項嗎？還是需要全部成功才能投注？ | PRD 寫：「轉換結果為 Success（或 **Partial，如果 Phase 1 將部分載入視為有效**）且 Betslip 已載入」—— 但未明確說明 Partial 是否允許下注 |
| 3 | Bookie 清單從哪邊來？會根據使用者地區（NG/GH）不同而不同嗎？ | PRD 環境表格列出「BE: NG, GH」，並列出支援的 Bookies 表格（Sporty, MSport, Bet9ja...共 11 個）—— 但未說明資料來源及是否依地區篩選 |

### 💻 問 BE 的問題

| # | 問題 | PRD 敘述 |
|---|------|----------|
| 4 | `ConvertCompetitorCode` API 的完整 Request / Response Schema 是什麼？ | PRD 僅提及：<br>**輸入類型**：`type = COMPETITOR_CODE`（原始文字碼 + 來源博彩公司）<br>**回傳**：Booking Code、正規化選項清單、錯誤／部分匹配資訊（如有）<br>——缺少完整 Schema 定義 |
| 5 | `conversion_request_id` 何時生成？失敗時是否一定會回傳？ | PRD 寫：「Betslip 載入事件必須帶有唯一的 `conversion_request_id`（或等效的任務／請求識別碼）以確保端到端的可追溯性」—— 但未說明失敗時是否回傳 |
| 6 | Response 中的 `status` enum 有哪些值？ | PRD 寫：「狀態：`PENDING` → `PROCESSING` → `SUCCESS` / `FAILED` / `PARTIAL`」—— 但這是 Job 狀態，API Response 的 status 是否相同？ |
| 7 | PARTIAL 狀態時，`missing` 欄位的資料格式是什麼？ | PRD 寫：「部分對應：『我們轉換了部分選項，但有些在 Fcom 上不可用。』**如果可能，顯示缺失的賽事／盤口清單**」及「我們只能轉換 5 個選項中的 3 個。缺失的賽事：…」—— 但未定義資料結構 |
| 8 | Bookie 下拉選單的資料來源是什麼？Hardcoded / Config / API？ | PRD 寫：「使用者從下拉選單選擇競品博彩公司（例如：Bet9ja、BetKing 等）」及列出支援的 Bookies 表格（Sporty, MSport, Bet9ja...共 11 個）—— 但未說明資料來源 |
| 9 | 如果是 API，Bookie 清單的 Endpoint 和 Response 格式是什麼？ | PRD 未提及 Bookie 清單 API |

---

## 🟡 中優先度問題（影響 UX 品質）

### 📋 問 PM 的問題

| # | 問題 | PRD 敘述 |
|---|------|----------|
| 16 | 輸入錯誤提示的時機是？即時驗證（onChange）還是提交時（onSubmit）？ | PRD 僅寫：「使用者輸入 Booking Code 文字並點擊 **Load Code**」—— 未說明驗證時機 |
| 17 | 載入 Betslip 時，如果 Betslip 已有其他選項，是**覆蓋**還是**追加**？ | PRD 寫：「自動開啟 Betslip 並載入選項」—— 未說明與既有選項的處理方式 |
| 18 | 載入後的選項，賠率是即時的還是轉換當下的快照？ | PRD 寫：「賠率（如果需要用於對應／驗證）」—— 但未說明顯示給使用者的賠率是即時還是快照 |
| 19 | Phase 1 的最終 Figma node-id 是哪個？目前 PRD 提到的 `24353-69` 是最新版嗎？ | PRD Figma 連結：`https://www.figma.com/design/SvcTlADMZ7gUPIa7nN2hT1/Code-Converter?node-id=24353-69` |
| 20 | SUCCESS / PARTIAL / FAILED 三種狀態的 UI 分別對應哪個 Figma node？ | PRD 僅提供一個 Figma 連結，未區分各狀態的 node-id |
| 21 | Loading 動畫有特定設計嗎？還是使用通用 Loading Indicator？ | PRD 未提及 Loading 設計 |

### 💻 問 BE 的問題

| # | 問題 | PRD 敘述 |
|---|------|----------|
| 22 | Booking Code 的輸入格式規則是什麼？有長度限制嗎？ | PRD 寫：「使用者輸入 Booking Code 文字並點擊 Load Code」—— 未定義格式規則 |
| 23 | 輸入框允許空白和特殊分隔符嗎？需要 Client 端 trim 嗎？ | PRD 未提及輸入格式處理 |
| 24 | `selections` 資料格式是什麼？和現有 Betslip 的 Model 相容嗎？ | PRD 寫回傳包含「正規化選項清單」，正規化結構為：<br>• 賽事 ID / 名稱<br>• 盤口 ID / 名稱<br>• 選項 ID / 名稱<br>• 賠率<br>—— 但未定義完整 Schema |
| 25 | 賠率資料是 BE 回傳還是 Client 需要另外 fetch？ | PRD 寫：「賠率（如果需要用於對應／驗證）」—— 不確定是否包含在 Response 中 |

### 📊 問 DA 的問題

| # | 問題 | PRD 敘述 |
|---|------|----------|
| 26 | `betslip_load` 事件的完整參數定義是什麼？ | PRD 寫：「Betslip 載入事件必須帶有：<br>• `source = "code_converter"`<br>• 唯一的 `conversion_request_id`」<br>—— 但未定義完整參數 |
| 27 | PARTIAL 狀態的埋點需要帶 `missing_count` 嗎？ | PRD 未提及 PARTIAL 狀態的埋點細節 |
| 28 | 轉換失敗時，`convert_failed` 事件需要哪些參數？ | PRD 未定義失敗事件的參數 |
| 29 | 埋點的觸發時機是 API Response 還是 UI 渲染完成？ | PRD 未說明埋點觸發時機 |

---

## 🟢 低優先度問題（優化 / 未來考量）

### 📋 問 PM 的問題

| # | 問題 | PRD 敘述 |
|---|------|----------|
| 30 | 使用者在 Loading 時 App 進入背景，回來後如何處理？ | PRD 未提及背景處理 |
| 31 | Phase 2 (OCR2Code) 的非同步流程，Phase 1 需要預先設計架構嗎？ | PRD Phase 2 寫：「長時間執行的任務（OCR / Prompt）應加入佇列：產生 Request ID、狀態：`PENDING` → `PROCESSING` → `SUCCESS` / `FAILED` / `PARTIAL`、Frontend 可以輪詢或接收推播通知／App 內訊息」 |
| 32 | 目前只支援足球，未來擴展到其他運動時，UI 需要改動嗎？ | PRD 服務名稱為「**Sport** Booking Code Generator Service」，暗示可能擴展到其他運動 |
| 33 | Deep Link 支援計畫？使用者可以分享轉換結果嗎？ | PRD 未提及 Deep Link |
| 34 | PARTIAL 狀態允許下注，是否有 Compliance 風險需要提示使用者？ | PRD 寫：「轉換結果為 Success（或 **Partial，如果 Phase 1 將部分載入視為有效**）」—— 暗示需要 PM/Compliance 確認 |
| 35 | 競品 Booking Code 的使用是否有法律風險？需要加 Disclaimer 嗎？ | PRD 未提及法律風險 |

### 💻 問 BE 的問題

| # | 問題 | PRD 敘述 |
|---|------|----------|
| 36 | 相同的 Booking Code 重複轉換，是否會快取結果？ | PRD 未提及快取機制 |
| 37 | 是否有 Rate Limit？短時間內多次請求會被擋嗎？ | PRD 提及競品 API「`load_code` Endpoint 設定（URL、認證、**速率限制**等）」—— 但未說明 Fcom 自己的 Rate Limit |
| 38 | 預期的 API Response Time 是多少？需要設計進度條嗎？ | PRD 未提及預期 Response Time |
| 39 | 網路中斷時的 Retry 機制由 Client 還是 Backend 處理？ | PRD 寫：「逾時／內部錯誤：記錄以供監控和**重試選項**」—— 但未說明重試由誰負責 |
| 40 | 如果競品的賽事已結束，轉換會失敗還是跳過該選項（算 PARTIAL）？ | PRD 未提及賽事狀態處理 |
| 41 | 未來擴展到其他運動時，API 需要改動嗎？ | PRD 服務名稱為「Sport Booking Code Generator Service」，但未說明擴展計畫 |

---

## 📊 問題統計

| 優先度 | PM | BE | DA | 總計 |
|--------|----|----|----|----|
| 🔴 高 | 3 | 6 | - | 9 |
| 🟡 中 | 6 | 4 | 4 | 14 |
| 🟢 低 | 6 | 6 | - | 12 |
| **總計** | **15** | **16** | **4** | **35** |

---

## 📋 會議後待確認事項 Checklist

### BE 相關

- [ ] API Schema 文件（Request / Response 完整定義）
- [ ] Error Code enum 清單
- [ ] Bookie 清單資料來源確認
- [ ] `selections` 資料格式與現有 Betslip Model 相容性
- [ ] Timeout 數值確認

### PM 相關

- [ ] Figma 最終版本確認（各狀態 node-id）
- [ ] PARTIAL 狀態是否允許下注
- [ ] 自動跳轉 vs CTA 最終決議
- [ ] Compliance 風險評估
- [ ] Loading 狀態互動行為

### DA 相關

- [ ] 埋點規格文件
- [ ] Event 完整參數定義
- [ ] 觸發時機確認

---

## 📝 會議筆記區

### 🔴 高優先度 - PM 回覆

```
-
```

### 🔴 高優先度 - BE 回覆

```
-
```

### 🟡 中優先度 - PM 回覆

```
-
```

### 🟡 中優先度 - BE 回覆

```
-
```

### 🟢 低優先度 - 備註

```
-
```

### 其他決議

```
-
```
