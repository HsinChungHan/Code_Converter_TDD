# Phase 1 - Code Converter 實作指南

> 此文件為 View Layer 的實作步驟與程式碼範本

---

## 📁 檔案結構

```
FCom/
├── Features/
│   └── CodeConverter/
│       ├── Views/
│       │   ├── LoadCodeWidget.swift
│       │   ├── BookieDropdown.swift
│       │   ├── CodeInputField.swift
│       │   ├── LoadButton.swift
│       │   └── BookieSelectorBottomSheet.swift
│       ├── ViewModels/
│       │   └── LoadCodeViewModel.swift
│       ├── Models/
│       │   ├── LoadCodeState.swift
│       │   └── Bookie.swift
│       └── Components/
│           ├── BookieRow.swift
│           └── CountryChip.swift
```

---

## 🎨 1. Load Code Widget States

### 1.1 State Enum 定義

```swift
// LoadCodeState.swift

import Foundation

/// Load Code Widget 的所有狀態
enum LoadCodeInputState: Equatable {
    case `default`      // 預設狀態
    case focus          // 輸入框聚焦
    case typing         // 正在輸入
    case filled         // 已填入完成
    case loading        // 轉換中
    case error(String)  // 錯誤狀態
}

extension LoadCodeInputState {
    /// 是否顯示清除按鈕
    var showClearButton: Bool {
        switch self {
        case .typing, .filled:
            return true
        default:
            return false
        }
    }
    
    /// Load 按鈕是否啟用
    var isLoadButtonEnabled: Bool {
        switch self {
        case .typing, .filled:
            return true
        default:
            return false
        }
    }
    
    /// 是否顯示 Loading 提示
    var isLoading: Bool {
        if case .loading = self { return true }
        return false
    }
}
```

### 1.2 LoadCodeWidget 主元件

