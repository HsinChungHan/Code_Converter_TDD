# Phase 1 - Code2Code Sequence Diagram (Basic)

> **版本**：1 - 基礎版（Business Logic + API + App State）  
> **來源**：PRD (2025-01-06 版本) + API Doc  
> **範圍**：Phase 1 - Competitor Code → Fcom Booking Code  
> **更新**：2025-01-06 - 修正轉換成功後的完整流程

---

## App 角色拆分說明

| 角色 | 說明 | 拆分依據 |
|------|------|----------|
| **Load Code Widget** | 主要輸入元件，負責 Bookie 選擇、Code 輸入、狀態顯示 | PRD 定義的「Load Code Widget」元件 |
| **Bookie Selector Sheet** | Bottom Sheet 選擇器，負責 Provider 和 Country 選擇 | PRD 流程中的「選擇 Bookie」步驟為獨立互動 |
| **Betslip** | 投注單，負責載入轉換後的 selections | PRD 定義的結果顯示終點，獨立的功能模組 |

**拆分理由**：
1. **PRD 流程定義**：PRD 明確描述了 Widget → Bottom Sheet → Betslip 的互動流程
2. **功能職責分離**：每個元件有明確的單一職責
3. **狀態獨立性**：各元件有獨立的 UI 狀態（Widget: Default/Focus/Loading/Error, Betslip: 載入 selections）

---

## 主流程：Code2Code 轉換

```mermaid
sequenceDiagram
    actor User
    
    box rgb(173, 216, 230) App
        participant Widget as Load Code Widget
        participant Selector as Bookie Selector Sheet
        participant Betslip as Betslip
    end
    
    participant BE as Backend

    %% 1. 初始化階段
    rect rgb(240, 248, 255)
        note over User,Widget: 1. 初始化階段
        User->>Widget: 開啟首頁
        Widget->>User: 顯示 Widget (Default 狀態)
    end

    %% 2. 選擇 Bookie (含 Config API)
    rect rgb(255, 250, 240)
        note over User,Selector: 2. 選擇 Bookie
        User->>Widget: 點擊 Bookie Dropdown
        Widget->>BE: GET /orders/converter/config/providerCountries
        
        alt Config API Success
            BE-->>Widget: {bizCode: 10000, data: [{provider, name, countries}...]}
            Widget->>Selector: 開啟 Bottom Sheet (顯示 Provider 列表)
            
            alt ALL 國家 Provider (如 Fcom)
                User->>Selector: 選擇 Provider
                note over Selector: Country 預設為 ALL，無需選擇
            else 單一國家 Provider (如 Bet9ja)
                User->>Selector: 選擇 Provider
                note over Selector: Country 自動選定，無需選擇
            else 多國家 Provider (如 MSport)
                User->>Selector: 選擇 Provider
                Selector->>User: 顯示 Country 列表
                User->>Selector: 選擇 Country
            end
            
            User->>Selector: 點擊 Submit 按鈕
            Selector-->>Widget: 關閉 Sheet + 回傳 {provider, country}
            Widget->>User: 更新顯示已選 Provider
        
        else Config API Failure
            BE-->>Widget: error response
            Widget->>User: 顯示 "Config Load Failed" 錯誤 (Stop)
        end
    end

    %% 3. 輸入 Booking Code
    rect rgb(240, 255, 240)
        note over User,Widget: 3. 輸入 Booking Code
        User->>Widget: 點擊輸入框
        Widget->>User: 顯示 Focus 狀態
        User->>Widget: 輸入 Booking Code
        Widget->>User: 顯示 Filled 狀態 (Load 按鈕啟用)
    end

    %% 4. 轉換流程
    rect rgb(255, 245, 238)
        note over User,BE: 4. 轉換流程
        User->>Widget: 點擊 Load 按鈕
        Widget->>User: 顯示 Loading 狀態
        
        Widget->>BE: POST /orders/converter/code
        note over Widget,BE: Request: {provider, country, bookingCode}
        
        alt Convert API Success
            BE-->>Widget: {bizCode: 10000, data: {shareCode, successCnt, failCnt}}
            note over Widget: 記錄 failCnt 用於後續 Toast 顯示
            
            %% 5. Check Liabilities [既有流程]
            note over Widget,BE: 5. Check Liabilities [既有流程]
            Widget->>BE: GET /bookingCode/[shareCode]/liabilities
            
            alt Liabilities API Success
                BE-->>Widget: {isTrusted: true/false}
                
                %% 6. Get Betslip Data [既有流程]
                note over Widget,BE: 6. Get Betslip Data [既有流程]
                Widget->>BE: GET /orders/share/[shareCode]
                
                alt Share API Success
                    BE-->>Widget: {betslipData: selections}
                    
                    %% 7. 彈出 Betslip 並且顯示轉換結果
                    note over Widget,Betslip: 7. 彈出 Betslip 並且顯示轉換結果
                    Widget->>Betslip: Pop up Betslip (載入 selections)
                    Betslip->>User: 顯示 Betslip
                    
                    opt failCnt > 0 (部分轉換失敗)
                        Betslip->>User: 顯示 Toast "⚠ X selections failed to convert"
                    end
                    
                else Share API Failure
                    BE-->>Widget: error response
                    Widget->>User: 按照 Betslip 既有流程顯示錯誤 UI (Stop)
                end
                
            else Liabilities API Failure
                BE-->>Widget: error response
                Widget->>User: 按照 Betslip 既有流程顯示錯誤 UI (Stop)
            end
            
        else Convert API Error
            BE-->>Widget: error response
            Widget->>User: 顯示 Error 狀態 (Stop)
        end
    end
```

