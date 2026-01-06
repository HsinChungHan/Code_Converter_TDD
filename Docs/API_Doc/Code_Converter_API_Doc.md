# Code Converter API Documentation

> **模組**：Code Converter  
> **最後更新**：2025-01-06

---

## 目錄

1. [Convert Code2Code](#1-convert-code2code)
2. [Get Provider Country Config](#2-get-provider-country-config)

---

## 1. Convert Code2Code

將競品的 Booking Code 轉換為 Fcom 的 Share Code。

### 基本資訊

| 項目 | 說明 |
|------|------|
| **Method** | `POST` |
| **Endpoint** | `/orders/converter/code` |
| **Description** | Convert competitor booking code to share code, returns bookingCode as shareCode |

---

### Header

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uid` | String | Optional | User ID |
| `OperId` | String | Optional | Operator ID |

---

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | String | ✅ Required | 競品 Provider Code |
| `country` | String | ✅ Required | Country Code |
| `bookingCode` | String | ✅ Required | 競品 Booking Code |

#### `provider` 可用值

| Value | Description |
|-------|-------------|
| `fcom` | Fcom (Football.com) |
| `sporty` | Sporty |
| `bet9ja` | Bet9ja |
| `betking` | BetKing |
| `msport` | MSport |

#### `country` 可用值

| Value | Description |
|-------|-------------|
| `ALL` | 所有國家 |
| `NG` | Nigeria |
| `KE` | Kenya |
| `UG` | Uganda |
| `GH` | Ghana |
| `ZM` | Zambia |
| `TZ` | Tanzania |

---

### Response

#### Success 200

| Field | Type | Description |
|-------|------|-------------|
| `bizCode` | Number | Response code (10000 = Success) |
| `message` | String | Response message |
| `data` | `Code2CodeVO` | Code convert result |

#### Code2CodeVO

| Field | Type | Description |
|-------|------|-------------|
| `shareCode` | String | 轉換後的 Fcom Share Code |
| `successCnt` | Number | 成功轉換的 selection 數量 |
| `failCnt` | Number | 轉換失敗的 selection 數量 |

---

### Example

#### Request

```bash
curl -X POST '/orders/converter/code' \
  -H 'Content-Type: application/json' \
  -H 'uid: user123' \
  -H 'OperId: operator456' \
  -d '{
    "provider": "bet9ja",
    "country": "NG",
    "bookingCode": "3RA3FA"
  }'
```

#### Response - Success

```json
{
  "bizCode": 10000,
  "message": "SUCCESS",
  "innerMsg": "SUCCESS",
  "data": {
    "shareCode": "ABC123",
    "successCnt": 5,
    "failCnt": 1
  }
}
```

---

### 狀態判斷邏輯

| 條件 | 狀態 | 說明 |
|------|------|------|
| `failCnt == 0` | SUCCESS | 全部轉換成功 |
| `failCnt > 0 && successCnt > 0` | PARTIAL | 部分轉換成功 |
| `successCnt == 0` | FAILED | 全部轉換失敗 |

---

## 2. Get Provider Country Config

取得支援的 Provider 及其對應的國家設定。

### 基本資訊

| 項目 | 說明 |
|------|------|
| **Method** | `GET` |
| **Endpoint** | `/orders/converter/config/providerCountries` |
| **Description** | Get supported countries per provider from config |

---

### Request

此 API 無需任何參數。

---

### Response

#### Success 200

| Field | Type | Description |
|-------|------|-------------|
| `bizCode` | Number | Response code (10000 = Success) |
| `message` | String | Response message |
| `data` | Array | Provider country config 列表 |

#### Data Item (Provider Config)

| Field | Type | Description |
|-------|------|-------------|
| `provider` | String | Provider code |
| `name` | String | Provider 顯示名稱 |
| `countries` | Array\<String\> | 支援的國家代碼列表 |

#### `provider` 可用值

| Value | Description |
|-------|-------------|
| `fcom` | Fcom (Football.com) |
| `sporty` | Sporty |
| `bet9ja` | Bet9ja |
| `betking` | BetKing |
| `msport` | MSport |

#### `countries` 可用值

| Value | Description |
|-------|-------------|
| `ALL` | 所有國家（通常用於 Fcom） |
| `NG` | Nigeria |
| `KE` | Kenya |
| `UG` | Uganda |
| `GH` | Ghana |
| `ZM` | Zambia |
| `TZ` | Tanzania |

---

### Example

#### Request

```bash
curl -X GET '/orders/converter/config/providerCountries'
```

#### Response - Success

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
      "provider": "betking",
      "name": "BetKing",
      "countries": ["NG"]
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
    },
    {
      "provider": "sporty",
      "name": "Sporty",
      "countries": ["NG", "GH"]
    }
  ]
}
```

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

> ⚠️ **Note**: Error codes 需與 BE 確認實際定義

---

## 附錄：圖片來源

| 檔案 | 說明 |
|------|------|
| `1_API_ConverterCodeToCode.png` | Convert Code2Code API 文件截圖 |
| `2_API_GetProviderCountryConfig.png` | Get Provider Country Config API 文件截圖 |