```swift
// LoadCodeWidget.swift

import SwiftUI
import DesignSystem

struct LoadCodeWidget: View {
    @StateObject private var viewModel = LoadCodeViewModel()
    
    var body: some View {
        VStack(spacing: 0) {
            // Main Input Row
            HStack(spacing: 8) {
                // Bookie Dropdown
                BookieDropdown(
                    selectedBookie: viewModel.selectedBookie,
                    onTap: viewModel.showBookieSelector
                )
                
                // Input Container
                CodeInputField(
                    text: $viewModel.bookingCode,
                    state: viewModel.inputState,
                    onClear: viewModel.clearInput,
                    onSubmit: viewModel.loadCode
                )
                
                // Load Button
                LoadButton(
                    isEnabled: viewModel.inputState.isLoadButtonEnabled,
                    isLoading: viewModel.inputState.isLoading,
                    onTap: viewModel.loadCode
                )
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.backgroundType1Secondary)
            .cornerRadius(8)
            
            // Error Message (if any)
            if case .error(let message) = viewModel.inputState {
                Text(message)
                    .font(.b2_r)
                    .foregroundColor(.warningPrimary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 16)
                    .padding(.top, 8)
            }
            
            // Loading Hint
            if viewModel.inputState.isLoading {
                Text("Conversion may take up to 10 seconds...")
                    .font(.b2_r)
                    .foregroundColor(.textType1Secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 16)
                    .padding(.top, 8)
            }
        }
    }
}

// MARK: - Preview

#Preview("Default") {
    LoadCodeWidget_Preview(state: .default)
}

#Preview("Focus") {
    LoadCodeWidget_Preview(state: .focus)
}

#Preview("Typing") {
    LoadCodeWidget_Preview(state: .typing)
}

#Preview("Filled") {
    LoadCodeWidget_Preview(state: .filled)
}

#Preview("Loading") {
    LoadCodeWidget_Preview(state: .loading)
}

#Preview("Error") {
    LoadCodeWidget_Preview(state: .error("We couldn't find this booking code. Please check and try again."))
}

// Preview Helper
private struct LoadCodeWidget_Preview: View {
    let state: LoadCodeInputState
    
    var body: some View {
        ZStack {
            Color.backgroundType1Primary.ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Mock Widget based on state
                VStack(spacing: 0) {
                    HStack(spacing: 8) {
                        // Bookie Dropdown
                        HStack(spacing: 4) {
                            Text("F.com")
                                .font(.b1_m)
                                .foregroundColor(.textType1Primary)
                            Image(systemName: "chevron.down")
                                .font(.system(size: 12))
                                .foregroundColor(.textType1Secondary)
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(Color.backgroundType1Tertiary)
                        .cornerRadius(8)
                        
                        // Input Field
                        HStack(spacing: 8) {
                            Group {
                                switch state {
                                case .default:
                                    Text("Booking Code")
                                        .foregroundColor(.textType1Secondary)
                                case .focus:
                                    HStack(spacing: 0) {
                                        Text("Booking Code")
                                            .foregroundColor(.textType1Secondary)
                                        Rectangle()
                                            .fill(Color.brandSecondary)
                                            .frame(width: 2, height: 16)
                                    }
                                case .typing, .filled:
                                    HStack {
                                        Text("3RA3FA")
                                            .foregroundColor(.textType1Primary)
                                        Spacer()
                                        Image(systemName: "xmark.circle.fill")
                                            .foregroundColor(.textType1Secondary)
                                    }
                                case .loading:
                                    Text("Converting...")
                                        .foregroundColor(.textType1Secondary)
                                case .error:
                                    Text("3RA3FA")
                                        .foregroundColor(.textType1Primary)
                                }
                            }
                            .font(.b1_r)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 10)
                        .background(Color.backgroundType1Tertiary)
                        .cornerRadius(8)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(
                                    state == .focus ? Color.brandSecondary : Color.clear,
                                    lineWidth: 1
                                )
                        )
                        
                        // Load Button
                        Text("Load")
                            .font(.b1_b)
                            .foregroundColor(
                                state.isLoadButtonEnabled 
                                    ? Color.brandTertiary 
                                    : Color.textDisableType1Primary
                            )
                            .padding(.horizontal, 16)
                            .padding(.vertical, 10)
                            .background(
                                state.isLoadButtonEnabled 
                                    ? Color.brandSecondary 
                                    : Color.brandSecondaryDisable
                            )
                            .cornerRadius(8)
                    }
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(Color.backgroundType1Secondary)
                    .cornerRadius(8)
                    
                    // Error/Loading Message
                    if case .error(let message) = state {
                        Text(message)
                            .font(.b2_r)
                            .foregroundColor(.warningPrimary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal, 16)
                            .padding(.top, 8)
                    }
                    
                    if state.isLoading {
                        Text("Conversion may take up to 10 seconds...")
                            .font(.b2_r)
                            .foregroundColor(.textType1Secondary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal, 16)
                            .padding(.top, 8)
                    }
                }
                .padding(16)
            }
        }
    }
}
```

---

## 🎨 2. Bookie Dropdown

### 2.1 BookieDropdown 元件

```swift
// BookieDropdown.swift

import SwiftUI
import DesignSystem

struct BookieDropdown: View {
    let selectedBookie: Bookie?
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 4) {
                // Bookie Name
                Text(selectedBookie?.displayName ?? "Select")
                    .font(.b1_m)
                    .foregroundColor(.textType1Primary)
                
                // Country (if multi-country)
                if let country = selectedBookie?.selectedCountry {
                    Text(country)
                        .font(.b2_m)
                        .foregroundColor(.textType1Secondary)
                }
                
                // Dropdown Arrow
                Image(systemName: "chevron.down")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.textType1Secondary)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color.backgroundType1Tertiary)
            .cornerRadius(8)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Preview

#Preview("Default - F.com") {
    BookieDropdown_Preview(
        bookie: Bookie(name: "F.com", countries: nil)
    )
}

#Preview("With Country - Bet9ja NG") {
    BookieDropdown_Preview(
        bookie: Bookie(name: "Bet9ja", countries: ["NG", "KE"], selectedCountry: "NG")
    )
}

#Preview("No Selection") {
    BookieDropdown_Preview(bookie: nil)
}

private struct BookieDropdown_Preview: View {
    let bookie: Bookie?
    
    var body: some View {
        ZStack {
            Color.backgroundType1Primary.ignoresSafeArea()
            
            BookieDropdown(
                selectedBookie: bookie,
                onTap: {}
            )
        }
    }
}
```

