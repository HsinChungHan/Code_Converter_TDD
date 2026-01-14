# ~~Module Sequence Diagram: Load Provider Config~~ ❌ 廢棄

## ⚠️ 此文件已廢棄

| 項目 | 說明 |
|------|------|
| **廢棄原因** | BE 新設計不再需要 Provider Config API |
| **廢棄日期** | 2025-01 |
| **替代方案** | 無需替代，直接輸入 Booking Code 即可轉換 |

---

## 廢棄內容

### ~~原觸發時機~~

~~用戶點擊 Bookie Dropdown 時，載入 Provider Config 並顯示 Bookie Selector Sheet。~~

### ~~原 API~~

```
❌ 廢棄: GET /orders/converter/config/providerCountries
```

### ~~原流程~~

```
❌ 廢棄: 
User → 點擊 Bookie Dropdown → 載入 Config → 開啟 Bookie Selector Sheet
```

---

## 新文件位置

Tooltip 相關邏輯請參考：

- [04_tooltip_display_logic.md](./04_tooltip_display_logic.md)

---

## 相關廢棄項目

| 項目 | 類型 |
|------|------|
| `LoadProviderConfigUseCase` | UseCase |
| `ProviderConfig` | Domain Model |
| `ProviderCountryConfigDTO` | DTO |
| `BookieSelectorSheet` | UI |
| `BookieDropdownView` | UI |
| `.bookieDropdownTapped` | Action |
| `providerConfigs` | State |
| `isBookieSelectorPresented` | State |
