# UI 層替換策略：LoadBookingCodeSectionView → LoadCodeViewController

> **版本**：01_09 (2025-01-09)  
> **變更原因**：需求調整，簡化 Bookie 選擇流程  
> **專注**：UI 層替換

---

## ⚠️ 與 TDD 舊版 (01_01) 的主要差異

| 項目 | 舊版 (01_01) | 新版 (01_09) | 影響 |
|------|--------------|--------------|------|
| **BookieDropdownView** | ✅ 需要 | ❌ 移除 | 不需實作 |
| **BookieSelectorSheet** | ✅ 需要 | ❌ 移除 | 不需實作 |
| **CountryDropdownView** | ✅ 需要 | ❌ 移除 | 不需擴展 |
| **Info Tip Icon** | ❌ 沒有 | ✅ 新增 | 需實作 |
| **按鈕文字** | "Load" | "Import" | 文字變更 |
| **Placeholder** | "Booking Code" | "Paste any booking code" | 文字變更 |
| **元件佈局** | HStack (Dropdown + Input) | 只有 Input Row | 結構簡化 |

---

## 📐 簡化後的元件結構 (01_09)

```
LoadBookingCodeSectionView
├── VStack
│   ├── Input Row (HStack)
│   │   ├── Input Container (ZStack)
│   │   │   ├── TextField (placeholder / 輸入文字)
│   │   │   ├── Clear Icon ⊗ (條件顯示)
│   │   │   └── Import Button / Loading Spinner
│   │   └── Info Tip Icon ⓘ (16px)
│   │
│   └── Helper Text (條件顯示)
│       ├── Loading: "Conversion may take up to 10 seconds..."
│       └── Error: "We couldn't find this booking code..."
└── (無 Sheet，已移除 Bookie Selector)
```

---

## 🔄 State 簡化（移除 Bookie 相關）

### 原有 State（01_01）
```swift
struct State: Equatable {
    // 原有
    var bookingCode: String = ""
    var selectedCountry: Region = .current      // ← 保留向後相容
    var isLoading: Bool = false
    
    // Code Converter (01_01)
    var enableCodeConverter: Bool = true
    var selectedBookie: SelectedBookie?         // ❌ 移除
    var providerConfigs: [ProviderConfig] = []  // ❌ 移除
    var inputState: WidgetInputState = .default // ✅ 保留
    var isBookieSelectorPresented: Bool = false // ❌ 移除
    var errorMessage: String?                   // ✅ 保留
}
```

### 簡化後 State（01_09）
```swift
@ObservableState
struct State: Equatable {
    // ========== 核心屬性 ==========
    var bookingCode: String = ""
    var inputState: WidgetInputState = .default
    var errorMessage: String?
    
    // ========== 向後相容（如有需要） ==========
    var isLoading: Bool = false
    var selectedCountry: Region = .current
    var enableCodeConverter: Bool = true
    
    // ========== 已移除 ==========
    // var selectedBookie: SelectedBookie?
    // var providerConfigs: [ProviderConfig] = []
    // var isBookieSelectorPresented: Bool = false
}
```

---

## 🎯 Action 簡化

### 需保留的 Action
```swift
enum Action: Equatable {
    // 原有（保持相容）
    case onAppear
    case bookingCodeChanged(String)
    case loadBookingCode
    case bookingCodeLoadFailed(String)
    case bookingCodeLoaded(LoadCodeModel.CodeResult)
    
    // 輸入相關
    case inputFocused
    case inputBlurred
    case clearButtonTapped
    case infoTipTapped          // 🆕 新增
    
    // Code Converter
    case convertCodeCompleted(Result<ConvertBookingCodeOutput, Error>)
    case presentBetslip(shareCode: String, failCnt: Int)
}
```

### 已移除的 Action
```swift
// ❌ 不再需要
// case bookieDropdownTapped
// case bookieSelectorDismissed
// case bookieSelected(provider: String, country: CountryCode)
// case providerConfigLoaded(Result<[ProviderConfig], Error>)
```

---

## 🧩 View 實作（簡化版）

### LoadBookingCodeSectionView.swift

