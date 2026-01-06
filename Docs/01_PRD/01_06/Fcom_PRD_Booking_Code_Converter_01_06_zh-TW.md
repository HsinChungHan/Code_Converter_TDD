# Booking Code Converter

## 負責人

| 項目 | 內容 |
|------|------|
| **文件狀態** | DRAFT 1ST VERSION |
| **文件負責人** | @Dino Yeh |
| **UED** | @Ten Liu |
| **開發人員** | BE: @Gary Chen, @Danny Lin |
| | Android: @David Huang |
| | WAP: @Paul Yang |
| | iOS: @Reed Hsin |
| **QA** | 待定 |
| **DA** | @Richard Cheng |
| **Figma** | [Code-Converter](https://www.figma.com/design/SvcTlADMZ7gUPIa7nN2hT1/Code-Converter?node-id=24353-69) |
| **API 文件** | 待定 |
| **Epic Ticket** | [FOOTBALL-9161: Booking Code Converter](https://jira.example.com/browse/FOOTBALL-9161) `BACKLOG` |

---

## 版本歷史

| 日期 | 備註 |
|------|------|
| 2025-01-06 | 新增 GA Events 詳細參數、API Endpoints、Twitter Tag Bot 功能 |

---

## 環境

| 平台 | 地區 | 後台相關 |
|------|------|----------|
| BE | NG, GH | BO Page |
| WAP | | BO Config |
| FE for BO page | | |
| Android | | |
| iOS | | |

---

## 時程

| 系統設計 | 日期 |
|----------|------|
| BE: | |
| Android: | |
| WAP: | |
| iOS: | |

---

## 功能描述

> 讓使用者能夠輕鬆地將競品的 Booking Code 或投注截圖轉換為 Fcom 的 Booking Code，並直接在 Fcom 上投注。在後續階段，允許使用者透過自然語言提示生成投注組合。

### Phase 1 範圍：Code2Code

**競品 → Fcom Booking Code**

1. 使用者在 Fcom App（或透過 Telegram Bot）輸入競品的 Booking Code。
2. Backend 呼叫競品的公開「load code」API，取得投注組合（賽事、盤口、選項），將其對應到 Fcom 的盤口，並生成 Fcom Booking Code。
3. 生成的 Fcom Booking Code 會自動載入 Fcom Betslip。

### Phase 2 範圍：OCR2Code

**圖片 → Fcom Booking Code**

- 使用者將投注截圖（來自競品／社群媒體）分享到 Fcom App 或 Telegram Bot。
- Backend 使用 OCR + 解析來提取選項，對應到 Fcom 盤口，生成 Fcom Booking Code，並載入 Betslip（或在 Telegram 回覆）。

### Phase 3 範圍：Prompt2Code

**提示詞 → Fcom Booking Code**

- 使用者透過 Fcom App Widget 或 Telegram Bot 發送自然語言提示（例如：「幫我找 3 場今天開賽且勝率最高的比賽」）。
- Backend 使用 AI 解析提示，從 Fcom 資料庫取得合適的選項，建立 Booking Code 並回傳。

### 平台

- Android / iOS / WAP
- Telegram Bot（既有）
- 共用 Backend 服務：**Booking Code Generator**

### 核心價值

- 降低從其他博彩公司遷移或複製社群媒體投注單的使用者的摩擦。
- 將外部／社群投注流量導入 Fcom。
- 使用現有的 Data + AI 提供「智慧投注建議」（Phase 2）。

---

## User Story

| 故事名稱 | 作為... | 我想要... | 以便... |
|----------|---------|-----------|---------|
| **Code2Code**（Fcom App 內） | 看到其他博彩公司有趣投注的使用者 | 將競品的 Booking Code 貼到 Fcom | 我可以快速在 Fcom 下同樣的注，無需手動重建 |
| **OCR2Code**（Fcom App – 分享圖片） | 瀏覽社群媒體／聊天群組的使用者 | 直接將投注截圖分享到 Fcom | Fcom 可以讀取、轉換，讓我輕鬆投注相同的組合 |
| **OCR2Code**（Telegram Bot） | 比起 App 更常使用 Telegram 的使用者 | 將投注截圖轉發給 Fcom Telegram Bot | 它可以將其轉換為我可以重複使用的 Fcom Booking Code 或選項 |
| **Prompt2Code**（Phase 2） | 沒有特定投注碼但有想法的使用者 | 輸入簡單的請求（例如：「今天 3 場穩的，勝率最高」） | Fcom 可以根據我的偏好生成 Booking Code |
| **非同步／長時間流程** | 使用者 | 在系統轉換我的圖片或提示時能夠離開畫面 | 我不會被長時間的 AI/OCR 處理阻擋，可以繼續使用 App |

---

## 錯誤處理

| 錯誤類型 | 訊息 |
|----------|------|
| **無效的競品投注碼** | 「我們在 [BookieName] 找不到此 Booking Code。請檢查後重試。」 |
| **OCR 無法解析圖片** | 「我們無法從此圖片識別有效的投注。請嘗試其他截圖或更清晰的圖片。」 |
| **部分對應** | 「我們轉換了部分選項，但有些在 Fcom 上不可用。」<br> *如果可能，顯示缺失的賽事／盤口清單。* |
| **逾時／內部錯誤** | 「轉換時間比預期長。請稍後再試。」<br> *記錄以供監控和重試選項。* |

---

## 詳細規格 (SPEC)

### 架構 / 元件

#### Frontend

- Fcom App **「Load Code」Widget**
- 聊天式介面（用於非同步流程和歷史記錄）
- 系統層級分享入口（Android/iOS）
- Telegram Bot（既有，重用相同 Backend）

#### Backend

**Sport Booking Code Generator Service**

**輸入類型：**
- `type = COMPETITOR_CODE`（原始文字碼 + 來源博彩公司）
- `type = IMAGE`（圖片 URL 或檔案參照）
- `type = PROMPT`（自由文字，後續階段）

**職責：**

1. 解析輸入（投注碼／圖片／提示）。
2. 正規化為內部選項結構：
   - 賽事 ID / 名稱
   - 盤口 ID / 名稱
   - 選項 ID / 名稱
   - 賠率（如果需要用於對應／驗證）
3. 將外部選項對應到 Fcom 盤口（資料庫查詢 + 對應規則）。
4. 建立 Fcom Booking Code。
5. 回傳：
   - Booking Code
   - 正規化選項清單
   - 錯誤／部分匹配資訊（如有）

#### Competitor API Clients

針對每個支援的競品：
- `load_code` Endpoint 設定（URL、認證、速率限制等）
- Response 對應到內部 Schema

#### Mapping Layer

競品賽事／盤口／選項與 Fcom 內部 ID 之間的對應邏輯：
- 依賽事日期時間 + 隊伍名稱 + 聯賽
- 依盤口類型名稱／代碼
- 依選項標籤（例如：「主勝」、「大於 2.5」）

#### AI / OCR Layer

接收圖片並提取：
- 博彩公司名稱（如果可能）
- 賽事／隊伍／盤口／賠率清單

回傳機器可讀的結構給 Mapping Layer。

#### Job / 非同步處理

長時間執行的任務（OCR / Prompt）應加入佇列：
- 產生 Request ID
- 狀態：`PENDING` → `PROCESSING` → `SUCCESS` / `FAILED` / `PARTIAL`
- Frontend 可以輪詢或接收推播通知／App 內訊息。

---

## 流程

### 1. Code2Code – App 內（文字輸入）

**輸入：**
- 使用者在 Load Code Widget 手動輸入競品 Booking Code。
- 使用者從下拉選單選擇競品博彩公司（例如：Bet9ja、BetKing 等）。

**流程：**

| 步驟 | 描述 |
|------|------|
| 1 | 使用者在首頁開啟 Load Code Widget。 |
| 2 | 使用者從下拉選單選擇 Bookie。 |
| 3 | 使用者輸入 Booking Code 文字並點擊 **Load Code**。 |
| 4 | App 發送請求到 Booking Code Generator。 |
| 5 | Backend 呼叫競品的 `load_code` API，取得選項。 |
| 6 | Backend 透過資料庫／Mapping Layer 將這些選項對應到 Fcom 盤口。 |
| 7 | Backend 生成 Fcom Booking Code（例如：AF1234）並回傳 Response。 |
| 8 | App：<br> • 顯示成功訊息：「已轉換為 Fcom 投注碼 AF1234」<br> • 自動開啟 Betslip 並載入選項。 |

**錯誤情境：**

| 情境 | UI 訊息 |
|------|---------|
| 無效的競品投注碼 / API 回傳「找不到」 | 「在 [BookieName] 找不到此投注碼。請檢查後重試。」 |
| 僅部分對應（部分賽事在 Fcom 不可用） | 「我們只能轉換 5 個選項中的 3 個。缺失的賽事：…」 |
| 競品 API 當機 / 逾時 | 監控 @Gary Chen |

**Mockup 參考：**
1. 首頁 Load Code Widget
2. 空的 Mini Betslip（a. 優化空的 Betslip）
3. Code Center Load Code 頁籤

---

### 1.5 Twitter Tag Bot（新增功能）

**流程：**

| 步驟 | 描述 |
|------|------|
| 1 | 使用者在 Twitter 上 Tag Fcom 官方帳號。 |
| 2 | 官方帳號收到通知，透過貼文 ID 找到該 Twitter 貼文。 |
| 3 | 系統轉換投注碼。 |
| 4 | 在該貼文下方以留言方式回覆轉換結果。 |

---

### 2. OCR2Code – App 內（分享圖片）

**輸入：**
- 使用者在截圖上點擊系統分享。
- 從分享選項中選擇 Fcom App。

**流程：**

| 步驟 | 描述 |
|------|------|
| 1 | 使用者在社群／聊天中看到投注截圖 → 點擊分享。 |
| 2 | 在系統分享表單中，使用者選擇 Fcom。 |
| 3 | Fcom App 開啟「Code Converter」聊天 UI（或專用畫面）顯示：<br> • 分享的圖片 <br> • 訊息「我們正在將您的截圖轉換為 Booking Code…」 |
| 4 | App 發送請求到 Backend。 |
| 5 | Backend 將任務推送到 OCR/AI 佇列：<br> a. OCR 提取文字 → 賽事／盤口／賠率。<br> b. Mapping Layer 將其對應到 Fcom 盤口。<br> c. 生成 Booking Code。 |
| 6 | 完成後，Backend 發送結果：<br> • `SUCCESS`：Fcom Booking Code + 選項清單 <br> • `PARTIAL`：部分選項缺失 <br> • `FAILED`：無法解析／無匹配 |
| 7 | App：在聊天 UI 中顯示訊息：<br> 「這是您轉換後的投注碼：AF1234。點擊投注。」<br> 當使用者點擊時，開啟 Betslip 並載入選項。 |

**備註：**
- 使用者應該能夠離開畫面，繼續其他操作。
- 當結果準備好時：通知／App 內訊息
- 聊天歷史保留輸入圖片 + 輸出投注碼

---

### 3. OCR2Code – Telegram Bot

**流程：**

| 步驟 | 描述 |
|------|------|
| 1 | 使用者轉發或上傳投注截圖到 Fcom Telegram Bot。 |
| 2 | Bot 接收圖片並發送到 Backend。 |
| 3 | Backend 執行相同的 OCR + Mapping + Booking Code 生成器。 |
| 4 | Bot 在聊天中回覆：<br> **成功時：**「轉換後的 Booking Code：AF1234」（可選列出選項）<br> **部分／失敗時：** 說明出了什麼問題。 |

---

### 4. Prompt2Code – App Widget 或 Telegram（Phase 2）

**流程：**

| 步驟 | 描述 |
|------|------|
| 1 | 使用者開啟 Code Converter 聊天（App）或 Telegram Bot 並輸入提示，例如：<br> 「找 3 場今天開賽且勝率最高的比賽。」 |
| 2 | Client 發送請求。 |
| 3 | Backend：<br> a. 使用 AI 模型解析意圖和限制（賽事數量：3、日期：今天、條件：最高勝率）<br> b. 查詢 Fcom 資料庫／推薦引擎以取得合適的選項。<br> c. 建立 Booking Code。 |
| 4 | 回傳結果 → Booking Code + 說明。 |
| 5 | UI 顯示：「這是根據您請求的投注碼：AF5678」<br> 列出賽事和盤口。 |

---

## 使用案例

### 支援的 Bookies

| 排名 | Bookies | 國家 | 負責人 |
|------|---------|------|--------|
| 1 | Sporty | NG, GH | |
| 2 | MSport | NG/GH/UG/ZM | @Danny Lin |
| 3 | Bet9Ja | NG | @Gary Chen |
| 4 | Bangbet | KE, UG, NG, GH, TZ | @Danny Lin |
| 5 | BetKing | NG | @Gary Chen |
| 6 | 1xBet | Global | |
| 7 | Betway | Global | |
| 8 | LiveScore Bet | UK | |
| 9 | Stack | Global | |
| 10 | BetPawa | Africa | |
| 11 | Bet365 | Global | |

### 使用案例情境

1. **App 內文字投注碼轉換**
   - 使用者在競品網站看到 Booking Code。
   - 開啟 Fcom App → Load Code Widget → 選擇競品 → 輸入投注碼 → 點擊 Load → Fcom 轉換並載入 Betslip。

2. **App 內圖片分享轉換**
   - 使用者在 Instagram / WhatsApp 看到投注截圖。
   - 點擊分享 → 選擇 Fcom → App 開啟聊天視圖並上傳圖片 → 系統轉換 → 回傳 Fcom Booking Code → 使用者點擊投注。

3. **Telegram 截圖轉換**
   - 使用者將投注截圖轉發給 Fcom Telegram Bot。
   - Bot 回覆 Fcom Booking Code 和選項清單。

4. **基於提示的 Booking Code（Phase 2）**
   - 使用者在 Fcom App 開啟 Code Converter 聊天。
   - 輸入：「今天 3 場比賽，最高勝率，總賠率約 3.0。」
   - 系統根據匹配條件從資料庫回傳 Booking Code。

---

## API Endpoints

| 頁面 | API Endpoint | 備註 |
|------|--------------|------|
| Home Page | `POST /orders/converter/code` (New) | 轉換 Code2Code |
| Home Page | `GET /orders/converter/config/providerCountries` (New) | 取得 provider country 設定 |
| Home Page | `GET /orders/share/:shareCode` | 透過 share code 取得 order 記錄 |

---

## BO 頁面設計

*待定*

---

## 文案

*待定*

---

## GA Events

### 事件定義

| Event 名稱 | 觸發時機 | 參數 |
|------------|----------|------|
| `code_converter__open_bookie_spinner` | 開啟 bookie 選擇器 | `location`: widget / empty_betslip / code_center |
| `code_converter__choose_bookies` | 點擊送出 CTA | `bookie`, `country`, `location` |
| `code_converter__load_code` | 點擊 Load Code CTA | `bookie`, `country`, `location` |
| `code_converter__load_code_successfully` | API 回傳成功 response | `bookie`, `country`, `location` |

### 參數說明

**location 可能值：**
- `widget` - 首頁 Widget
- `empty_betslip` - 空的 Betslip
- `code_center` - Code Center 頁籤

---

## 後續追蹤

| 任務 | 負責人 | 狀態 | 行動項目 |
|------|--------|------|----------|
| Code2Code BE | @Gary Chen, @Danny Lin | IN PROGRESS | • 整合 bookies<br>• 對應 events/markets & outcomes<br>• 完成投注碼轉換機制 |
| Code2Code Client tech | | | Load code component 擴展 |

---

## 指標

### North Star Metric（Phase 1）：Converter-attributed Betslip Loads

**定義：**
成功轉換競品投注碼並將結果選項載入 Betslip 的 Session／使用者數量。

**納入條件（歸因）：**
- 轉換結果為 **Success**（或 **Partial**，如果 Phase 1 將部分載入視為有效）且 Betslip 已載入。
- Betslip 載入事件必須帶有：
  - `source = "code_converter"`
  - 唯一的 `conversion_request_id`（或等效的任務／請求識別碼）以確保端到端的可追溯性。

**備註：**
- 此指標專注於 Phase 1 的核心價值：透過將外部投注碼轉換為 Fcom 上可操作的 Betslip 來減少摩擦。
- 不要求在 Betslip 載入後進行投注。

---

## DA 需求

### 監控互動

**3 個入口（widget / empty betslip / code center load code tab）**

觀察漏斗：
1. Bookies spinner
2. 選擇 bookies
3. 輸入 booking code
4. Load code

### 轉換成功率

1. 追蹤轉換量和各 bookie 的轉換成功率（分別計算）
   - 轉換成功率應明確包含並追蹤部分結果
2. 目標是識別最受歡迎的第三方 bookies，並提高這些 bookies 的轉換成功率
3. 比較 Fcom / Sporty 投注碼與其他 bookies 投注碼的比例

### BE Tables

轉換的 booking codes 資料：
- Bookie
- 總選項數量
- 成功選項數量
- *待定：失敗的選項將如何儲存在資料庫中？我們有關於失敗選項的哪些資訊？*

---

## 設計資源與靈感

### 首頁 – Load Code Widget（既有）

**Case 1（文字輸入）：**
- Bookie 下拉選單（競品對應所必需）
- 投注碼文字欄位
- 「Load Code」CTA

**Case 3（提示）（Phase 2）：**
- 額外模式／切換：「請 AI 建立投注碼」
- 開啟聊天視圖或展開為提示輸入。

### 聊天式介面（OCR 和 Prompt 建議使用）

**優點：**
- 自然處理慢速 AI / OCR（非同步）。
- 清晰的歷史記錄：使用者可以看到之前的圖片／請求和結果。
- 易於擴展到未來功能（例如：說明／提示）。

### 通知

如果處理時間超過 X 秒，顯示：
> 「我們仍在處理中，您可以繼續使用 App。準備好時我們會通知您。」

---

## 其他

### 其他產品設計參考

*競品設計參考以獲取靈感。*

---

## 名詞解釋

### 投注相關術語

| 術語 | 英文 | 說明 |
|------|------|------|
| **投注碼** | Booking Code | 由博彩公司生成的唯一代碼，代表一組預選的投注選項。使用者可透過此代碼快速載入投注組合，無需手動逐一選擇。 |
| **投注單** | Betslip | 使用者在博彩平台上選擇的所有投注項目的集合，類似於購物車。使用者在此確認選項、輸入金額並提交投注。 |
| **盤口** | Market | 針對某一賽事提供的投注類型，例如：勝負盤（1X2）、大小球（Over/Under）、讓分盤（Handicap）等。 |
| **賽事** | Event | 可供投注的比賽或活動，例如：曼聯 vs 利物浦的英超比賽。 |
| **選項** | Selection / Outcome | 盤口中可選擇的具體投注結果，例如：在「大小球 2.5」盤口中，「大於 2.5」或「小於 2.5」即為選項。 |
| **賠率** | Odds | 表示投注回報的數值。例如賠率 2.50 表示投注 1 元可獲得 2.50 元（含本金）。 |
| **博彩公司** | Bookie / Bookmaker | 提供投注服務的公司，例如：Bet9ja、BetKing、1xBet 等。 |
| **競品** | Competitor | 指 Fcom 以外的其他博彩公司。 |

### 技術相關術語

| 術語 | 英文 | 說明 |
|------|------|------|
| **光學字元辨識** | OCR (Optical Character Recognition) | 從圖片中識別並提取文字的技術，用於解析投注截圖。 |
| **對應層** | Mapping Layer | 負責將競品的賽事、盤口、選項對應到 Fcom 內部資料的邏輯模組。 |
| **非同步處理** | Async Processing | 任務在背景執行，使用者無需等待即可繼續操作，任務完成後會收到通知。 |
| **佇列** | Queue | 待處理任務的排隊機制，確保系統依序處理請求。 |

### 狀態相關術語

| 術語 | 英文 | 說明 |
|------|------|------|
| **成功** | SUCCESS | 所有選項皆成功轉換並對應到 Fcom 盤口。 |
| **部分成功** | PARTIAL | 部分選項成功轉換，但有些選項在 Fcom 上不可用或無法對應。 |
| **失敗** | FAILED | 轉換失敗，可能原因包括：投注碼無效、圖片無法解析、系統錯誤等。 |

### 平台相關術語

| 術語 | 英文 | 說明 |
|------|------|------|
| **Fcom** | Fcom (Football.com) | 本產品所屬的博彩平台。 |
| **WAP** | WAP (Mobile Web) | 行動網頁版本，透過手機瀏覽器存取。 |
| **BO** | Back Office | 後台管理系統，供內部人員進行設定和管理。 |