---

## 🎨 3. Code Input Field

### 3.1 CodeInputField 元件

```swift
// CodeInputField.swift

import SwiftUI
import DesignSystem

struct CodeInputField: View {
    @Binding var text: String
    let state: LoadCodeInputState
    let onClear: () -> Void
    let onSubmit: () -> Void
    
    @FocusState private var isFocused: Bool
    
    var body: some View {
        HStack(spacing: 8) {
            // Text Field
            TextField("Booking Code", text: $text)
                .font(.b1_r)
                .foregroundColor(.textType1Primary)
                .focused($isFocused)
                .disabled(state.isLoading)
                .onSubmit(onSubmit)
            
            // Clear Button
            if state.showClearButton && !text.isEmpty {
                Button(action: onClear) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.system(size: 16))
                        .foregroundColor(.textType1Secondary)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
        .background(Color.backgroundType1Tertiary)
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(
                    isFocused ? Color.brandSecondary : Color.clear,
                    lineWidth: 1
                )
        )
    }
}

// MARK: - Preview

#Preview("Default - Empty") {
    CodeInputField_Preview(text: "", state: .default)
}

#Preview("Focus - With Cursor") {
    CodeInputField_Preview(text: "", state: .focus)
}

#Preview("Typing") {
    CodeInputField_Preview(text: "3RA3FA", state: .typing)
}

#Preview("Loading") {
    CodeInputField_Preview(text: "3RA3FA", state: .loading)
}

private struct CodeInputField_Preview: View {
    @State var text: String
    let state: LoadCodeInputState
    
    var body: some View {
        ZStack {
            Color.backgroundType1Primary.ignoresSafeArea()
            
            CodeInputField(
                text: $text,
                state: state,
                onClear: { text = "" },
                onSubmit: {}
            )
            .padding()
        }
    }
}
```

---

## 🎨 4. Load Button

### 4.1 LoadButton 元件

```swift
// LoadButton.swift

import SwiftUI
import DesignSystem

struct LoadButton: View {
    let isEnabled: Bool
    let isLoading: Bool
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            Group {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .brandTertiary))
                        .scaleEffect(0.8)
                } else {
                    Text("Load")
                        .font(.b1_b)
                }
            }
            .foregroundColor(isEnabled ? .brandTertiary : .textDisableType1Primary)
            .frame(width: 56, height: 36)
            .background(isEnabled ? Color.brandSecondary : Color.brandSecondaryDisable)
            .cornerRadius(8)
        }
        .buttonStyle(.plain)
        .disabled(!isEnabled || isLoading)
    }
}

// MARK: - Preview

#Preview("Disabled") {
    LoadButton_Preview(isEnabled: false, isLoading: false)
}

#Preview("Enabled") {
    LoadButton_Preview(isEnabled: true, isLoading: false)
}

#Preview("Loading") {
    LoadButton_Preview(isEnabled: true, isLoading: true)
}

private struct LoadButton_Preview: View {
    let isEnabled: Bool
    let isLoading: Bool
    
    var body: some View {
        ZStack {
            Color.backgroundType1Primary.ignoresSafeArea()
            
            LoadButton(
                isEnabled: isEnabled,
                isLoading: isLoading,
                onTap: {}
            )
        }
    }
}
```

