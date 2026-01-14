# Figma → DesignSystem Mapping

> **目的**：將 Figma 設計規格對應到 codebase 現有的 DesignSystem 顏色/樣式  
> **來源**：`DesignSystem/Sources/Colors/`

---

## 🎨 顏色對照表

### 品牌色 (Brand)

| Figma 變數 | Hex (Dark) | DesignSystem | SwiftUI 使用 |
|------------|------------|--------------|--------------|
| `brand/brand_secondary` | `#9FF611` | ✅ `Color.brandSecondary` | `.foregroundColor(.brandSecondary)` |
| `brand/brand_secondary_disable` | `#343247` | ✅ `Color.brandSecondaryDisable` | `.background(Color.brandSecondaryDisable)` |
| `brand/brand_tertiary` | `#100E26` | ✅ `Color.brandTertiary` | `.background(Color.brandTertiary)` |

### 背景色 (Background)

| Figma 變數 | Hex (Dark) | DesignSystem | SwiftUI 使用 |
|------------|------------|--------------|--------------|
| `background_type1_primary` | `#1C1A31` | ✅ `Color.backgroundType1Primary` | `.background(Color.backgroundType1Primary)` |
| `background_type1_secondary` | `#100E26` | ✅ `Color.backgroundType1Secondary` | `.background(Color.backgroundType1Secondary)` |
| `background_type1_tertiary` | `#28263C` | ✅ `Color.backgroundType1Tertiary` | `.background(Color.backgroundType1Tertiary)` |

### 文字色 (Text)

| Figma 變數 | Hex (Dark) | DesignSystem | SwiftUI 使用 |
|------------|------------|--------------|--------------|
| `text_type1_primary` | `#E7E7E9` | ✅ `Color.textType1Primary` | `.foregroundColor(.textType1Primary)` |
| `text_type1_secondary` | `#878693` | ✅ `Color.textType1Secondary` | `.foregroundColor(.textType1Secondary)` |
| `text_type1_tertiary` | `#FFFFFF` | ✅ `Color.textType1Tertiary` | `.foregroundColor(.textType1Tertiary)` |
| `text_disable_type1_primary` | `#9C9BAB` | ✅ `Color.textDisableType1Primary` | `.foregroundColor(.textDisableType1Primary)` |
| `text_type2_secondary` | `#E7E7E9` | ✅ `Color.textType2Secondary` | `.foregroundColor(.textType2Secondary)` |

### 線條/邊框 (Line)

| Figma 變數 | Hex (Dark) | DesignSystem | SwiftUI 使用 |
|------------|------------|--------------|--------------|
| `line_type1_primary` | `#332F59` | ✅ `Color.lineType1Primary` | `.stroke(Color.lineType1Primary)` |
| `line_type1_secondary` | `#464272` | ✅ `Color.lineType1Secondary` | `.stroke(Color.lineType1Secondary)` |

### 警告/錯誤 (Warning)

| Figma 變數 | Hex (Dark) | DesignSystem | SwiftUI 使用 |
|------------|------------|--------------|--------------|
| `warning_primary` | `#FB4D3D` | ✅ `Color.warningPrimary` | `.foregroundColor(.warningPrimary)` |

---

## 🧩 元件對照表

### Load Code Widget

```swift
// 外框背景
.background(Color.backgroundType1Tertiary)  // #28263C

// Dropdown / Input 背景
.background(Color.backgroundType1Secondary)  // #100E26

// Focus 邊框
.overlay(
    RoundedRectangle(cornerRadius: 10)
        .stroke(Color.brandSecondary, lineWidth: 1)  // #9FF611
)

// Error 邊框
.overlay(
    RoundedRectangle(cornerRadius: 10)
        .stroke(Color.warningPrimary, lineWidth: 1)  // #FB4D3D
)

// Placeholder 文字
.foregroundColor(.textType1Secondary)  // #878693

// 輸入文字
.foregroundColor(.textType1Primary)  // #E7E7E9

// 游標顏色
.tint(.brandSecondary)  // #9FF611
```

