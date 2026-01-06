# View Implementation: 復用策略詳解

## 復用策略總覽

```
┌────────────────────────────────────────────────────────────────────────┐
│                   LoadCodeWidgetView 復用策略                          │
├────────────────────────────────────────────────────────────────────────┤
│  核心原則：最大化復用 LoadBookingCodeSectionView 的結構               │
│                                                                        │
│  1. 保持原有 API 相容性（不破壞現有呼叫方）                           │
│  2. 新功能以 optional flag 方式加入                                   │
│  3. 擴展子元件而非重寫                                                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 現有 vs 新增對照

### LoadBookingCodeSectionView → LoadCodeWidgetView

```swift
// 現有
struct LoadBookingCodeSectionView: View {
    let store: StoreOf<LoadBookingCodeSection.Feature>
    @FocusState private var isTextFieldFocused: Bool

    var body: some View {
        VStack(spacing: 0) {
            HStack(spacing: 8) {
                CountryDropdownView(...)      // ← 復用，擴展為 BookieDropdown
                BookingCodeInputView(...)     // ← 復用，增加狀態
            }
        }
    }
}

// 新增（擴展）
struct LoadCodeWidgetView: View {
    let store: StoreOf<LoadCodeWidget.Feature>
    @FocusState private var isTextFieldFocused: Bool
    
    var body: some View {
        WithPerceptionTracking {
            VStack(spacing: 0) {
                // 主要輸入區
                HStack(spacing: 8) {
                    BookieDropdownView(...)     // ← 擴展自 CountryDropdownView
                    BookingCodeInputView(...)   // ← 擴展，增加狀態
                }
                
                // 新增：Loading 提示文字
                if let hintText = store.loadingHintText {
                    LoadingHintView(text: hintText)
                }
                
                // 新增：錯誤訊息
                if let errorMessage = store.errorMessage {
                    ErrorMessageView(message: errorMessage)
                }
            }
            .sheet(isPresented: $store.isBookieSelectorPresented.sending(\.bookieSelectorDismissed)) {
                BookieSelectorSheet(...)       // ← 新增
            }
        }
    }
}
```

---

## 子元件變更詳解

### 1. CountryDropdownView → BookieDropdownView

| 屬性 | 原有 | 新增 |
|------|------|------|
| 顯示文字 | `selectedCountry.description` | `selectedBookie.displayText` |
| 點擊行為 | Menu 選擇 | 開啟 Sheet |
| 箭頭圖示 | chevron.down | chevron.down |

```swift
// 原有
private struct CountryDropdownView: View {
    let selectedCountry: Region
    let availableCountries: [Region]
    let onSelection: (Region) -> Void

    var body: some View {
        Menu {
            ForEach(availableCountries, id: \.self) { country in
                Button(country.description) {
                    onSelection(country)
                }
            }
        } label: {
            HStack(spacing: 8) {
                Text(selectedCountry.description)
                Spacer()
                Image(systemName: "chevron.down")
            }
        }
    }
}

// 新增（擴展）
private struct BookieDropdownView: View {
    let selectedBookie: SelectedBookie?
    let enableCodeConverter: Bool
    let selectedCountry: Region  // 向後相容
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 8) {
                // 根據 enableCodeConverter 決定顯示內容
                if enableCodeConverter, let bookie = selectedBookie {
                    // 新功能：顯示 Bookie + Country
                    VStack(alignment: .leading, spacing: 2) {
                        Text(bookie.name)
                            .font(.system(size: 12))
                            .lineLimit(1)
                        Text(bookie.country.displayName)
                            .font(.system(size: 10))
                            .foregroundColor(.secondary)
                    }
                } else {
                    // 向後相容：只顯示 Country
                    Text(selectedCountry.description)
                        .font(.system(size: 12))
                }
                
                Spacer()
                
                Image(systemName: "chevron.down")
                    .font(.system(size: 10))
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(Color.backgroundType1Secondary)
        )
    }
}
```

---

### 2. BookingCodeInputView 擴展

| 功能 | 原有 | 新增 |
|------|------|------|
| Focus 綠色邊框 | ✅ | ✅ |
| Loading Spinner | ✅ | ✅ |
| Error 紅色邊框 | ❌ | ✅ |
| 清除按鈕 ⊗ | ❌ | ✅ |
| Load 按鈕顏色 | 固定 | 動態（綠/灰） |

```swift
// 擴展後
private struct BookingCodeInputView: View {
    let bookingCode: String
    let inputState: WidgetInputState
    var isTextFieldFocused: FocusState<Bool>.Binding
    let onTextChange: (String) -> Void
    let onSubmit: () -> Void
    let onClear: () -> Void
    let onFocus: () -> Void
    let onBlur: () -> Void