---

## 🎨 5. Bookie Selector Bottom Sheet

### 5.1 BookieSelectorBottomSheet 元件

```swift
// BookieSelectorBottomSheet.swift

import SwiftUI
import DesignSystem

struct BookieSelectorBottomSheet: View {
    @Binding var isPresented: Bool
    @Binding var selectedBookie: Bookie?
    let bookies: [Bookie]
    
    @State private var expandedBookie: Bookie?
    
    var body: some View {
        VStack(spacing: 0) {
            // Handle Bar
            Capsule()
                .fill(Color.lineType1Secondary)
                .frame(width: 36, height: 4)
                .padding(.top, 8)
            
            // Title
            Text("Select bookie")
                .font(.h4_r)
                .foregroundColor(.textType1Primary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 16)
                .padding(.vertical, 16)
            
            // Divider
            Divider()
                .background(Color.lineType1Primary)
            
            // Bookie List
            ScrollView {
                LazyVStack(spacing: 0) {
                    ForEach(bookies, id: \.name) { bookie in
                        BookieRow(
                            bookie: bookie,
                            isExpanded: expandedBookie?.name == bookie.name,
                            isSelected: selectedBookie?.name == bookie.name,
                            onTap: {
                                handleBookieTap(bookie)
                            },
                            onCountrySelect: { country in
                                handleCountrySelect(bookie, country: country)
                            }
                        )
                    }
                }
            }
            .scrollFadeMask(
                topColor: .brandTertiary,
                bottomColor: .brandTertiary
            )
        }
        .background(Color.brandTertiary)
        .cornerRadius(16, corners: [.topLeft, .topRight])
    }
    
    private func handleBookieTap(_ bookie: Bookie) {
        if bookie.hasMultipleCountries {
            // Toggle expand
            withAnimation(.easeInOut(duration: 0.2)) {
                expandedBookie = expandedBookie?.name == bookie.name ? nil : bookie
            }
        } else {
            // Direct select
            selectedBookie = bookie
            isPresented = false
        }
    }
    
    private func handleCountrySelect(_ bookie: Bookie, country: String) {
        var selected = bookie
        selected.selectedCountry = country
        selectedBookie = selected
        isPresented = false
    }
}

// MARK: - Preview

#Preview("Bookie List") {
    BookieSelectorBottomSheet_Preview()
}

#Preview("With Country Expanded") {
    BookieSelectorBottomSheet_Preview(expandedBookie: "Bet9ja")
}

private struct BookieSelectorBottomSheet_Preview: View {
    @State private var isPresented = true
    @State private var selectedBookie: Bookie? = nil
    var expandedBookie: String? = nil
    
    let mockBookies: [Bookie] = [
        Bookie(name: "F.com", countries: nil),
        Bookie(name: "Bet9ja", countries: ["NG", "KE", "GH"]),
        Bookie(name: "SportyBet", countries: ["NG", "KE"]),
        Bookie(name: "1xBet", countries: nil),
        Bookie(name: "BetKing", countries: nil),
        Bookie(name: "NairaBet", countries: nil),
    ]
    
    var body: some View {
        ZStack {
            Color.backgroundType1Primary.ignoresSafeArea()
            
            VStack {
                Spacer()
                
                BookieSelectorBottomSheet(
                    isPresented: $isPresented,
                    selectedBookie: $selectedBookie,
                    bookies: mockBookies
                )
                .frame(height: 400)
            }
        }
    }
}
```

---

## 🎨 6. Bookie Row

### 6.1 BookieRow 元件

