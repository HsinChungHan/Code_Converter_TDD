# UseCase Input and Output Model

## ⚠️ BE 新設計更新 (2025-01)

| 變更項目 | 說明 |
|----------|------|
| **LoadProviderConfigUseCase 廢棄** | Config API 已廢棄 |
| **ConvertBookingCodeInput 簡化** | 只需 `bookingCode`，移除 `provider` 和 `country` |

---

## ~~LoadProviderConfigUseCase~~ ❌ 廢棄

```swift
// ❌ 廢棄 - Config API 已不再使用
// struct LoadProviderConfigInput: Equatable { }
// struct LoadProviderConfigOutput: Equatable {
//     let providerConfigs: [ProviderConfig]
// }
```

---

## ConvertBookingCodeUseCase

### Input Model

```swift
struct ConvertBookingCodeInput: Equatable {
    let bookingCode: String
    
    // ❌ 已移除
    // let provider: String
    // let country: String
}
```

| 屬性 | 類型 | 說明 |
|------|------|------|
| `bookingCode` | `String` | 任意 Booking Code（BE 自動識別 Provider） |
| ~~`provider`~~ | ~~`String`~~ | ❌ 已移除 |
| ~~`country`~~ | ~~`String`~~ | ❌ 已移除 |

---

### Output Model

```swift
struct ConvertBookingCodeOutput: Equatable {
    let convertResult: ConvertResult
    let liabilities: LiabilitiesResult
}
```

| 屬性 | 類型 | 說明 |
|------|------|------|
| `convertResult` | `ConvertResult` | 轉換結果（shareCode, successCnt, failCnt） |
| `liabilities` | `LiabilitiesResult` | Liabilities 檢查結果（既有流程） |

---

### UseCase 定義

```swift
protocol ConvertBookingCodeUseCaseProtocol {
    func execute(_ input: ConvertBookingCodeInput) async -> Result<ConvertBookingCodeOutput, Error>
}

struct ConvertBookingCodeUseCase: ConvertBookingCodeUseCaseProtocol {
    let codeConverterRepository: CodeConverterRepositoryProtocol
    let betslipRepository: BetslipRepositoryProtocol
    
    func execute(_ input: ConvertBookingCodeInput) async -> Result<ConvertBookingCodeOutput, Error> {
        do {
            // 1. 轉換 Booking Code（只需 bookingCode）
            let convertResult = try await codeConverterRepository.convertCode(
                bookingCode: input.bookingCode
            )
            
            // 檢查是否全部失敗
            guard !convertResult.isAllFailed else {
                throw CodeConverterError.allSelectionsFailed
            }
            
            // 2. 檢查 Liabilities（既有流程 - 使用返回的 shareCode）
            let liabilities = try await betslipRepository.checkLiabilities(
                shareCode: convertResult.shareCode
            )
            
            return .success(ConvertBookingCodeOutput(
                convertResult: convertResult,
                liabilities: liabilities
            ))
        } catch {
            return .failure(error)
        }
    }
}
```

---

## Error Types

```swift
enum CodeConverterError: Error, Equatable {
    case invalidParameter
    case codeNotFound
    case allSelectionsFailed
    case timeout
    case internalError
    case unknown
    
    var localizedDescription: String {
        switch self {
        case .invalidParameter:
            return "Invalid parameter"
        case .codeNotFound:
            return "We couldn't find this booking code. Please check and try again."
        case .allSelectionsFailed:
            return "All selections failed to convert"
        case .timeout:
            return "Request timeout. Please try again."
        case .internalError:
            return "Internal error. Please try again later."
        case .unknown:
            return "An unknown error occurred"
        }
    }
    
    static func from(bizCode: Int) -> CodeConverterError {
        switch bizCode {
        case 10001: return .invalidParameter
        case 10002: return .codeNotFound
        case 10005: return .timeout
        case 10006: return .internalError
        default: return .unknown
        }
    }
}
```

### 廢棄的 Error Cases

| Error Case | 原因 |
|------------|------|
| ~~`providerNotSupported`~~ | 不再需要 Provider 驗證 |
| ~~`countryNotSupported`~~ | 不再需要 Country 驗證 |
| ~~`codeNotFound(bookieName:)`~~ | 簡化為不帶 bookieName |

---

## Dependency Injection

```swift
extension DependencyValues {
    var convertBookingCodeUseCase: ConvertBookingCodeUseCaseProtocol {
        get { self[ConvertBookingCodeUseCaseKey.self] }
        set { self[ConvertBookingCodeUseCaseKey.self] = newValue }
    }
    
    // ❌ 廢棄
    // var loadProviderConfigUseCase: LoadProviderConfigUseCaseProtocol { ... }
}

private enum ConvertBookingCodeUseCaseKey: DependencyKey {
    static let liveValue: ConvertBookingCodeUseCaseProtocol = ConvertBookingCodeUseCase(
        codeConverterRepository: CodeConverterRepository(),
        betslipRepository: BetslipRepository()
    )
}
```

---

## 廢棄項目清單

| 項目 | 類型 | 原因 |
|------|------|------|
| `LoadProviderConfigUseCase` | UseCase | Config API 已廢棄 |
| `LoadProviderConfigInput` | Input Model | 對應 UseCase 已廢棄 |
| `LoadProviderConfigOutput` | Output Model | 對應 UseCase 已廢棄 |
| `provider` 參數 | Input Field | BE 自動識別 |
| `country` 參數 | Input Field | BE 自動識別 |
| `providerNotSupported` | Error Case | 無需驗證 |
| `countryNotSupported` | Error Case | 無需驗證 |