    var body: some View {
        ZStack {
            // 背景
            RoundedRectangle(cornerRadius: 10)
                .fill(Color.backgroundType1Secondary)
            
            HStack(spacing: 8) {
                // 輸入框
                TextField("Booking Code", text: .init(
                    get: { bookingCode },
                    set: { onTextChange($0) }
                ))
                .font(.system(size: 14))
                .textFieldStyle(PlainTextFieldStyle())
                .focused(isTextFieldFocused)
                .tint(.brandSecondary)
                .onSubmit {
                    onSubmit()
                    isTextFieldFocused.wrappedValue = false
                }
                .onChange(of: isTextFieldFocused.wrappedValue) { newValue in
                    if newValue {
                        onFocus()
                    } else {
                        onBlur()
                    }
                }
                .submitLabel(.done)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .padding(.leading, 16)
                
                Spacer(minLength: 0)
                
                // 清除按鈕（新增）
                if inputState.showClearButton {
                    Button(action: onClear) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.gray)
                    }
                }
                
                // Load 按鈕 / Spinner
                if inputState == .loading {
                    ProgressView()
                        .scaleEffect(0.8)
                        .padding(.trailing, 8)
                } else {
                    Button(action: onSubmit) {
                        Text("Load")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(inputState.isLoadButtonEnabled ? .black : .gray)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 6)
                                    .fill(inputState.isLoadButtonEnabled ? Color.brandSecondary : Color.gray.opacity(0.3))
                            )
                    }
                    .disabled(!inputState.isLoadButtonEnabled)
                    .padding(.trailing, 8)
                }
            }
        }
        // 邊框顏色（根據狀態）
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(borderColor, lineWidth: 2)
        )
    }
    
    private var borderColor: Color {
        if inputState.showErrorBorder {
            return .red
        } else if inputState.showFocusBorder {
            return .brandSecondary
        }
        return .clear
    }
}
```

---

### 3. 新增元件

#### LoadingHintView

```swift
private struct LoadingHintView: View {
    let text: String
    
    var body: some View {
        Text(text)
            .font(.system(size: 12))
            .foregroundColor(.secondary)
            .multilineTextAlignment(.leading)
            .padding(.top, 8)
            .padding(.horizontal, 8)
    }
}
```

#### ErrorMessageView

```swift
private struct ErrorMessageView: View {
    let message: String
    
    var body: some View {
        Text(message)
            .font(.system(size: 12))
            .foregroundColor(.red)
            .multilineTextAlignment(.leading)
            .padding(.top, 8)
            .padding(.horizontal, 8)
    }
}
```

---

## 向後相容性保證

### 1. Feature 初始化相容

```swift
// 原有呼叫方式仍然有效
let store = Store(initialState: LoadCodeWidget.State()) {
    LoadCodeWidget.Feature()
}

// 新功能呼叫方式
let store = Store(initialState: LoadCodeWidget.State(enableCodeConverter: true)) {
    LoadCodeWidget.Feature()
}
```

### 2. State 預設值

所有新增屬性都有合理的預設值，不影響原有邏輯：

```swift
extension LoadCodeWidget.State {
    init(
        // 原有（保持預設）
        bookingCode: String = "",
        selectedCountry: Region = .current,
        isLoading: Bool = false,
        contentState: SectionContentState = .loaded,
        availableCountries: [Region] = [.ghana, .nigeria],
        
        // 新增（預設關閉）
        enableCodeConverter: Bool = false,  // ← 預設關閉！
        selectedBookie: SelectedBookie? = nil,
        providerConfigs: [ProviderConfig] = [],
        inputState: WidgetInputState = .default,
        isBookieSelectorPresented: Bool = false,
        errorMessage: String? = nil,
        convertResult: ConvertResult? = nil
    )
}
```

### 3. 漸進式遷移

| 入口點 | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| 首頁 Widget | `enableCodeConverter = true` | 完成 | 完成 |
| Code Center | 暫用舊元件 | 替換為新元件 | 移除舊元件 |
| Betslip | 暫用舊元件 | 替換為新元件 | 移除舊元件 |

