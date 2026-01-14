# LoadBookingCodeSection - 版本變更紀錄

---

## 📅 01_14 (2025-01-14) - BE 新設計更新 ⚠️

### 🔄 BE 新設計變更摘要

| 變更項目 | 舊版 | 新版 |
|----------|------|------|
| **Provider/Country 選擇** | 需先選擇 Bookie | ❌ **廢棄** - 不需選擇 |
| **Config API** | `GET /orders/converter/config/providerCountries` | ❌ **廢棄** |
| **Convert API Request** | `{provider, country, bookingCode}` | `{bookingCode}` 只需 bookingCode |
| **Bookie Selector Sheet** | 需實作 | ❌ **廢棄** - 不需實作 |
| **流程** | 選 Bookie → 輸入 Code → 轉換 | 輸入 Code → 轉換 → 走原有 load code 流程 |

### ❌ 新廢棄項目

| 項目 | 類型 | 原因 |
|------|------|------|
| `GET /orders/converter/config/providerCountries` | API | BE 不再需要 |
| `LoadProviderConfigUseCase` | UseCase | 對應 API 廢棄 |
| `ProviderConfig` | Domain Model | 對應 API 廢棄 |
| `SelectedBookie` | Domain Model | 不再需要選擇 |
| `CountryCode` | Value Object | 不再需要 |
| `selectedBookie` State | State | 不再需要 |
| `providerConfigs` State | State | 不再需要 |
| `isBookieSelectorPresented` State | State | 不再需要 |
| `bookieDropdownTapped` Action | Action | 不再需要 |
| `bookieSelected` Action | Action | 不再需要 |
| `bookieSelectorDismissed` Action | Action | 不再需要 |
| `provider` 參數 | API Request | BE 自動識別 |
| `country` 參數 | API Request | BE 自動識別 |

### ✅ 保留的功能

| 功能 | 說明 |
|------|------|
| 6 種輸入狀態 | Default, Focus, Typing, Filled, Loading, Error |
| BookingCodeInputView | 核心輸入元件 |
| ConvertBookingCodeUseCase | Code2Code 轉換（簡化版） |
| Betslip 導航 | 含 Partial Error Toast |
| Tooltip | 首次使用引導 (Device ID 儲存) |

### 🆕 新增項目

| 項目 | 說明 |
|------|------|
| `04_tooltip_display_logic.md` | Tooltip 顯示邏輯序列圖 |
| `isTooltipVisible` State | Tooltip 顯示狀態 |
| `tooltipDismissed` Action | 關閉 Tooltip |
| `TooltipStorage` | Tooltip 儲存邏輯 (UserDefaults + Device ID) |

### 📐 簡化後的流程

```
舊流程（已廢棄）:
User → 選擇 Bookie → 輸入 Code → 轉換

新流程:
User → (Tooltip 首次顯示) → 輸入 Code → POST /orders/converter/code → 走原有 Load Code 流程
```

---

## 📅 01_12 (2025-01-12)

### 🆕 新增功能 1：Info Icon → GuideDialog

| 項目 | 說明 |
|------|------|
| **功能** | 點擊 Info Icon (ⓘ) 彈出說明 Dialog |
| **標題** | "Import Booking Code" |
| **內容** | Bullet list 說明支援的功能 |
| **按鈕** | "Ok" |
| **Figma node-id** | `27536:84826` |

### 復用現有元件：GuideDialog

```
FComUI/Sources/FComUI/GuideDialog/
├── View/
│   └── GuideDialogView.swift
├── Model/
│   ├── GuideDialogViewState.swift  ← ViewState, Page, Theme
│   └── GuideDialogViewAction.swift
└── FComUIFactory+GuideDialog.swift ← Factory method
```

---

### 🆕 新增功能 2：One-Time Tooltip

| 項目 | 說明 |
|------|------|
| **功能** | Feature 上線後顯示一次性提示 |
| **文字** | "Supports booking codes from many platforms" |
| **行為** | 點擊後消失，按 device ID 存儲到 local storage |
| **Figma node-id** | `27526:71304` |

### 復用現有元件：Tooltip

```
FComUI/Sources/FComUI/Tooltip/
├── TooltipView.swift           ← 核心 View
├── Tooltip+Model.swift
├── ViewModels/
│   ├── TooltipViewState.swift  ← Placement, Config
│   └── TooltipViewAction.swift
└── Extensions/
    └── View+TooltipView.swift  ← .showTooltip() modifier
```

### 使用方式

```swift
// Tooltip: 外層加上 .tooltipOverlay()，Widget 上加上 .showTooltip(config:)
// GuideDialog: 用 .fullScreenCover 包裝 FComUIFactory.createGuideDialogView()
```

