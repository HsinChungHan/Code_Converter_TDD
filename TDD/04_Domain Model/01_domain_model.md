# Domain Model

## 模型總覽

```
┌─────────────────────────────────────────────────────────────────┐
│                         Domain Models                           │
├─────────────────────────────────────────────────────────────────┤
│  ProviderConfig        Provider 設定（來自 API）                 │
│  SelectedBookie        已選擇的 Bookie（UI State）              │
│  ConvertResult         轉換結果（來自 API）                      │
│  WidgetInputState      Widget 輸入狀態（6 種狀態）               │
│  CountryCode           國家代碼（Value Object）                  │
├─────────────────────────────────────────────────────────────────┤
│                     既有復用的 Models                            │
├─────────────────────────────────────────────────────────────────┤
│  Region                現有國家/地區 enum                        │
│  LoadCodeModel.CodeResult  現有載入結果                          │
│  EventDetailOutcomeElement 現有選項元素                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 新增的 Domain Models

### ProviderConfig

對應 API: `GET /orders/converter/config/providerCountries`

```swift
/// Provider 設定（來自 API）
struct ProviderConfig: Equatable, Identifiable {
    let id: String  // 使用 provider 作為 id
    let provider: String
    let name: String
    let countries: [CountryCode]
    
    /// 轉換為 Region 列表（向後相容用）
    var regions: [Region] {
        countries.compactMap { Region.from(countryCode: $0) }
    }
    
    /// 是否只有單一國家
    var isSingleCountry: Bool {
        countries.count == 1
    }
}
```

### CountryCode

```swift
/// 國家代碼 Value Object
enum CountryCode: String, Equatable, CaseIterable {
    case nigeria = "NG"
    case ghana = "GH"
    case kenya = "KE"
    case tanzania = "TZ"
    case uganda = "UG"
    case zambia = "ZM"
    case ethiopia = "ET"
    case cameroon = "CM"
    case senegal = "SN"
    case ivoryCoast = "CI"
    
    /// 國家名稱（顯示用）
    var displayName: String {
        switch self {
        case .nigeria: return "Nigeria"
        case .ghana: return "Ghana"
        case .kenya: return "Kenya"
        case .tanzania: return "Tanzania"
        case .uganda: return "Uganda"
        case .zambia: return "Zambia"
        case .ethiopia: return "Ethiopia"
        case .cameroon: return "Cameroon"
        case .senegal: return "Senegal"
        case .ivoryCoast: return "Ivory Coast"
        }
    }
    
    /// 國旗 Emoji（可選）
    var flag: String {
        switch self {
        case .nigeria: return "🇳🇬"
        case .ghana: return "🇬🇭"
        case .kenya: return "🇰🇪"
        case .tanzania: return "🇹🇿"
        case .uganda: return "🇺🇬"
        case .zambia: return "🇿🇲"
        case .ethiopia: return "🇪🇹"
        case .cameroon: return "🇨🇲"
        case .senegal: return "🇸🇳"
        case .ivoryCoast: return "🇨🇮"
        }
    }
}
```

### SelectedBookie

```swift
/// 已選擇的 Bookie（UI State 用）
struct SelectedBookie: Equatable {
    let provider: String    // e.g. "bet9ja"
    let name: String        // e.g. "Bet9ja"
    let country: CountryCode
    
    /// 顯示文字（用於 Dropdown）
    var displayText: String {
        "\(name) \(country.rawValue)"  // e.g. "Bet9ja NG"
    }
    
    /// 短顯示（名稱太長時用）
    var shortDisplayText: String {
        let maxLength = 12
        if name.count > maxLength {
            return "\(name.prefix(maxLength))… \(country.rawValue)"
        }
        return displayText
    }
    
    /// 從 ProviderConfig + CountryCode 建立
    init(provider: String, name: String, country: CountryCode) {
        self.provider = provider
        self.name = name
        self.country = country
    }
    
    /// 從 ProviderConfig 建立（使用第一個國家）
    init?(from config: ProviderConfig) {
        guard let firstCountry = config.countries.first else { return nil }
        self.provider = config.provider
        self.name = config.name
        self.country = firstCountry
    }
}
```

### WidgetInputState

對應 Figma 設計的 6 種 UI 狀態

```swift
/// Widget 輸入狀態
enum WidgetInputState: Equatable {
    /// 預設狀態：無輸入、無聚焦
    case `default`
    