---

## 完整流程圖

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Code2Code 轉換流程                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. GET /config/providerCountries                                        │
│     ├─ Success → 顯示 Bookie Selector Sheet                              │
│     └─ Failure → "Config Load Failed" (Stop)                             │
│                                                                          │
│  2. User 選擇 Provider + Country → 點擊 Submit → 關閉 Sheet              │
│                                                                          │
│  3. User 輸入 Booking Code                                               │
│                                                                          │
│  4. POST /orders/converter/code                                          │
│     ├─ Success → 取得 {shareCode, successCnt, failCnt}                   │
│     │                                                                    │
│     │   5. GET /bookingCode/[shareCode]/liabilities [既有流程]           │
│     │      ├─ Success → 取得 {isTrusted}                                 │
│     │      │                                                             │
│     │      │   6. GET /orders/share/[shareCode] [既有流程]               │
│     │      │      ├─ Success → 取得 {betslipData}                        │
│     │      │      │                                                      │
│     │      │      │   7. Pop up Betslip                                  │
│     │      │      │      ├─ 顯示 selections                              │
│     │      │      │      └─ 若 failCnt > 0 → Toast 提示失敗數量          │
│     │      │      │                                                      │
│     │      │      └─ Failure → Betslip 既有錯誤 UI (Stop)                │
│     │      │                                                             │
│     │      └─ Failure → Betslip 既有錯誤 UI (Stop)                       │
│     │                                                                    │
│     └─ Failure → Error 狀態 (Stop)                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## App 狀態變化

| 階段 | Widget 狀態 | 說明 |
|------|-------------|------|
| 初始化 | Default | 預設顯示，等待使用者操作 |
| 點擊輸入框 | Focus | 輸入框聚焦，準備輸入 |
| 輸入中 | Typing | 顯示清除按鈕 |
| 輸入完成 | Filled | Load 按鈕啟用 |
| 轉換中 | Loading | 顯示載入動畫和提示文字 |
| 轉換失敗 | Error | 顯示錯誤訊息，可重試 |
| 轉換成功 | → Betslip | Pop up Betslip |

---

## API 調用順序

| 順序 | API | Method | 用途 | 失敗處理 |
|:----:|-----|--------|------|----------|
| 1 | `/orders/converter/config/providerCountries` | `GET` | 取得 Provider 和 Country 列表 | "Config Load Failed" |
| 2 | `/orders/converter/code` | `POST` | 執行 Code 轉換 | Error 狀態 |
| 3 | `/bookingCode/[shareCode]/liabilities` | `GET` | 檢查 Liabilities [既有流程] | Betslip 既有錯誤 UI |
| 4 | `/orders/share/[shareCode]` | `GET` | 取得 Betslip 資料 [既有流程] | Betslip 既有錯誤 UI |

---

## Response 使用方式

### 1. GET /orders/converter/config/providerCountries

```json
{
  "bizCode": 10000,
  "data": [
    { "provider": "bet9ja", "name": "Bet9ja", "countries": ["NG"] },
    { "provider": "msport", "name": "MSport", "countries": ["NG", "GH", "UG", "ZM"] }
  ]
}
```

**使用方式**：
- `data` 陣列 → 渲染 Bookie Selector Sheet 列表
- `countries == ["ALL"]` → Country 預設為 ALL，無需選擇
- `countries.length == 1` → 自動選定國家，無需選擇
- `countries.length > 1` → 顯示 Country 子選單供選擇

### 2. POST /orders/converter/code

```json
{
  "bizCode": 10000,
  "data": {
    "shareCode": "ABC123",
    "successCnt": 5,
    "failCnt": 1
  }
}
```

**使用方式**：
- `shareCode` → 用於後續 API 調用
- `failCnt` → 記錄，在 Betslip 顯示時用於 Toast 提示

### 3. GET /bookingCode/[shareCode]/liabilities [既有流程]

```json
{
  "isTrusted": true
}
```

**使用方式**：
- 驗證 shareCode 的有效性

### 4. GET /orders/share/[shareCode] [既有流程]

```json
{
  "betslipData": {
    "selections": [...]
  }
}
```

**使用方式**：
- `betslipData` → 用於渲染 Betslip 內容

---

## Toast 顯示邏輯

| 條件 | 顯示 |
|------|------|
| `failCnt == 0` | 無 Toast |
| `failCnt > 0` | "⚠ {failCnt} selections failed to convert" |

---

## 備註

- 📍 **PRD 來源**：`../01_PRD/01_06/Fcom_PRD_Booking_Code_Converter_01_06_zh-TW.md`
- 📍 **API 文件**：`../API_Doc/Code_Converter_API_Doc.md`