---

## 📅 01_09 (2025-01-09) - 當前版本

### 🔄 需求變更摘要

| 變更類型 | 說明 |
|----------|------|
| **簡化流程** | 移除 Bookie/Country 選擇器，使用者直接輸入 Booking Code |
| **UI 變更** | 按鈕文字 "Load" → "Import"，Placeholder 變更 |
| **新增元件** | Info Tip Icon (ⓘ) |
| **移除元件** | BookieDropdownView, BookieSelectorSheet |

### ❌ 已移除的功能

| 功能 | 原 TDD 文件 | 狀態 |
|------|-------------|------|
| Bookie Selector Sheet | `01_view_implementation.md` | ❌ 不需實作 |
| BookieDropdownView | `01_view_implementation.md` | ❌ 不需實作 |
| CountryDropdownView 擴展 | `01_view_implementation.md` | ❌ 不需實作 |
| LoadProviderConfigUseCase | `07_UseCase` | ❌ 不需實作 |
| 1.0.3 Bookie Selection 畫面 | `03_state_to_figma_mapping.md` | ❌ 已移除 |
| 1.0.4 Type Done 畫面 | `03_state_to_figma_mapping.md` | ❌ 已移除 |

### ✅ 保留的功能

| 功能 | 說明 |
|------|------|
| 6 種輸入狀態 | Default, Focus, Typing, Filled, Loading, Error |
| LoadBookingCodeSectionView 擴展 | 核心 View 結構不變 |
| BookingCodeInputView 擴展 | 增加狀態、清除按鈕 |
| ConvertBookingCodeUseCase | Code2Code 轉換 |
| Betslip 導航 | 含 Partial Error Toast |

### 🆕 新增內容

| 項目 | 檔案 |
|------|------|
| UI 替換策略 (01_09) | `05_ui_replacement_strategy_01_09.md` |
| Info Tip Icon | 16px，點擊顯示提示 |
| 簡化的 State/Action | 移除 Bookie 相關屬性 |

### 📐 元件結構對比

#### 舊版 (01_01)
```
LoadBookingCodeSectionView
├── HStack
│   ├── BookieDropdownView ← ❌ 移除
│   └── BookingCodeInputView
└── BookieSelectorSheet ← ❌ 移除
```

#### 新版 (01_09)
```
LoadBookingCodeSectionView
├── VStack
│   ├── HStack (Input Row)
│   │   ├── Input Container
│   │   │   ├── TextField
│   │   │   ├── Clear Button
│   │   │   └── Import Button
│   │   └── Info Tip Icon ← 🆕 新增
│   └── Helper Text (Loading/Error)
└── (無 Sheet)
```

---

## 📅 01_01 (2025-01-01) - 舊版

### 功能描述

- 完整 Bookie + Country 選擇器
- Bottom Sheet 雙欄選擇器
- LoadProviderConfigUseCase 取得 Provider Config
- 用戶需選擇 Bookie 後才能 Load

### 相關檔案

| 檔案 | 說明 |
|------|------|
| `01_view_implementation.md` | 包含 BookieDropdownView, BookieSelectorSheet |
| `02_view_design_specs.md` | 舊版 Design Tokens |
| `03_state_to_figma_mapping.md` | 包含 1.0.3, 1.0.4 畫面 |
| `04_figma_to_design_system_mapping.md` | Figma → Code 對照 |

---

## 📚 如何使用

### 如果你在實作 01_09 版本

1. **優先參考**：`05_ui_replacement_strategy_01_09.md`
2. **忽略**：
   - `01_view_implementation.md` 中的 BookieDropdownView, BookieSelectorSheet
   - `03_state_to_figma_mapping.md` 中的 1.0.3, 1.0.4, Bookie Selector 部分

### 如果你需要回顧舊版設計

1. 參考 `Docs/02_Design/01_01/` 資料夾
2. 使用 `01_view_implementation.md` 完整內容

---

## 🔗 快速導航

| 文件 | 版本 | 用途 |
|------|------|------|
| [05_ui_replacement_strategy_01_09.md](./05_ui_replacement_strategy_01_09.md) | 01_09 | ⭐ UI 替換策略 |
| [01_view_implementation.md](./01_view_implementation.md) | 01_01 | View 實作 (部分已過時) |
| [03_state_to_figma_mapping.md](./03_state_to_figma_mapping.md) | 已更新 | State ↔ Figma 對照 |
| [02_view_design_specs.md](./02_view_design_specs.md) | 01_01 | Design Specs (部分已過時) |

