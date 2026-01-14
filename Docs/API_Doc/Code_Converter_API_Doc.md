# Code Converter API Documentation

> **模組**：Code Converter  
> **最後更新**：2025-01-14

---

## ⚠️ BE 新設計更新 (2025-01-14)

| 變更項目 | 說明 |
|----------|------|
| **Config API 廢棄** | ~~`GET /orders/converter/config/providerCountries`~~ 不再使用 |
| **Convert API 簡化** | 不再需要 `provider` 和 `country` 參數，只需 `bookingCode` |

---

## 目錄

1. [Convert Code2Code](#1-convert-code2code) ✅ 使用中
2. ~~[Get Provider Country Config](#2-get-provider-country-config)~~ ❌ 廢棄

---

## 1. Convert Code2Code

將任意 Booking Code 轉換為 Fcom 的 Share Code。

### 基本資訊

| 項目 | 說明 |
|------|------|
| **Method** | `POST` |
| **Endpoint** | `/orders/converter/code` |
| **Description** | Convert any booking code to share code, BE will auto-detect provider |

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
| ~~`provider`~~ | ~~String~~ | ❌ 已移除 | ~~競品 Provider Code~~ **BE 自動識別** |
| ~~`country`~~ | ~~String~~ | ❌ 已移除 | ~~Country Code~~ **BE 自動識別** |
| `bookingCode` | String | ✅ Required | 任意 Booking Code |

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

#### Request (新版 - 2025-01-14)

```bash
curl -X POST '/orders/converter/code' \
  -H 'Content-Type: application/json' \
  -H 'uid: user123' \
  -H 'OperId: operator456' \
  -d '{
    "bookingCode": "3RA3FA"
  }'
```

#### ~~Request (舊版 - 已廢棄)~~

```bash
# ❌ 已廢棄 - 不再需要 provider 和 country
curl -X POST '/orders/converter/code' \
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

### 後續流程

Convert API 成功後，需走原有 Load Code 流程：

| 順序 | API | 說明 |
|:----:|-----|------|
| 1 | `POST /orders/converter/code` | 轉換 Booking Code → 取得 shareCode |
| 2 | `GET /bookingCode/{shareCode}/liabilities` | 檢查 Liabilities（既有流程） |
| 3 | `GET /orders/share/{shareCode}` | 取得 Betslip Data（既有流程） |

---

## 2. Get Provider Country Config ❌ 廢棄

> ⚠️ **此 API 已廢棄** (2025-01-14)
>
> BE 新設計不再需要選擇 Provider/Country，此 API 不再使用。

### ~~基本資訊~~

| 項目 | 說明 |
|------|------|
| **Method** | ~~`GET`~~ |
| **Endpoint** | ~~`/orders/converter/config/providerCountries`~~ |
| **Status** | ❌ **廢棄** |

---

## Error Codes

| bizCode | message | Description | 狀態 |
|---------|---------|-------------|------|
| 10000 | SUCCESS | 請求成功 | ✅ |
| 10001 | INVALID_PARAMETER | 參數錯誤 | ✅ |
| 10002 | CODE_NOT_FOUND | 找不到指定的 Booking Code | ✅ |
| ~~10003~~ | ~~PROVIDER_NOT_SUPPORTED~~ | ~~不支援的 Provider~~ | ❌ 廢棄 |
| ~~10004~~ | ~~COUNTRY_NOT_SUPPORTED~~ | ~~不支援的 Country~~ | ❌ 廢棄 |
| 10005 | TIMEOUT | 請求逾時 | ✅ |
| 10006 | INTERNAL_ERROR | 內部錯誤 | ✅ |

---

## 廢棄項目清單

| 項目 | 類型 | 原因 |
|------|------|------|
| `GET /orders/converter/config/providerCountries` | API | BE 新設計不需要 |
| `provider` 參數 | Request Field | BE 自動識別 |
| `country` 參數 | Request Field | BE 自動識別 |
| `PROVIDER_NOT_SUPPORTED` (10003) | Error Code | 無需驗證 |
| `COUNTRY_NOT_SUPPORTED` (10004) | Error Code | 無需驗證 |

---

## 附錄：圖片來源

| 檔案 | 說明 | 狀態 |
|------|------|------|
| `1_API_ConverterCodeToCode.png` | Convert Code2Code API 文件截圖 | ⚠️ 舊版截圖 |
| `2_API_GetProviderCountryConfig.png` | Get Provider Country Config API 文件截圖 | ❌ 廢棄 |