```swift
// BookieRow.swift

import SwiftUI
import DesignSystem

struct BookieRow: View {
    let bookie: Bookie
    let isExpanded: Bool
    let isSelected: Bool
    let onTap: () -> Void
    let onCountrySelect: (String) -> Void
    
    var body: some View {
        VStack(spacing: 0) {
            // Main Row
            Button(action: onTap) {
                HStack {
                    // Bookie Logo (placeholder)
                    Circle()
                        .fill(Color.backgroundType1Tertiary)
                        .frame(width: 32, height: 32)
                    
                    // Bookie Name
                    Text(bookie.name)
                        .font(.b1_m)
                        .foregroundColor(.textType1Primary)
                    
                    Spacer()
                    
                    // Expand Icon or Checkmark
                    if bookie.hasMultipleCountries {
                        Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(.textType1Secondary)
                    } else if isSelected {
                        Image(systemName: "checkmark")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(.brandSecondary)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(isSelected && !bookie.hasMultipleCountries 
                    ? Color.backgroundType1Tertiary 
                    : Color.clear)
            }
            .buttonStyle(.plain)
            
            // Country Chips (if expanded)
            if isExpanded, let countries = bookie.countries {
                HStack(spacing: 8) {
                    ForEach(countries, id: \.self) { country in
                        CountryChip(
                            country: country,
                            isSelected: bookie.selectedCountry == country,
                            onTap: { onCountrySelect(country) }
                        )
                    }
                    Spacer()
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 12)
            }
            
            // Divider
            Divider()
                .background(Color.lineType1Primary)
                .padding(.horizontal, 16)
        }
    }
}

// MARK: - Preview

#Preview("Single Country - Unselected") {
    BookieRow_Preview(
        bookie: Bookie(name: "F.com", countries: nil),
        isExpanded: false,
        isSelected: false
    )
}

#Preview("Single Country - Selected") {
    BookieRow_Preview(
        bookie: Bookie(name: "F.com", countries: nil),
        isExpanded: false,
        isSelected: true
    )
}

#Preview("Multi Country - Collapsed") {
    BookieRow_Preview(
        bookie: Bookie(name: "Bet9ja", countries: ["NG", "KE", "GH"]),
        isExpanded: false,
        isSelected: false
    )
}

#Preview("Multi Country - Expanded") {
    BookieRow_Preview(
        bookie: Bookie(name: "Bet9ja", countries: ["NG", "KE", "GH"]),
        isExpanded: true,
        isSelected: false
    )
}

private struct BookieRow_Preview: View {
    let bookie: Bookie
    let isExpanded: Bool
    let isSelected: Bool
    
    var body: some View {
        ZStack {
            Color.brandTertiary.ignoresSafeArea()
            
            BookieRow(
                bookie: bookie,
                isExpanded: isExpanded,
                isSelected: isSelected,
                onTap: {},
                onCountrySelect: { _ in }
            )
        }
    }
}
```

---

## 🎨 7. Country Chip

### 7.1 CountryChip 元件

```swift
// CountryChip.swift

import SwiftUI
import DesignSystem

struct CountryChip: View {
    let country: String
    let isSelected: Bool
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            Text(country)
                .font(.b2_m)
                .foregroundColor(isSelected ? .brandTertiary : .textType1Primary)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.brandSecondary : Color.backgroundType1Tertiary)
                .cornerRadius(16)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(
                            isSelected ? Color.clear : Color.lineType1Secondary,
                            lineWidth: 1
                        )
                )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Preview

#Preview("Unselected") {
    CountryChip_Preview(isSelected: false)
}

#Preview("Selected") {
    CountryChip_Preview(isSelected: true)
}

private struct CountryChip_Preview: View {
    let isSelected: Bool
    
    var body: some View {
        ZStack {
            Color.brandTertiary.ignoresSafeArea()
            
            CountryChip(
                country: "NG",
                isSelected: isSelected,
                onTap: {}
            )
        }
    }
}
```

---

## 📦 8. Model

### 8.1 Bookie Model