```swift
struct LoadBookingCodeSectionView: View {
    let store: StoreOf<LoadBookingCodeSection.Feature>
    @FocusState private var isTextFieldFocused: Bool
    
    var body: some View {
        WithPerceptionTracking {
            VStack(spacing: 4) {
                // 主輸入區
                inputRow
                
                // Loading / Error 提示
                helperTextView
            }
            .padding(8)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.backgroundType1Tertiary) // #28263c
            )
        }
    }
    
    // MARK: - Input Row
    private var inputRow: some View {
        HStack(spacing: 8) {
            inputContainer
            infoTipIcon
        }
    }
    
    // MARK: - Input Container
    private var inputContainer: some View {
        HStack(spacing: 8) {
            // TextField
            TextField("Paste any booking code", text: $store.bookingCode.sending(\.bookingCodeChanged))
                .font(.custom("Roboto", size: 14))
                .foregroundColor(Color.textType1Primary)    // #e7e7e9
                .tint(Color.brandSecondary)                  // #9ff611
                .focused($isTextFieldFocused)
                .onSubmit { store.send(.loadBookingCode) }
                .onChange(of: isTextFieldFocused) { newValue in
                    store.send(newValue ? .inputFocused : .inputBlurred)
                }
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
            
            // Clear Button
            if store.inputState.showClearButton {
                Button { store.send(.clearButtonTapped) } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(Color.textType1Secondary) // #878693
                        .frame(width: 20, height: 20)
                }
            }
            
            // Import Button / Loading
            importButton
        }
        .padding(.horizontal, 12)
        .frame(height: 44)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(Color.backgroundType1Secondary) // #100e26
        )
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(borderColor, lineWidth: 2)
        )
    }
    
    // MARK: - Import Button
    @ViewBuilder
    private var importButton: some View {
        if store.inputState == .loading {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: Color.brandSecondary))
                .frame(width: 12, height: 12)
                .padding(.horizontal, 12)
        } else {
            Button { store.send(.loadBookingCode) } label: {
                Text("Import")
                    .font(.custom("Roboto-Medium", size: 12))
                    .foregroundColor(store.isImportButtonEnabled
                        ? Color.brandTertiary           // #100e26
                        : Color.textDisableType1Primary // #9c9bab
                    )
                    .padding(.horizontal, 12)
                    .frame(height: 28)
                    .background(
                        RoundedRectangle(cornerRadius: 2)
                            .fill(store.isImportButtonEnabled
                                ? Color.brandSecondary         // #9ff611
                                : Color.brandSecondaryDisable  // #343247
                            )
                    )
            }
            .disabled(!store.isImportButtonEnabled)
        }
    }
    
    // MARK: - Info Tip Icon
    private var infoTipIcon: some View {
        Button { store.send(.infoTipTapped) } label: {
            Image("icon/tip/1") // 或 systemName
                .foregroundColor(Color.textType1Secondary) // #878693
                .frame(width: 16, height: 16)
        }
    }
    
    // MARK: - Helper Text
    @ViewBuilder
    private var helperTextView: some View {
        if store.inputState == .loading {
            Text("Conversion may take up to 10 seconds, please stay here and wait for the result.")
                .font(.custom("Roboto", size: 12))
                .foregroundColor(Color.textType1Primary) // #e7e7e9
                .multilineTextAlignment(.leading)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.top, 4)
        }
        
        if let error = store.errorMessage {
            Text(error)
                .font(.custom("Roboto", size: 12))
                .foregroundColor(Color.warningPrimary) // #fb4d3d
                .multilineTextAlignment(.leading)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.top, 4)
        }
    }
    
    // MARK: - Border Color
    private var borderColor: Color {
        switch store.inputState {
        case .focus, .typing:
            return Color.brandSecondary  // #9ff611
        case .error:
            return Color.warningPrimary  // #fb4d3d
        default:
            return Color.clear
        }
    }
}
```

---

## 📋 Computed Properties（簡化版）

