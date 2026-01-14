# Code Converter Widget - UI Only Implementation Plan

> **最後更新**: 2026-01-13

## 概述

將 "Load Booking Code" 功能統一為新的 "Code Converter Widget"，初期只替換 UI，保留既有 API 邏輯。

---

## 架構決策

### Option A（❌ 不採用）：擴展現有 View
- 修改 `LoadBookingCodeSectionView`
- 風險：影響現有邏輯，難以回滾

### Option B（✅ 採用）：建立新的 Widget
- 新建 `CodeConverterWidget` 資料夾
- Feature Flag 控制切換
- 優點：隔離風險，易於 A/B 測試

---

## 檔案結構規劃

```
FCom/Home Tab/HomeListView/LoadBookingCode/
├── CodeConverterWidget/
│   ├── CodeConverterConfig.swift          # Feature Flag
│   ├── WidgetInputState.swift             # 輸入狀態 enum
│   ├── CodeConverterWidget+Feature.swift  # TCA State/Action/Reducer
│   ├── CodeConverterWidgetView.swift      # SwiftUI View
│   └── CodeConverterTooltipStorage.swift  # Tooltip 顯示記錄
└── LoadBookingCodeSectionView.swift       # 舊版（保留）
```

---

## 實作步驟

### Step 0: Feature Flag ✅
- 建立 `CodeConverterConfig.swift`
- 使用 `@Persisted` 存儲到 UserDefaults
- DEBUG mode 可強制開啟

### Step 1: WidgetInputState ✅
- 定義輸入框的視覺狀態 enum
- Cases: default, focus, typing, filled, loading, error

### Step 2: State/Action 定義 ✅
- 定義 TCA State 與 Action
- 整合到 `CodeConverterWidget+Feature.swift`

### Step 3: Reducer 實作 ✅
- 複用 `LoadCodeManager` 處理 API
- 處理輸入、提交、錯誤等 Action

### Step 4: View 實作 ✅
- SwiftUI View 對應 Figma 設計
- 包含 TextField、Import Button、Info Icon、Error Message

### Step 5: Tooltip Storage ✅
- 一次性 tooltip 顯示邏輯
- UserDefaults 儲存已顯示狀態

### Step 6: HomeListView 整合 ✅
- 根據 Feature Flag 切換新舊 UI
- Guide Dialog 使用 FCDialog overlay

### Step 7: Code Center 整合 ✅
- Dependency Injection 模式
- 返回 `CodeConverterWidgetViews` struct
- Dialog overlay 加在 CodeCenterContainerView 根層級

#### 架構決策（TCA + Clean Architecture）

```swift
// ✅ 符合 TCA：使用 Effect 隔離 side effects
Reduce { state, action in
    case .bookingCodeLoaded(let result):
        return .run { _ in  // Side effects 在 Effect 中
            await addSelectionsToBetslip(result)
            await presentBetslipViewController()
        }
}
```

**為什麼符合架構：**
1. **Single Source of Truth**: State 只存在於 Store
2. **Unidirectional Data Flow**: View → Action → Reducer → State → View
3. **Pure Reducer**: Reducer 本身是純函數，side effects 在 `.run` Effect 中
4. **Dependency Injection**: 通過 `CodeCenterDependencies` 注入，模組間解耦

### Step 8: Betslip 整合 🚧 進行中

**目標**: 替換 `BetslipViewController` 中的 `LoadCodeViewController`

**新建檔案**:
- `FCom/Betslip/Main/BetslipCodeConverterIntegration.swift`

**修改檔案**:
- `FCom/Betslip/Main/BetslipViewController.swift`

**整合方式**:
```swift
// BetslipCodeConverterConfig
struct BetslipCodeConverterConfig {
    let onHeightChange: (CGFloat) -> Void
    let onBookingCodeLoaded: (LoadCodeModel.CodeResult) -> Void
    let onDismiss: () -> Void
}

// 創建 Views
static func createViews(config: BetslipCodeConverterConfig) -> BetslipCodeConverterViews
```

> ⚠️ **重要提醒**：
> 當從 stash pop 出 Step 8 的改動後，需要 **手動在 Xcode 中加入以下檔案**：
> 
> ```
> FCom/Betslip/Main/BetslipCodeConverterIntegration.swift
> ```
> 
> **步驟**：
> 1. 在 Xcode 中找到 `FCom/Betslip/Main/` 資料夾
> 2. 右鍵 → Add Files to "FCom"...
> 3. 選擇 `BetslipCodeConverterIntegration.swift`
> 4. 確保 Target 勾選 FCom

**Stash 命令**:
```bash
# Pop stash
git stash pop "stash@{0}"

# 或查看 stash list
git stash list
```

### Step 9: Deep Link 整合（待規劃）

**目標**: 替換 `CurrentTabRouter` 中的 `LoadCodeViewController`

---

## 驗收 Checklist

### UI States
- [ ] Default 狀態
- [ ] Focus 狀態（藍框）
- [ ] Typing 狀態（顯示清除按鈕）
- [ ] Loading 狀態（Spinner）
- [ ] Error 狀態（紅框 + 錯誤訊息）

### Interactions
- [ ] 輸入過濾（只允許英數）
- [ ] Import 按鈕 enable/disable
- [ ] Clear 按鈕功能
- [ ] Info icon → Guide Dialog
- [ ] Tooltip 一次性顯示

### Design
- [ ] 顏色、字體、間距對應 Figma
- [ ] Dialog 置中 + 背景蒙版

### Feature Flag
- [ ] 開啟時顯示新 UI
- [ ] 關閉時顯示舊 UI

---

## 注意事項

1. **LoadCodeManager 複用**: 不要重新實作 API 邏輯
2. **錯誤處理**: 使用 `manager.mapErrorToMessage(error)`
3. **Guide Dialog**: 使用 `FCDialog`，不是 `GuideDialogView`
4. **Tooltip Overlay**: 需要 `.tooltipOverlay()` modifier
5. **不要刪除舊檔案**: `LoadBookingCodeSectionView` 等保留

---

## 風險評估

| 風險 | 等級 | 緩解方案 |
|------|------|----------|
| Feature Flag 失效 | 低 | 預設 false，漸進開啟 |
| 新舊 UI 行為不一致 | 中 | 複用 LoadCodeManager |
| Xcode project 衝突 | 低 | 手動加入檔案提醒 |

---

## 時間預估

- Step 0-6: ✅ 已完成
- Step 7: ✅ 已完成
- Step 8: 🚧 進行中（stash 狀態）
- Step 9: ⏳ 待規劃

**總預估**: 4-4.5 天
