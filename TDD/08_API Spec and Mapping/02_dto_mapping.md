# DTO → Domain Model Mapping

## DTO 定義

### ProviderCountryConfigDTO

```swift
struct ProviderCountryConfigResponse: Decodable {
    let bizCode: Int
    let message: String
    let data: [ProviderCountryConfigDTO]?
}

struct ProviderCountryConfigDTO: Decodable {
    let provider: String
    let name: String
    let countries: [String]
}
```

---

### Code2CodeDTO

```swift
struct Code2CodeResponse: Decodable {
    let bizCode: Int
    let message: String
    let innerMsg: String?
    let data: Code2CodeDataDTO?
}

struct Code2CodeDataDTO: Decodable {
    let shareCode: String
    let successCnt: Int
    let failCnt: Int
}
```

---

### Code2CodeRequestDTO

```swift
struct Code2CodeRequestDTO: Encodable {
    let provider: String
    let country: String
    let bookingCode: String
}
```

---

## Mapping 規則

### ProviderCountryConfigDTO → ProviderConfig

| DTO 欄位 | Domain Model 欄位 | 轉換邏輯 |
|----------|-------------------|----------|
| `provider` | `provider` | 直接對應 |
| `name` | `name` | 直接對應 |
| `countries` | `countries` | String[] → [CountryCode]，過濾無效值 |

**實作：**

```swift
extension ProviderConfig {
    init(from dto: ProviderCountryConfigDTO) {
        self.provider = dto.provider
        self.name = dto.name
        self.countries = dto.countries.compactMap { CountryCode(rawValue: $0) }
    }
}
```

---

### Code2CodeDataDTO → ConvertResult

| DTO 欄位 | Domain Model 欄位 | 轉換邏輯 |
|----------|-------------------|----------|
| `shareCode` | `shareCode` | 直接對應 |
| `successCnt` | `successCnt` | 直接對應 |
| `failCnt` | `failCnt` | 直接對應 |

**實作：**

```swift
extension ConvertResult {
    init(from dto: Code2CodeDataDTO) {
        self.shareCode = dto.shareCode
        self.successCnt = dto.successCnt
        self.failCnt = dto.failCnt
    }
}
```

---

## Repository Mapping 責任

| Repository | DTO | Domain Model |
|------------|-----|--------------|
| **CodeConverterRepository** | ProviderCountryConfigDTO | ProviderConfig |
| **CodeConverterRepository** | Code2CodeDataDTO | ConvertResult |
| **BetslipRepository** | LiabilitiesDTO | Liabilities（既有） |
| **BetslipRepository** | BetslipDataDTO | BetslipData（既有） |

---

## Repository 實作

```swift
protocol CodeConverterRepositoryProtocol {
    func getProviderCountryConfig() async throws -> [ProviderConfig]
    func convertCode(provider: String, country: String, bookingCode: String) async throws -> ConvertResult
}

struct CodeConverterRepository: CodeConverterRepositoryProtocol {
    let client: CodeConverterClient
    
    init(client: CodeConverterClient = .live) {
        self.client = client
    }
    
    func getProviderCountryConfig() async throws -> [ProviderConfig] {
        let response = try await client.fetchProviderCountries()
        
        guard response.bizCode == 10000, let data = response.data else {
            throw CodeConverterError.from(bizCode: response.bizCode)
        }
        
        return data.map { ProviderConfig(from: $0) }
    }
    
    func convertCode(provider: String, country: String, bookingCode: String) async throws -> ConvertResult {
        let request = Code2CodeRequestDTO(
            provider: provider,
            country: country,
            bookingCode: bookingCode
        )
        
        let response = try await client.convertCode(request)
        
        guard response.bizCode == 10000, let data = response.data else {
            throw CodeConverterError.from(bizCode: response.bizCode, bookieName: provider)
        }
        
        return ConvertResult(from: data)
    }
}
```

