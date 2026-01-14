# ~~Module Sequence Diagram: Bookie Selection~~ ❌ 廢棄

## ⚠️ 此文件已廢棄

| 項目 | 說明 |
|------|------|
| **廢棄原因** | BE 新設計不再需要選擇 Provider/Country |
| **廢棄日期** | 2025-01 |
| **替代方案** | 無需替代，直接輸入任意 Booking Code 即可轉換 |

---

## 廢棄內容

### ~~原情境說明~~

~~當用戶從 Bookie Selector Sheet 選擇 Bookie 時，有三種情況：~~

1. ~~**ALL 國家 Provider**：如 Fcom，Country 預設為 ALL，無需選擇~~
2. ~~**單一國家 Bookie**：如 Bet9ja，Country 自動選定，無需選擇~~
3. ~~**多國家 Bookie**：如 MSport，需要先選擇 Country~~

### ~~原流程~~

```
❌ 廢棄:
User → 點擊 Bookie Dropdown → 載入 Config → 開啟 Sheet → 選擇 Provider → 選擇 Country → Submit
```

---

## 新流程

```
✅ 新流程:
User → 輸入任意 Booking Code → 點擊 Load → BE 自動識別 Provider/Country
```

---

## 相關廢棄項目

| 項目 | 類型 |
|------|------|
| `BookieSelectorSheet` | UI |
| `BookieDropdownView` | UI |
| `CountryListView` | UI |
| `.bookieSelected` | Action |
| `.bookieSelectorDismissed` | Action |
| `.bookieDropdownTapped` | Action |
| `selectedBookie` | State |
| `isBookieSelectorPresented` | State |
| `providerConfigs` | State |
| `SelectedBookie` | Domain Model |
| `ProviderConfig` | Domain Model |
| `GET /orders/converter/config/providerCountries` | API |

---

## 對開發的影響

### 移除的 UI 元件

1. ❌ `BookieSelectorSheet` - 不需要實作
2. ❌ `BookieDropdownView` - 不需要擴展 `CountryDropdownView`
3. ❌ Provider/Country 選擇邏輯 - 全部移除

### 簡化的 State

```swift
// 舊版 State（已廢棄）
struct State {
    var selectedBookie: SelectedBookie?           // ❌ 移除
    var providerConfigs: [ProviderConfig] = []    // ❌ 移除
    var isBookieSelectorPresented: Bool = false   // ❌ 移除
}

// 新版 State
struct State {
    var bookingCode: String = ""
    var inputState: WidgetInputState = .default
    var isTooltipVisible: Bool = false  // 新增
    // ... 其他
}
```

### 簡化的 Action

```swift
// 舊版 Action（已廢棄）
enum Action {
    case bookieDropdownTapped      // ❌ 移除
    case bookieSelectorDismissed   // ❌ 移除
    case bookieSelected(...)       // ❌ 移除
    case providerConfigLoaded(...) // ❌ 移除
}

// 新版 Action
enum Action {
    case bookingCodeChanged(String)
    case loadBookingCode
    case tooltipDismissed  // 新增
    // ... 其他
}
```