```swift
// Bookie.swift

import Foundation

struct Bookie: Equatable, Identifiable {
    var id: String { name }
    let name: String
    let countries: [String]?
    var selectedCountry: String?
    
    var displayName: String {
        name
    }
    
    var hasMultipleCountries: Bool {
        (countries?.count ?? 0) > 1
    }
    
    init(name: String, countries: [String]?, selectedCountry: String? = nil) {
        self.name = name
        self.countries = countries
        self.selectedCountry = selectedCountry ?? countries?.first
    }
}
```

---

## ✅ 實作 Checklist

### 元件開發順序

| # | 元件 | 狀態數 | Preview 數 | 優先級 |
|---|------|--------|-----------|--------|
| 1 | `LoadCodeState.swift` | - | - | 🔴 |
| 2 | `Bookie.swift` | - | - | 🔴 |
| 3 | `LoadButton.swift` | 3 | 3 | 🔴 |
| 4 | `CountryChip.swift` | 2 | 2 | 🟡 |
| 5 | `CodeInputField.swift` | 4 | 4 | 🔴 |
| 6 | `BookieDropdown.swift` | 3 | 3 | 🔴 |
| 7 | `BookieRow.swift` | 4 | 4 | 🟡 |
| 8 | `BookieSelectorBottomSheet.swift` | 2 | 2 | 🟡 |
| 9 | `LoadCodeWidget.swift` | 6 | 6 | 🔴 |

### Preview 總覽

| 元件 | Preview 名稱 |
|------|-------------|
| `LoadCodeWidget` | Default, Focus, Typing, Filled, Loading, Error |
| `BookieDropdown` | Default, With Country, No Selection |
| `CodeInputField` | Default - Empty, Focus - With Cursor, Typing, Loading |
| `LoadButton` | Disabled, Enabled, Loading |
| `BookieSelectorBottomSheet` | Bookie List, With Country Expanded |
| `BookieRow` | Single Country - Unselected/Selected, Multi Country - Collapsed/Expanded |
| `CountryChip` | Unselected, Selected |

---

## 🔗 Design Token 對照

### 顏色

| 用途 | Figma Token | Code |
|------|-------------|------|
| 主要 CTA | `brand/brand_secondary` | `Color.brandSecondary` |
| 禁用按鈕 | `brand/brand_secondary_disable` | `Color.brandSecondaryDisable` |
| 深色背景 | `brand/brand_tertiary` | `Color.brandTertiary` |
| 主要背景 | `background_type1_primary` | `Color.backgroundType1Primary` |
| 次要背景 | `background_type1_secondary` | `Color.backgroundType1Secondary` |
| 輸入框背景 | `background_type1_tertiary` | `Color.backgroundType1Tertiary` |
| 主要文字 | `text_type1_primary` | `Color.textType1Primary` |
| 次要文字 | `text_type1_secondary` | `Color.textType1Secondary` |
| 禁用文字 | `text_disable_type1_primary` | `Color.textDisableType1Primary` |
| 錯誤文字 | `warning_primary` | `Color.warningPrimary` |
| 分隔線 | `line_type1_primary` | `Color.lineType1Primary` |

### 字型

| 用途 | Figma | Code |
|------|-------|------|
| 按鈕文字 | Body 1 Bold | `.b1_b` |
| 輸入文字 | Body 1 Regular | `.b1_r` |
| Bookie 名稱 | Body 1 Medium | `.b1_m` |
| 提示文字 | Body 2 Regular | `.b2_r` |
| Country | Body 2 Medium | `.b2_m` |
| Sheet Title | Headline 4 Regular | `.h4_r` |

---

## 🚀 開始實作

1. 從 `LoadCodeState.swift` 和 `Bookie.swift` Model 開始
2. 實作最小元件：`LoadButton`, `CountryChip`
3. 實作輸入相關：`CodeInputField`, `BookieDropdown`
4. 組合成 `LoadCodeWidget`
5. 實作 Bottom Sheet：`BookieRow`, `BookieSelectorBottomSheet`
6. 每個元件完成後確認所有 Preview 正確顯示