```swift
extension LoadBookingCodeSection.State {
    /// Import 按鈕是否啟用
    var isImportButtonEnabled: Bool {
        !bookingCode.isEmpty && inputState.isImportButtonEnabled
    }
    
    /// 是否顯示清除按鈕
    var showClearButton: Bool {
        !bookingCode.isEmpty && inputState.showClearButton
    }
}

extension WidgetInputState {
    var isImportButtonEnabled: Bool {
        switch self {
        case .typing, .filled, .error: return true
        default: return false
        }
    }
    
    var showClearButton: Bool {
        switch self {
        case .typing, .filled, .error: return true
        default: return false
        }
    }
}
```

---

## 🗑️ 可刪除的檔案/元件

| 檔案 | 原因 |
|------|------|
| `BookieDropdownView.swift` | 不需實作（已移除 Bookie Selector） |
| `BookieSelectorSheet.swift` | 不需實作（已移除 Bookie Selector） |
| `CountryDropdownView.swift` 擴展邏輯 | 不需擴展 |
| `LoadProviderConfigUseCase.swift` | 不需 Provider Config API |

---

## 🔄 替換 LoadCodeViewController 的步驟

### Phase 1: 擴展 LoadBookingCodeSectionView

```swift
// 1. 更新 BookingCodeInputView → 增加 6 種狀態
// 2. 新增 Info Tip Icon
// 3. 新增 Helper Text View (Loading / Error)
// 4. 更新按鈕文字 "Load" → "Import"
// 5. 更新 Placeholder 文字
```

### Phase 2: 更新 Feature (TCA)

```swift
// 1. State 增加 inputState, errorMessage
// 2. Action 增加 inputFocused, inputBlurred, clearButtonTapped, infoTipTapped
// 3. Reducer 增加狀態轉換邏輯
// 4. 移除 Bookie 相關邏輯
```

### Phase 3: 替換入口點

| 入口點 | 現有 | 替換為 |
|--------|------|--------|
| 首頁 Widget | `LoadBookingCodeSectionView` | 原地擴展 |
| Code Center | `LoadCodeViewWrapper` → `LoadCodeViewController` | `LoadBookingCodeSectionView` (UIHostingController) |
| Betslip Empty | 無 | 嵌入 `LoadBookingCodeSectionView` |

### Phase 4: 清理

```swift
// 1. 移除 LoadCodeViewController.swift  ✅ 可直接刪除
// 2. 移除 LoadCodeViewController.xib     ✅ 可直接刪除
// 3. 移除 LoadCodeViewWrapper.swift
```

> ⚠️ **確認**：`LoadCodeViewController.swift` 和 `LoadCodeViewController.xib` 可直接移除，無依賴問題

---

## 📐 Design Tokens 快速參考

```swift
extension Color {
    // Background
    static let backgroundType1Tertiary = Color(hex: "#28263c")
    static let backgroundType1Secondary = Color(hex: "#100e26")
    
    // Text
    static let textType1Primary = Color(hex: "#e7e7e9")
    static let textType1Secondary = Color(hex: "#878693")
    static let textDisableType1Primary = Color(hex: "#9c9bab")
    
    // Brand
    static let brandSecondary = Color(hex: "#9ff611")
    static let brandTertiary = Color(hex: "#100e26")
    static let brandSecondaryDisable = Color(hex: "#343247")
    
    // Warning
    static let warningPrimary = Color(hex: "#fb4d3d")
}
```

---

## 🆕 Info Icon → GuideDialog (2025-01-12 新增)

> 點擊 Info Icon (ⓘ) 彈出說明 Dialog

### Figma 資訊

| 項目 | 值 |
|------|-----|
| Frame node-id | `27536:81442` |
| Dialog node-id | `27536:84826` |
| 標題 | "Import Booking Code" |
| 內容 | Bullet list 說明 |
| 按鈕 | "Ok" |

### 復用現有 GuideDialog 元件

