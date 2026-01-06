# Code2Code 完整整合流程

## Flow 資訊

| 欄位 | 值 |
|------|-----|
| **feature** | CodeConverter |
| **flow_id** | CC-ISSD-001 |
| **flow_type** | Full |
| **flow_name** | Code2Code 完整整合流程 |

---

## 流程說明

| 階段 | 說明 |
|------|------|
| **1. 初始化階段** | 1. Widget 顯示預設狀態<br>2. 使用者點擊 Bookie Dropdown<br>3. 系統取得 Provider Config |
| **2. 選擇 Bookie** | 1. 開啟 Bookie Selector Sheet<br>2. 選擇 Provider 和 Country<br>3. 關閉 Sheet 並更新 Widget |
| **3. 輸入 Booking Code** | 1. Focus 輸入框<br>2. 輸入 Booking Code<br>3. 啟用 Load 按鈕 |
| **4. 轉換流程** | 1. 呼叫 Convert API<br>2. 檢查 Liabilities<br>3. 取得 Betslip Data<br>4. 載入 Betslip |

---

## 整合序列圖

```mermaid
sequenceDiagram
    actor User
    
    box rgb(207,232,255) UI Layer
        participant Widget as LoadCodeWidget
        participant Sheet as BookieSelectorSheet
        participant Betslip as Betslip
    end
    
    box rgb(255,250,205) Domain Layer
        participant Feature as LoadCodeWidgetFeature
        participant ConvertUC as ConvertBookingCodeUseCase
        participant ConfigUC as LoadProviderConfigUseCase
    end
    
    box rgb(240,240,240) Data and Infrastructure Layer
        participant Repo as CodeConverterRepository
        participant Client as CodeConverterClient
        participant API as CodeConverterAPI
        participant BetslipRepo as BetslipRepository
        participant BetslipClient as BetslipClient
        participant BetslipAPI as BetslipAPI
    end

    Note over User,Widget: 使用者進入首頁或 Code Center

    %% 1. 初始化 - 取得 Provider Config
    User->>Widget: 點擊 Bookie Dropdown
    Widget->>Feature: .bookieDropdownTapped
    Feature->>ConfigUC: execute()
    ConfigUC->>Repo: getProviderCountryConfig()
    Repo->>Client: fetchProviderCountries()
    Client->>API: GET /orders/converter/config/providerCountries
    API-->>Client: ProviderCountryConfigDTO
    Client-->>Repo: ProviderCountryConfigDTO
    Repo-->>ConfigUC: [ProviderConfig]
    ConfigUC-->>Feature: LoadProviderConfigOutput
    Feature->>Widget: 更新 State
    Widget->>Sheet: 開啟 Bottom Sheet
    
    %% 2. 選擇 Bookie
    Note over User,Sheet: 使用者選擇 Bookie 和 Country
    User->>Sheet: 選擇 Provider
    
    alt 單一國家 Provider
        Note over Sheet: Country 自動選定
    else 多國家 Provider
        Sheet->>User: 顯示 Country 列表
        User->>Sheet: 選擇 Country
    end
    
    User->>Sheet: 點擊 Submit
    Sheet-->>Widget: {provider, country}
    Widget->>Feature: .bookieSelected(provider, country)
    Feature->>Widget: 更新顯示已選 Provider
    
    %% 3. 輸入 Booking Code
    User->>Widget: 點擊輸入框
    Widget->>Feature: .inputFocused
    Feature->>Widget: 更新為 Focus 狀態
    User->>Widget: 輸入 Booking Code
    Widget->>Feature: .bookingCodeChanged(code)
    Feature->>Widget: 更新為 Typing/Filled 狀態
    
    %% 4. 轉換流程
    User->>Widget: 點擊 Load 按鈕
    Widget->>Feature: .loadButtonTapped
    Feature->>Widget: 更新為 Loading 狀態
    Feature->>ConvertUC: execute(provider, country, bookingCode)
    
    ConvertUC->>Repo: convertCode(provider, country, bookingCode)
    Repo->>Client: convertCode(request)
    Client->>API: POST /orders/converter/code
    
    alt Convert API Success
        API-->>Client: Code2CodeVO {shareCode, successCnt, failCnt}
        Client-->>Repo: Code2CodeVO
        Repo-->>ConvertUC: ConvertResult
        
        %% 5. Check Liabilities (既有流程)
        Note over ConvertUC,BetslipAPI: Check Liabilities 既有流程
        ConvertUC->>BetslipRepo: checkLiabilities(shareCode)
        BetslipRepo->>BetslipClient: getLiabilities(shareCode)
        BetslipClient->>BetslipAPI: GET /bookingCode/{shareCode}/liabilities
        BetslipAPI-->>BetslipClient: LiabilitiesDTO
        BetslipClient-->>BetslipRepo: LiabilitiesDTO
        BetslipRepo-->>ConvertUC: Liabilities
        
        %% 6. Get Betslip Data (既有流程)
        Note over ConvertUC,BetslipAPI: Get Betslip Data 既有流程
        ConvertUC->>BetslipRepo: getBetslipData(shareCode)
        BetslipRepo->>BetslipClient: getShareOrder(shareCode)
        BetslipClient->>BetslipAPI: GET /orders/share/{shareCode}
        BetslipAPI-->>BetslipClient: BetslipDataDTO
        BetslipClient-->>BetslipRepo: BetslipDataDTO
        BetslipRepo-->>ConvertUC: BetslipData
        
        ConvertUC-->>Feature: ConvertBookingCodeOutput
        Feature->>Betslip: 載入 selections
        Betslip->>User: 顯示 Betslip
        
        opt failCnt > 0
            Note over Betslip: 部分轉換失敗
            Betslip->>User: 顯示 Toast X selections failed to convert
        end
        
    else Convert API Error
        API-->>Client: error response
        Client-->>Repo: error
        Repo-->>ConvertUC: error
        ConvertUC-->>Feature: error
        Feature->>Widget: 更新為 Error 狀態
        Widget->>User: 顯示錯誤訊息
    end
```

---

## API 調用順序

| 順序 | API | Method | 說明 |
|:----:|-----|--------|------|
| 1 | `/orders/converter/config/providerCountries` | `GET` | 取得 Provider Country 設定 |
| 2 | `/orders/converter/code` | `POST` | 轉換 Booking Code |
| 3 | `/bookingCode/{shareCode}/liabilities` | `GET` | 檢查 Liabilities（既有） |
| 4 | `/orders/share/{shareCode}` | `GET` | 取得 Betslip Data（既有） |