### Load 按鈕

```swift
// 啟用狀態
Text("Load")
    .foregroundColor(.brandTertiary)  // #100E26 (深色背景上的文字)
    .background(Color.brandSecondary)  // #9FF611

// 禁用狀態
Text("Load")
    .foregroundColor(.textDisableType1Primary)  // #9C9BAB
    .background(Color.brandSecondaryDisable)  // #343247
```

### 清除按鈕

```swift
Image(systemName: "xmark.circle.fill")
    .foregroundColor(.textType1Secondary)  // #878693
```

### Error 訊息

```swift
Text(errorMessage)
    .foregroundColor(.warningPrimary)  // #FB4D3D
```

### Bookie Selector Sheet

```swift
// Sheet 背景
.background(Color.brandTertiary)  // #100E26

// 未選中按鈕
.background(Color.lineType1Secondary.opacity(0.5))  // #464272 @ 50%
.foregroundColor(.textType1Tertiary)  // #FFFFFF

// 選中按鈕
.background(Color.brandSecondary)  // #9FF611
.foregroundColor(.lineType1Secondary)  // #464272
```

### Toast (Partial Error)

```swift
HStack(spacing: 4) {
    Image("icon/exclamtion/2")
        .foregroundColor(.textType2Secondary)  // #E7E7E9
    Text("\(count) selections failed to convert")
        .foregroundColor(.textType2Secondary)  // #E7E7E9
}
.background(Color.warningPrimary)  // #FB4D3D
```

---

## ⚠️ 缺少的顏色（需確認）

以下顏色在 Figma 設計稿中出現，但在 DesignSystem 中可能需要確認：

| Figma 用途 | Hex | 建議 DesignSystem 對應 |
|------------|-----|------------------------|
| 拖曳條 (Drag Handle) | `#D9D9D9` | 可能需新增或使用 `.indicator` |
| 漸層遮罩 | `#100E26` → transparent | 使用 `Color.brandTertiary` |

---

## 📋 快速對照清單

```swift
// === 品牌色 ===
Color.brandSecondary          // #9FF611 - Focus 邊框、CTA 按鈕
Color.brandSecondaryDisable   // #343247 - 禁用按鈕
Color.brandTertiary           // #100E26 - 深色背景

// === 背景色 ===
Color.backgroundType1Primary   // #1C1A31 - 主背景
Color.backgroundType1Secondary // #100E26 - 輸入框背景
Color.backgroundType1Tertiary  // #28263C - Widget 外框

// === 文字色 ===
Color.textType1Primary         // #E7E7E9 - 主文字
Color.textType1Secondary       // #878693 - 次文字、Placeholder
Color.textType1Tertiary        // #FFFFFF - 白色文字
Color.textDisableType1Primary  // #9C9BAB - 禁用文字

// === 警告 ===
Color.warningPrimary           // #FB4D3D - 錯誤邊框、錯誤文字

// === 線條 ===
Color.lineType1Secondary       // #464272 - Bookie 選項背景
```

---

## 🔄 TDD 原始規格 vs DesignSystem 對照

| TDD 原始寫法 | 應改為 |
|-------------|--------|
| `Color(hex: "#9ff611")` | `Color.brandSecondary` |
| `Color(hex: "#343247")` | `Color.brandSecondaryDisable` |
| `Color(hex: "#100e26")` | `Color.brandTertiary` 或 `Color.backgroundType1Secondary` |
| `Color(hex: "#28263c")` | `Color.backgroundType1Tertiary` |
| `Color(hex: "#e7e7e9")` | `Color.textType1Primary` |
| `Color(hex: "#878693")` | `Color.textType1Secondary` |
| `Color(hex: "#9c9bab")` | `Color.textDisableType1Primary` |
| `Color(hex: "#fb4d3d")` | `Color.warningPrimary` |
| `Color(hex: "#464272")` | `Color.lineType1Secondary` |
| `Color(hex: "#ffffff")` | `Color.textType1Tertiary` |