```swift
// 路徑: FComUI/Sources/FComUI/GuideDialog/

// 1. 定義 Action
case infoTipTapped  // 點擊 Info Icon

// 2. 在 Reducer 中處理
case .infoTipTapped:
    state.isGuideDialogPresented = true
    return .none

// 3. 在 View 中顯示 Dialog
.fullScreenCover(isPresented: $store.isGuideDialogPresented) {
    FComUIFactory.createGuideDialogView(
        viewState: .init(
            pages: [
                .init(
                    title: "Import Booking Code",
                    description: """
                    • Paste a booking code to load its selections into your betslip.
                    • Supports our codes and codes from other betting sites.
                    """,
                    contentSource: .image(.asset(name: ""))
                )
            ],
            finalButtonTitle: "Ok",
            theme: .init(
                backgroundStyle: .absoluteType1,
                titleStyle: .h3m,
                descriptionStyle: .h4r
            ),
            contentTopPadding: 0
        ),
        viewAction: .init(
            onDoneButtonTapped: {
                store.send(.guideDialogDismissed)
            }
        )
    )
}
```

### State 新增

```swift
// 新增 State 屬性
var isGuideDialogPresented: Bool = false
```

### Action 新增

```swift
// 新增 Action
case infoTipTapped
case guideDialogDismissed
```

---

## 🆕 One-Time Tooltip (2025-01-12 新增)

> Feature 上線後顯示一次性提示，按 device ID 存儲

### Figma 資訊

| 項目 | 值 |
|------|-----|
| Frame node-id | `27526:67890` |
| Tooltip node-id | `27526:71304` |
| 文字 | "Supports booking codes from many platforms" |
| 位置 | Widget 下方 (downLeading) |

### 復用現有 Tooltip 元件

```swift
// 路徑: FComUI/Sources/FComUI/Tooltip/

// 使用方式
import FComUI

struct SomeParentView: View {
    @State private var showTooltip = !CodeConverterTooltipStorage.hasShown
    @State private var widgetFrame: CGRect = .zero
    
    var body: some View {
        VStack {
            LoadBookingCodeSectionView(...)
                .showTooltip(config: Tooltip.TooltipSwiftUIConfig(
                    isPresented: $showTooltip,
                    anchorFrame: $widgetFrame,
                    placement: .downLeading,
                    description: "Supports booking codes from many platforms",
                    onClose: {
                        CodeConverterTooltipStorage.markAsShown()
                    },
                    duration: 0  // 不自動消失
                ))
        }
        .tooltipOverlay()  // 必須在外層加上
    }
}
```

### Tooltip 儲存邏輯

```swift
struct CodeConverterTooltipStorage {
    private static let key = "code_converter_tooltip_shown"
    
    static var hasShown: Bool {
        UserDefaults.standard.bool(forKey: key)
    }
    
    static func markAsShown() {
        UserDefaults.standard.set(true, forKey: key)
    }
}
```

### Tooltip 樣式 (已從 Figma 確認)

| 屬性 | 值 |
|------|-----|
| 背景色 | `#4d5fae` (hint_background_type1) |
| 文字色 | `#e7e7e9` |
| 字型 | Body/B2_R (Roboto Regular 12px) |
| 圓角 | 4px |
| Padding | 12px × 6px |
| 箭頭 | 向上，16×12px |

---

## ✅ 驗證 Checklist

- [ ] 6 種輸入狀態正確渲染 (Default, Focus, Typing, Filled, Loading, Error)
- [ ] Import 按鈕狀態正確 (啟用/禁用/Loading)
- [ ] Clear 按鈕條件顯示
- [ ] Info Tip Icon 點擊事件
- [ ] Helper Text 正確顯示 (Loading/Error)
- [ ] 邊框顏色正確 (綠色 Focus/Typing, 紅色 Error)
- [ ] Design Tokens 正確套用
- [ ] 替換 LoadCodeViewController 後功能正常
- [ ] **One-Time Tooltip** 首次顯示並正確儲存狀態 (2025-01-12 新增)
- [ ] **Info Icon → GuideDialog** 點擊彈出說明 Dialog (2025-01-12 新增)

---

## 🔗 相關 Figma Node ID

| 狀態 | node-id |
|------|---------|
| Default | `26769:88873` |
| Focus | `26769:88868` |
| Typing | `26769:88869` |
| Filled | `26769:88870` |
| Loading | `26769:88872` |
| Error | `26769:88871` |

---

*此文件根據 2025-01-09 Figma 設計更新*

