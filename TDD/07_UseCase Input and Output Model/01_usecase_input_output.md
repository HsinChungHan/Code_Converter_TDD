# UseCase Input and Output Model

## LoadProviderConfigUseCase

### Input Model

```swift
struct LoadProviderConfigInput: Equatable {
    // 無參數
}
```

**說明**：此 UseCase 不需要任何輸入參數，直接取得所有可用的 Provider Config。

---

### Output Model

```swift
struct LoadProviderConfigOutput: Equatable {
    let providerConfigs: [ProviderConfig]
}
```

| 屬性 | 類型 | 說明 |
|------|------|------|
| `providerConfigs` | `[ProviderConfig]` | 所有可用的 Provider 設定列表 |

---

### UseCase 定義

```swift
protocol LoadProviderConfigUseCaseProtocol {
    func execute() async -> Result<LoadProviderConfigOutput, Error>
}

struct LoadProviderConfigUseCase: LoadProviderConfigUseCaseProtocol {
    let repository: CodeConverterRepositoryProtocol
    
    func execute() async -> Result<LoadProviderConfigOutput, Error> {
        do {
            let configs = try await repository.getProviderCountryConfig()
            return .success(LoadProviderConfigOutput(providerConfigs: configs))
        } catch {
            return .failure(error)
        }
    }
}
```

---

## ConvertBookingCodeUseCase

### Input Model

```swift
struct ConvertBookingCodeInput: Equatable {
    let provider: String
    let country: String
    let bookingCode: String
}
```

| 屬性 | 類型 | 說明 |
|------|------|------|
| `provider` | `String` | 競品 Provider 代碼（如 bet9ja） |
| `country` | `String` | 國家代碼（如 NG） |
| `bookingCode` | `String` | 競品 Booking Code |

---

### Output Model

```swift
struct ConvertBookingCodeOutput: Equatable {
    let convertResult: ConvertResult
    let betslipData: BetslipData
}
```

| 屬性 | 類型 | 說明 |
|------|------|------|
| `convertResult` | `ConvertResult` | 轉換結果（shareCode, successCnt, failCnt） |
| `betslipData` | `BetslipData` | Betslip 資料（既有 Domain Model） |

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
            // 1. 轉換 Booking Code
            let convertResult = try await codeConverterRepository.convertCode(
                provider: input.provider,
                country: input.country,
                bookingCode: input.bookingCode
            )
            
            // 2. 檢查 Liabilities（既有流程）
            _ = try await betslipRepository.checkLiabilities(shareCode: convertResult.shareCode)
            
            // 3. 取得 Betslip Data（既有流程）
            let betslipData = try await betslipRepository.getBetslipData(shareCode: convertResult.shareCode)
            
            return .success(ConvertBookingCodeOutput(
                convertResult: convertResult,
                betslipData: betslipData
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
    case codeNotFound(bookieName: String)
    case providerNotSupported
    case countryNotSupported
    case timeout
    case internalError
    case unknown
    
    var localizedDescription: String {
        switch self {
        case .invalidParameter:
            return "Invalid parameter"
        case .codeNotFound(let bookieName):
            return "We couldn't find this booking code on \(bookieName). Please check and try again."
        case .providerNotSupported:
            return "Provider not supported"
        case .countryNotSupported:
            return "Country not supported"
        case .timeout:
            return "Request timeout. Please try again."
        case .internalError:
            return "Internal error. Please try again later."
        case .unknown:
            return "An unknown error occurred"
        }
    }
    
    static func from(bizCode: Int, bookieName: String = "") -> CodeConverterError {
        switch bizCode {
        case 10001: return .invalidParameter
        case 10002: return .codeNotFound(bookieName: bookieName)
        case 10003: return .providerNotSupported
        case 10004: return .countryNotSupported
        case 10005: return .timeout
        case 10006: return .internalError
        default: return .unknown
        }
    }
}
```

---

## Dependency Injection

```swift
extension DependencyValues {
    var loadProviderConfigUseCase: LoadProviderConfigUseCaseProtocol {
        get { self[LoadProviderConfigUseCaseKey.self] }
        set { self[LoadProviderConfigUseCaseKey.self] = newValue }
    }
    
    var convertBookingCodeUseCase: ConvertBookingCodeUseCaseProtocol {
        get { self[ConvertBookingCodeUseCaseKey.self] }
        set { self[ConvertBookingCodeUseCaseKey.self] = newValue }
    }
}

private enum LoadProviderConfigUseCaseKey: DependencyKey {
    static let liveValue: LoadProviderConfigUseCaseProtocol = LoadProviderConfigUseCase(
        repository: CodeConverterRepository()
    )
}

private enum ConvertBookingCodeUseCaseKey: DependencyKey {
    static let liveValue: ConvertBookingCodeUseCaseProtocol = ConvertBookingCodeUseCase(
        codeConverterRepository: CodeConverterRepository(),
        betslipRepository: BetslipRepository()
    )
}
```

