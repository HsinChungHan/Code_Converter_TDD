# Domain Model

## ⚠️ BE 新設計更新 (2025-01)

| 變更項目 | 說明 |
|----------|------|
| **ProviderConfig 廢棄** | 不再需要 Provider Config 資料 |
| **SelectedBookie 廢棄** | 不再需要選擇 Bookie |
| **CountryCode 簡化** | 仍保留但不再用於 Bookie 選擇 |

---

## 模型總覽

```
┌─────────────────────────────────────────────────────────────────┐
│                         Domain Models                           │
├─────────────────────────────────────────────────────────────────┤
│  ConvertResult         轉換結果（來自 API）                      │
│  WidgetInputState      Widget 輸入狀態（6 種狀態）               │
├─────────────────────────────────────────────────────────────────┤
│                     既有復用的 Models                            │
├─────────────────────────────────────────────────────────────────┤
│  Region                現有國家/地區 enum                        │
│  LoadCodeModel.CodeResult  現有載入結果                          │
│  EventDetailOutcomeElement 現有選項元素                          │
├─────────────────────────────────────────────────────────────────┤
│                     廢棄的 Models                                │
├─────────────────────────────────────────────────────────────────┤
│  ❌ ProviderConfig      已廢棄 - 不再需要 Provider 設定           │
│  ❌ SelectedBookie      已廢棄 - 不再需要 Bookie 選擇            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 新增的 Domain Models

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
    let successCnt: Int
    let failCnt: Int
    
    /// 是否部分失敗
    var hasPartialFailure: Bool {
        failCnt > 0 && successCnt > 0
    }
    
    /// 是否全部失敗
    var isAllFailed: Bool {
        successCnt == 0 && failCnt > 0
    }
}
```

---

## 既有復用的 Models

### Region（無需擴展）

```swift
// 保持現有 Region enum 不變
// 不再需要從 CountryCode 轉換
```

---

## DTO → Domain Model 轉換

### CodeConverterResponseDTO → ConvertResult

```swift
/// API Response DTO
struct CodeConverterResponseDTO: Decodable {
    let bizCode: Int
    let message: String
    let data: CodeConverterDataDTO?
}

struct CodeConverterDataDTO: Decodable {
    let shareCode: String
    let successCnt: Int
    let failCnt: Int
}

extension ConvertResult {
    init(from dto: CodeConverterDataDTO) {
        self.shareCode = dto.shareCode
        self.successCnt = dto.successCnt
        self.failCnt = dto.failCnt
    }
}
```

---

## 廢棄的 Domain Models

### ~~ProviderConfig~~ ❌ 廢棄

```swift
// ❌ 廢棄 - 不再需要
// 原用途：對應 API: GET /orders/converter/config/providerCountries
// struct ProviderConfig: Equatable, Identifiable {
//     let id: String
//     let provider: String
//     let name: String
//     let countries: [CountryCode]
// }
```

### ~~SelectedBookie~~ ❌ 廢棄

```swift
// ❌ 廢棄 - 不再需要
// 原用途：儲存已選擇的 Bookie
// struct SelectedBookie: Equatable {
//     let provider: String
//     let name: String
//     let country: CountryCode
// }
```

### ~~CountryCode~~ ❌ 廢棄

```swift
// ❌ 廢棄 - 不再需要
// 原用途：國家代碼 Value Object
// enum CountryCode: String, Equatable, CaseIterable {
//     case nigeria = "NG"
//     case ghana = "GH"
//     // ...
// }
```

---

## 廢棄項目清單

| 項目 | 類型 | 原因 |
|------|------|------|
| `ProviderConfig` | Domain Model | Config API 已廢棄 |
| `SelectedBookie` | Domain Model | 不再需要選擇 Bookie |
| `CountryCode` | Value Object | 不再需要國家代碼 |
| `ProviderCountryDTO` | DTO | 對應 API 已廢棄 |
