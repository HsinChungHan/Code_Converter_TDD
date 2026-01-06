# API Spec

## 新增 API

### 1. Get Provider Country Config

| 項目 | 說明 |
|------|------|
| **Method** | `GET` |
| **Endpoint** | `/orders/converter/config/providerCountries` |
| **Description** | 取得支援的 Provider 及其對應的國家設定 |
| **所屬 Client** | CodeConverterClient |
| **所屬 Repository** | CodeConverterRepository |
| **所屬 UseCase** | LoadProviderConfigUseCase |

#### Request

無參數

#### Response

```json
{
  "bizCode": 10000,
  "message": "SUCCESS",
  "data": [
    {
      "provider": "fcom",
      "name": "F.com",
      "countries": ["ALL"]
    },
    {
      "provider": "bet9ja",
      "name": "Bet9ja",
      "countries": ["NG"]
    },
    {
      "provider": "msport",
      "name": "MSport",
      "countries": ["NG", "GH", "UG", "ZM"]
    }
  ]
}
```

---

### 2. Convert Code2Code

| 項目 | 說明 |
|------|------|
| **Method** | `POST` |
| **Endpoint** | `/orders/converter/code` |
| **Description** | 將競品 Booking Code 轉換為 Fcom Share Code |
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
  "provider": "bet9ja",
  "country": "NG",
  "bookingCode": "3RA3FA"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | String | ✅ | 競品 Provider Code |
| `country` | String | ✅ | Country Code |
| `bookingCode` | String | ✅ | 競品 Booking Code |

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

---

## 既有 API（復用）

### 3. Check Liabilities

| 項目 | 說明 |
|------|------|
| **Method** | `GET` |
| **Endpoint** | `/bookingCode/{shareCode}/liabilities` |
| **Description** | 檢查 Share Code 的 Liabilities |
| **所屬 Client** | BetslipClient（既有） |
| **所屬 Repository** | BetslipRepository（既有） |

---

### 4. Get Share Order

| 項目 | 說明 |
|------|------|
| **Method** | `GET` |
| **Endpoint** | `/orders/share/{shareCode}` |
| **Description** | 取得 Share Code 對應的 Betslip Data |
| **所屬 Client** | BetslipClient（既有） |
| **所屬 Repository** | BetslipRepository（既有） |

---

## Error Codes

| bizCode | message | Description |
|---------|---------|-------------|
| 10000 | SUCCESS | 請求成功 |
| 10001 | INVALID_PARAMETER | 參數錯誤 |
| 10002 | CODE_NOT_FOUND | 找不到指定的 Booking Code |
| 10003 | PROVIDER_NOT_SUPPORTED | 不支援的 Provider |
| 10004 | COUNTRY_NOT_SUPPORTED | 不支援的 Country |
| 10005 | TIMEOUT | 請求逾時 |
| 10006 | INTERNAL_ERROR | 內部錯誤 |

---

## API 調用順序

| 順序 | API | 時機 |
|:----:|-----|------|
| 1 | GET `/orders/converter/config/providerCountries` | 點擊 Bookie Dropdown |
| 2 | POST `/orders/converter/code` | 點擊 Load 按鈕 |
| 3 | GET `/bookingCode/{shareCode}/liabilities` | 轉換成功後 |
| 4 | GET `/orders/share/{shareCode}` | Liabilities 檢查後 |