    /// 聚焦狀態：輸入框有綠色邊框
    case focus
    
    /// 輸入中：有文字、有清除按鈕、Load 按鈕為綠色
    case typing
    
    /// 已填寫：有文字、無聚焦
    case filled
    
    /// 載入中：顯示 Spinner + 提示文字
    case loading
    
    /// 錯誤狀態：紅色邊框 + 錯誤訊息
    case error(message: String)
    
    // MARK: - Computed Properties
    
    /// 輸入框是否顯示綠色邊框
    var showFocusBorder: Bool {
        switch self {
        case .focus, .typing: return true
        default: return false
        }
    }
    
    /// 輸入框是否顯示紅色邊框
    var showErrorBorder: Bool {
        if case .error = self { return true }
        return false
    }
    
    /// 是否顯示清除按鈕
    var showClearButton: Bool {
        switch self {
        case .typing, .filled, .error: return true
        default: return false
        }
    }
    
    /// Load 按鈕是否啟用
    var isLoadButtonEnabled: Bool {
        switch self {
        case .typing, .filled: return true
        default: return false
        }
    }
    
    /// 是否為錯誤狀態
    var isError: Bool {
        if case .error = self { return true }
        return false
    }
    
    /// 取得錯誤訊息
    var errorMessage: String? {
        if case let .error(message) = self { return message }
        return nil
    }
}
```

### ConvertResult

對應 API: `POST /orders/converter/code`

```swift
/// 轉換結果（來自 API）
struct ConvertResult: Equatable {
    let shareCode: String
    let selections: [Selection]
    
    /// 失敗數量
    var failCnt: Int {
        selections.filter { $0.isFailed }.count
    }
    
    /// 成功數量
    var successCnt: Int {
        selections.filter { !$0.isFailed }.count
    }
    
    /// 是否部分失敗
    var hasPartialFailure: Bool {
        failCnt > 0 && successCnt > 0
    }
    
    /// 是否全部失敗
    var isAllFailed: Bool {
        failCnt == selections.count
    }
}

extension ConvertResult {
    /// 單一選項
    struct Selection: Equatable {
        let eventId: String
        let sportId: Int
        let marketId: Int
        let selectionId: Int
        let odds: Double
        let specialBetValue: String?
        let isFailed: Bool
        let failReason: String?
    }
}
```

---

## 既有復用的 Models

### Region（擴展）

```swift
extension Region {
    /// 從 CountryCode 建立
    static func from(countryCode: CountryCode) -> Region? {
        switch countryCode {
        case .nigeria: return .nigeria
        case .ghana: return .ghana
        // ... 其他 mapping
        default: return nil
        }
    }
    
    /// 轉換為 CountryCode
    var countryCode: CountryCode? {
        switch self {
        case .nigeria: return .nigeria
        case .ghana: return .ghana
        // ... 其他 mapping
        default: return nil
        }
    }
}
```

---

## DTO → Domain Model 轉換

### ProviderCountryDTO → ProviderConfig

```swift
/// API Response DTO
struct ProviderCountryDTO: Decodable {
    let provider: String
    let name: String
    let countries: [String]
}

extension ProviderConfig {
    init(from dto: ProviderCountryDTO) {
        self.id = dto.provider
        self.provider = dto.provider
        self.name = dto.name
        self.countries = dto.countries.compactMap { CountryCode(rawValue: $0) }
    }
}
```

### CodeConverterResponseDTO → ConvertResult

```swift
/// API Response DTO
struct CodeConverterResponseDTO: Decodable {
    let shareCode: String
    let selections: [SelectionDTO]
}

struct SelectionDTO: Decodable {
    let eventId: String
    let sportId: Int
    let marketId: Int
    let selectionId: Int
    let odds: Double
    let specialBetValue: String?
    let isFailed: Bool
    let failReason: String?
}

extension ConvertResult {
    init(from dto: CodeConverterResponseDTO) {
        self.shareCode = dto.shareCode
        self.selections = dto.selections.map { Selection(from: $0) }
    }
}

extension ConvertResult.Selection {
    init(from dto: SelectionDTO) {
        self.eventId = dto.eventId
        self.sportId = dto.sportId
        self.marketId = dto.marketId
        self.selectionId = dto.selectionId
        self.odds = dto.odds
        self.specialBetValue = dto.specialBetValue
        self.isFailed = dto.isFailed
        self.failReason = dto.failReason
    }
}
```
