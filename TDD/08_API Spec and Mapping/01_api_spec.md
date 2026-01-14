# API Spec

## ⚠️ BE 新設計更新 (2025-01)

| 變更項目 | 說明 |
|----------|------|
| **Config API 廢棄** | ~~`GET /orders/converter/config/providerCountries`~~ 不再使用 |
| **Convert API 簡化** | 不再需要 `provider` 和 `country` 參數，只需 `bookingCode` |

---

## ~~廢棄 API~~

### ~~1. Get Provider Country Config~~ ❌ 廢棄

| 項目 | 說明 |
|------|------|
| **Method** | ~~`GET`~~ |
| **Endpoint** | ~~`/orders/converter/config/providerCountries`~~ |
| **狀態** | ❌ **已廢棄 - BE 新設計不再需要** |

---

## 新增 API

### 1. Convert Code2Code

| 項目 | 說明 |
|------|------|
| **Method** | `POST` |
| **Endpoint** | `/orders/converter/code` |
| **Description** | 將任意 Booking Code 轉換為 Fcom Share Code |
| **所屬 Client** | CodeConverterClient |
| **所屬 Repository** | CodeConverterRepository |
| **所屬 UseCase** | ConvertBookingCodeUseCase |

#### Headers

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uid` | String | Optional | User ID |
| `OperId` | String | Optional | Operator ID |

#### Request Body

```json
{
  "bookingCode": "3RA3FA"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ~~`provider`~~ | ~~String~~ | ❌ | ~~競品 Provider Code~~ **已移除** |
| ~~`country`~~ | ~~String~~ | ❌ | ~~Country Code~~ **已移除** |
| `bookingCode` | String | ✅ | 任意 Booking Code |

#### Response - Success

```json
{
  "bizCode": 10000,
  "message": "SUCCESS",
  "data": {
    "shareCode": "ABC123",
    "successCnt": 5,
    "failCnt": 1
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `shareCode` | String | 轉換後的 Fcom Share Code |
| `successCnt` | Int | 成功轉換的 selection 數量 |
| `failCnt` | Int | 失敗的 selection 數量 |

---

## 既有 API（復用）

### 2. Check Liabilities

| 項目 | 說明 |
|------|------|
| **Method** | `GET` |
| **Endpoint** | `/bookingCode/{shareCode}/liabilities` |
| **Description** | 檢查 Share Code 的 Liabilities |
| **所屬 Client** | BetslipClient（既有） |
| **所屬 Repository** | BetslipRepository（既有） |
| **備註** | Convert API 成功後，使用返回的 shareCode 呼叫 |

---

### 3. Get Share Order

| 項目 | 說明 |
|------|------|
| **Method** | `GET` |
| **Endpoint** | `/orders/share/{shareCode}` |
| **Description** | 取得 Share Code 對應的 Betslip Data |
| **所屬 Client** | BetslipClient（既有） |
| **所屬 Repository** | BetslipRepository（既有） |
| **備註** | Liabilities 檢查後，取得 Betslip 內容 |

---

## Error Codes

| bizCode | message | Description |
|---------|---------|-------------|
| 10000 | SUCCESS | 請求成功 |
| 10001 | INVALID_PARAMETER | 參數錯誤 |
| 10002 | CODE_NOT_FOUND | 找不到指定的 Booking Code |
| ~~10003~~ | ~~PROVIDER_NOT_SUPPORTED~~ | ~~不支援的 Provider~~ **已廢棄** |
| ~~10004~~ | ~~COUNTRY_NOT_SUPPORTED~~ | ~~不支援的 Country~~ **已廢棄** |
| 10005 | TIMEOUT | 請求逾時 |
| 10006 | INTERNAL_ERROR | 內部錯誤 |

---

## API 調用順序

| 順序 | API | 時機 | 狀態 |
|:----:|-----|------|------|
| ~~1~~ | ~~GET `/orders/converter/config/providerCountries`~~ | ~~點擊 Bookie Dropdown~~ | ❌ 廢棄 |
| 1 | POST `/orders/converter/code` | 點擊 Load 按鈕 | ✅ |
| 2 | GET `/bookingCode/{shareCode}/liabilities` | 轉換成功後 | ✅ 既有流程 |
| 3 | GET `/orders/share/{shareCode}` | Liabilities 檢查後 | ✅ 既有流程 |

---

## DTO 定義

### ConvertCodeRequestDTO

```swift
struct ConvertCodeRequestDTO: Encodable {
    let bookingCode: String
    
    // 已移除
    // let provider: String
    // let country: String
}
```

### ConvertCodeResponseDTO

```swift
struct ConvertCodeResponseDTO: Decodable {
    let bizCode: Int
    let message: String
    let data: ConvertCodeDataDTO?
}

struct ConvertCodeDataDTO: Decodable {
    let shareCode: String
    let successCnt: Int
    let failCnt: Int
}
```

---

## 廢棄項目

| 項目 | 類型 | 原因 |
|------|------|------|
| `GET /orders/converter/config/providerCountries` | API | BE 新設計不再需要選擇 Provider |
| `ProviderCountryConfigDTO` | DTO | 對應 Config API 廢棄 |
| `provider` 參數 | Request Field | BE 會自動識別 |
| `country` 參數 | Request Field | BE 會自動識別 |
| `PROVIDER_NOT_SUPPORTED` (10003) | Error Code | 無需驗證 Provider |
| `COUNTRY_NOT_SUPPORTED` (10004) | Error Code | 無需驗證 Country |
