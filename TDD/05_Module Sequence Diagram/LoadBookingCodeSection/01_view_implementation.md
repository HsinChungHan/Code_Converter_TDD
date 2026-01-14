# View Implementation: 復用策略詳解

## ⚠️ BE 新設計更新 (2025-01-14)

| 變更項目 | 說明 |
|----------|------|
| **BookieDropdownView 移除** | 不再需要 Bookie Dropdown |
| **BookieSelectorSheet 移除** | 不再需要 Bookie 選擇器 |
| **TooltipView 新增** | 首次使用時顯示引導 Tooltip |
| **Widget 結構簡化** | 只包含輸入框 + Load 按鈕 |

---

## 復用策略總覽

```
┌────────────────────────────────────────────────────────────────────────┐
│                   LoadCodeWidgetView 復用策略（簡化版）                 │
├────────────────────────────────────────────────────────────────────────┤
│  核心原則：最大化復用 LoadBookingCodeSectionView 的結構               │
│                                                                        │
│  1. 保持原有 API 相容性（不破壞現有呼叫方）                           │
│  2. 新功能以 optional flag 方式加入                                   │
│  3. 簡化結構：移除 Bookie Dropdown                                    │
│  4. 新增 Tooltip 元件                                                 │
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
                CountryDropdownView(...)      // ← 移除
                BookingCodeInputView(...)     // ← 復用，增加狀態
            }
        }
    }
}

// 新增（簡化版）
struct LoadCodeWidgetView: View {
    let store: StoreOf<LoadCodeWidget.Feature>
    @FocusState private var isTextFieldFocused: Bool
    
    var body: some View {
        WithPerceptionTracking {
            ZStack(alignment: .top) {
                VStack(spacing: 0) {
                    // 主要輸入區（簡化：只有輸入框）
                    BookingCodeInputView(...)   // ← 擴展，增加狀態
                    
                    // Loading 提示文字
                    if let hintText = store.loadingHintText {
                        LoadingHintView(text: hintText)
                    }
                    
                    // 錯誤訊息
                    if let errorMessage = store.errorMessage {
                        ErrorMessageView(message: errorMessage)
                    }
                }
                
                // Tooltip（首次使用時顯示）
                if store.isTooltipVisible {
                    TooltipView(onDismiss: {
                        store.send(.tooltipDismissed)
                    })
                    .offset(y: -50)
                }
            }
        }
    }
}
```

---

## 子元件變更詳解

### ~~1. CountryDropdownView → BookieDropdownView~~ ❌ 已廢棄

> **不再需要**：BE 新設計不需要選擇 Provider/Country

---

### 1. BookingCodeInputView 擴展

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
                
                // 清除按鈕
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
                .stroke(borderColor, lineWidth: inputState.showErrorBorder ? 1 : 2)
        )
    }
    
    private var borderColor: Color {
        if inputState.showErrorBorder {
            return .warningPrimary
        } else if inputState.showFocusBorder {
            return .brandSecondary
        }
        return .clear
    }
}
```

---

### 2. 新增元件

#### TooltipView

```swift
private struct TooltipView: View {
    let onDismiss: () -> Void
    
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: "lightbulb.fill")
                .foregroundColor(.yellow)
                .font(.system(size: 14))
            
            Text("Insert a booking code from any provider")
                .font(.system(size: 12))
                .foregroundColor(.white)
            
            Spacer()
            
            Button(action: onDismiss) {
                Image(systemName: "xmark")
                    .foregroundColor(.white.opacity(0.7))
                    .font(.system(size: 12))
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.black.opacity(0.85))
        )
        .shadow(color: .black.opacity(0.2), radius: 8, x: 0, y: 4)
    }
}
```

#### LoadingHintView

```swift
private struct LoadingHintView: View {
    let text: String
    
    var body: some View {
        Text(text)
            .font(.system(size: 12))
            .foregroundColor(.textType1Primary)
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
            .foregroundColor(.warningPrimary)
            .multilineTextAlignment(.leading)
            .padding(.top, 8)
            .padding(.horizontal, 8)
    }
}
```

---

## 完整 View 結構（簡化版）

```swift
struct LoadCodeWidgetView: View {
    @Perception.Bindable var store: StoreOf<LoadCodeWidget.Feature>
    @FocusState private var isTextFieldFocused: Bool
    
    var body: some View {
        WithPerceptionTracking {
            ZStack(alignment: .top) {
                // 主要 Widget
                VStack(spacing: 0) {
                    // 背景容器
                    HStack(spacing: 8) {
                        BookingCodeInputView(
                            bookingCode: store.bookingCode,
                            inputState: store.inputState,
                            isTextFieldFocused: $isTextFieldFocused,
                            onTextChange: { store.send(.bookingCodeChanged($0)) },
                            onSubmit: { store.send(.loadBookingCode) },
                            onClear: { store.send(.clearButtonTapped) },
                            onFocus: { store.send(.inputFocused) },
                            onBlur: { store.send(.inputBlurred) }
                        )
                    }
                    .padding(8)
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color.backgroundType1Tertiary)
                    )
                    
                    // Loading 提示
                    if let hintText = store.loadingHintText {
                        LoadingHintView(text: hintText)
                    }
                    
                    // 錯誤訊息
                    if let errorMessage = store.errorMessage {
                        ErrorMessageView(message: errorMessage)
                    }
                }
                
                // Tooltip
                if store.isTooltipVisible {
                    TooltipView(onDismiss: {
                        store.send(.tooltipDismissed)
                    })
                    .padding(.horizontal, 8)
                    .offset(y: -60)
                    .transition(.opacity.combined(with: .move(edge: .top)))
                }
            }
            .animation(.easeInOut(duration: 0.2), value: store.isTooltipVisible)
            .onAppear {
                store.send(.onAppear)
            }
        }
    }
}
```

---

## 廢棄的元件

| 元件 | 原因 |
|------|------|
| ~~`BookieDropdownView`~~ | 不再需要選擇 Bookie |
| ~~`BookieSelectorSheet`~~ | 不再需要 Bookie 選擇器 |
| ~~`CountryDropdownView` 擴展~~ | 不再需要 Country 選擇 |

---

## Preview

```swift
#Preview("Default") {
    LoadCodeWidgetView(
        store: Store(initialState: LoadCodeWidget.State()) {
            LoadCodeWidget.Feature()
        }
    )
    .padding()
    .background(Color.backgroundType1Primary)
}

#Preview("With Tooltip") {
    LoadCodeWidgetView(
        store: Store(initialState: LoadCodeWidget.State(isTooltipVisible: true)) {
            LoadCodeWidget.Feature()
        }
    )
    .padding()
    .background(Color.backgroundType1Primary)
}

#Preview("Loading") {
    LoadCodeWidgetView(
        store: Store(initialState: LoadCodeWidget.State(
            bookingCode: "3RA3FA",
            inputState: .loading
        )) {
            LoadCodeWidget.Feature()
        }
    )
    .padding()
    .background(Color.backgroundType1Primary)
}

#Preview("Error") {
    LoadCodeWidgetView(
        store: Store(initialState: LoadCodeWidget.State(
            bookingCode: "INVALID",
            inputState: .error(message: "We couldn't find this booking code. Please check and try again."),
            errorMessage: "We couldn't find this booking code. Please check and try again."
        )) {
            LoadCodeWidget.Feature()
        }
    )
    .padding()
    .background(Color.backgroundType1Primary)
}
```
