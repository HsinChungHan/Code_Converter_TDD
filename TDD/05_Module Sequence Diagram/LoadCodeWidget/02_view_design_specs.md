# View Design Specs（Figma 設計規格）

> **來源**：Figma File Key `SvcTlADMZ7gUPIa7nN2hT1`  
> **參考**：`Phase1_Design_Specs.md`, `Figma_Nodes_Phase1.md`

---

## 📋 目錄

1. [Design Tokens](#design-tokens)
2. [Load Code Widget](#load-code-widget)
3. [Bookie Selector Bottom Sheet](#bookie-selector-bottom-sheet)
4. [Toast Message (Partial Error)](#toast-message-partial-error)
5. [Icons](#icons)
6. [響應式規則](#響應式規則)

---

## 🎨 Design Tokens

### 顏色 (Colors)

#### 品牌色 (Brand)

| 變數名稱 | Hex 值 | SwiftUI | 用途 |
|----------|--------|---------|------|
| `brand/brand_secondary` | `#9ff611` | `.brandSecondary` | CTA 按鈕、選中狀態、Focus 邊框 |
| `brand/brand_secondary_disable` | `#343247` | - | 禁用狀態按鈕背景 |
| `brand/brand_tertiary` | `#100e26` | - | 深色背景、Bottom Sheet 背景 |

#### 背景色 (Background)

| 變數名稱 | Hex 值 | SwiftUI | 用途 |
|----------|--------|---------|------|
| `background_type1_primary` | `#1c1a31` | `.backgroundType1Primary` | 主背景 |
| `background_type1_secondary` | `#100e26` | `.backgroundType1Secondary` | 輸入框背景、Dropdown 背景 |
| `background_type1_tertiary` | `#28263c` | `.backgroundType1Tertiary` | Widget 外框背景 |

#### 文字色 (Text)

| 變數名稱 | Hex 值 | 用途 |
|----------|--------|------|
| `text_type1_primary` | `#e7e7e9` | 主要文字（輸入的 Booking Code） |
| `text_type1_secondary` | `#878693` | 次要文字（Placeholder、標籤） |
| `text_type1_tertiary` | `#ffffff` | 白色文字（Bookie 選項） |
| `text_disable_type1_primary` | `#9c9bab` | 禁用狀態文字 |

#### 警告/錯誤 (Warning)

| 變數名稱 | Hex 值 | 用途 |
|----------|--------|------|
| `warning_primary` | `#fb4d3d` | 錯誤邊框、錯誤文字、Toast 背景 |

---

### 字型 (Typography)

| 樣式名稱 | Font | Weight | Size | Line Height | 用途 |
|----------|------|--------|------|-------------|------|
| `Body/B1_M` | Roboto | Medium (500) | 14px | 20px | 中型按鈕、標籤 |
| `Body/B1_B` | Roboto | Bold (700) | 14px | auto | Bookie 選項文字 |
| `Body/B2_M` | Roboto | Medium (500) | 12px | 16px | Load 按鈕 |
| `Body/B2_R` | Roboto | Regular (400) | 12px | auto | 錯誤訊息、提示文字 |

**SwiftUI 對照：**

```swift
// Body/B1_M (14px Medium)
.font(.system(size: 14, weight: .medium))

// Body/B2_M (12px Medium) - Load 按鈕
.font(.system(size: 12, weight: .medium))

// Body/B2_R (12px Regular) - 錯誤訊息
.font(.system(size: 12, weight: .regular))
```

---

### 圓角 (Border Radius)

| 元件 | 值 | SwiftUI |
|------|-----|---------|
| Widget 外框 | `10px` | `RoundedRectangle(cornerRadius: 10)` |
| 輸入框 | `10px` | `RoundedRectangle(cornerRadius: 10)` |
| Load 按鈕 | `2px` | `RoundedRectangle(cornerRadius: 2)` |
| Bottom Sheet 頂部 | `10px` | `.cornerRadius(10, corners: [.topLeft, .topRight])` |
| Bookie 選項按鈕 | `10px` | `RoundedRectangle(cornerRadius: 10)` |
| Toast Message | `10px` | `RoundedRectangle(cornerRadius: 10)` |

---

### 間距 (Spacing)

| 元件 | 屬性 | 值 | SwiftUI |
|------|------|-----|---------|
| Widget 外框 | padding | `8px` | `.padding(8)` |
| Widget 外框 | gap | `8px` | `HStack(spacing: 8)` |
| 輸入框 | padding | `12px 14px` | `.padding(.horizontal, 14).padding(.vertical, 12)` |
| Load 按鈕 | padding | `12px` | `.padding(12)` |
| Load 按鈕 | height | `28px` | `.frame(height: 28)` |
| Bookie Dropdown | width | `104px` | `.frame(width: 104)` |
| Bookie Dropdown | height | `44px` | `.frame(height: 44)` |
| Input Container | height | `44px` | `.frame(height: 44)` |

---

### 陰影 (Shadows)

| 元件 | 值 | SwiftUI |
|------|-----|---------|
| Toast Message | `0px 4px 12px rgba(28, 26, 49, 0.25)` | `.shadow(color: Color(hex: "#1c1a31").opacity(0.25), radius: 12, x: 0, y: 4)` |

---

## 🧩 Load Code Widget

### 元件結構

```
Load Code Widget (外框)                    ← 10px 圓角, #28263c 背景, 8px padding
├── Bookie Dropdown (左側)                ← 104px × 44px, #100e26 背景
│   ├── Bookie 名稱 (如 "F.com")          ← #e7e7e9, 14px Medium
│   ├── Country 名稱 (如 "NG")            ← #878693, 12px Regular
│   └── 下拉箭頭 icon                      ← 12px, #ffffff
└── Input Container (右側)                ← flex: 1, 44px 高, #100e26 背景
    ├── Placeholder / 輸入文字             ← #878693 (placeholder) / #e7e7e9 (輸入)
    ├── 清除按鈕 (Typing/Filled/Error)     ← 20px, #878693
    └── Load 按鈕                          ← 28px 高, 2px 圓角
```

---

### 6 種狀態 - Figma Node ID 對照

| 狀態 | Figma Node ID | 輸入框邊框 | Load 按鈕 | 額外元素 |
|------|---------------|-----------|-----------|----------|
| **Default** | `26769:88873` | 無 | 灰色 `#343247` | - |
| **Focus** | `26769:88868` | 綠色 `#9ff611` 1px | 灰色 `#343247` | 綠色游標 |
| **Typing** | `26769:88869` | 綠色 `#9ff611` 1px | 綠色 `#9ff611` | 清除按鈕 ⊗ |
| **Filled** | `26769:88870` | 無 | 綠色 `#9ff611` | 清除按鈕 ⊗ |
| **Loading** | `26769:88872` | 無 | 灰色 + Spinner | Loading 提示文字 |
| **Error** | `26769:88871` | 紅色 `#fb4d3d` 1px | 綠色 `#9ff611` | 錯誤訊息（紅色） |

---

### Default 狀態

```
┌─────────────────────────────────────────────────────────────┐
│  ┌──────────────┐  ┌──────────────────────────────────────┐ │
│  │ F.com     ▼  │  │ Booking Code              ┌──────┐  │ │
│  │ NG           │  │                           │ Load │  │ │
│  └──────────────┘  └───────────────────────────└──────┘──┘ │
└─────────────────────────────────────────────────────────────┘
```

**SwiftUI 實作：**

```swift
// 外框
RoundedRectangle(cornerRadius: 10)
    .fill(Color(hex: "#28263c"))  // background_type1_tertiary

// Load 按鈕 (禁用)
Text("Load")
    .font(.system(size: 12, weight: .medium))
    .foregroundColor(Color(hex: "#9c9bab"))  // text_disable_type1_primary
    .padding(.horizontal, 12)
    .frame(height: 28)
    .background(
        RoundedRectangle(cornerRadius: 2)
            .fill(Color(hex: "#343247"))  // brand_secondary_disable
    )
```

---

### Focus 狀態

**變化：**
- Input Container：`border: 1px solid #9ff611`
- 游標：`#9ff611`, 1px × 14px

**SwiftUI 實作：**

```swift
// 輸入框邊框
.overlay(
    RoundedRectangle(cornerRadius: 10)
        .stroke(Color(hex: "#9ff611"), lineWidth: 1)
)

// TextField 游標顏色
.tint(Color(hex: "#9ff611"))
```

---

### Typing 狀態

**變化：**
- 保持綠色邊框
- 顯示清除按鈕 ⊗（20px，#878693）
- Load 按鈕變為綠色啟用

**SwiftUI 實作：**

```swift
// 清除按鈕
Button(action: onClear) {
    Image(systemName: "xmark.circle.fill")
        .resizable()
        .frame(width: 20, height: 20)
        .foregroundColor(Color(hex: "#878693"))
}

// Load 按鈕 (啟用)
Text("Load")
    .font(.system(size: 12, weight: .medium))
    .foregroundColor(Color(hex: "#100e26"))  // brand_tertiary
    .padding(.horizontal, 12)
    .frame(height: 28)
    .background(
        RoundedRectangle(cornerRadius: 2)
            .fill(Color(hex: "#9ff611"))  // brand_secondary
    )
```

---

### Loading 狀態

**變化：**
- 移除邊框
- Load 按鈕變為 Loading Spinner
- 顯示提示文字

**提示文字：**
```
"Conversion may take up to 10 seconds, please stay here and wait for the result."
```

**SwiftUI 實作：**

```swift
// Loading Spinner
ProgressView()
    .progressViewStyle(CircularProgressViewStyle(tint: Color.white))
    .scaleEffect(0.8)

// 提示文字
Text("Conversion may take up to 10 seconds, please stay here and wait for the result.")
    .font(.system(size: 12, weight: .regular))
    .foregroundColor(Color(hex: "#e7e7e9"))
    .padding(.top, 8)
```

---

### Error 狀態

**變化：**
- Input Container：`border: 1px solid #fb4d3d`（紅色）
- 顯示錯誤文字（紅色）
- 保持清除按鈕
- Load 按鈕保持綠色（可重試）

**錯誤文字：**
```
"We couldn't find this booking code on [BookieName]. Please check and try again."
```

**SwiftUI 實作：**

```swift
// 紅色邊框
.overlay(
    RoundedRectangle(cornerRadius: 10)
        .stroke(Color(hex: "#fb4d3d"), lineWidth: 1)
)

// 錯誤文字
Text(errorMessage)
    .font(.system(size: 12, weight: .regular))
    .foregroundColor(Color(hex: "#fb4d3d"))
    .padding(.top, 8)
```

---

## 📱 Bookie Selector Bottom Sheet

### Figma Node IDs

| 場景 | Node ID |
|------|---------|
| 開啟選單 | `26753:64425` |
| 多國家 Bookie | `26753:74664` |
| 選擇 Country | `26753:78142` |
| 點擊 mask 關閉 | `26753:81632` |
| 選擇完成 | `26753:85011` |
| Scroll Bookie List | `26748:63554` |
| Bookie with Country | `26748:63712` |

---

### 元件結構

```
Bottom Sheet                               ← #100e26 背景, 10px 頂部圓角
├── 拖曳條 (Drag Handle)                   ← #d9d9d9, 60px × 4px, 18px 圓角
├── 標題列
│   ├── "Bookie" 標籤                       ← #878693, 14px Medium
│   └── "Country" 標籤                      ← #878693, 14px Medium
├── 雙欄選擇器
│   ├── Bookie 列表 (左欄)
│   └── Country 列表 (右欄)
└── 漸層遮罩 (Fade Out Mask)                ← #100e26 0% → 100%, 12px 高
```

---

### 樣式規格

**Bottom Sheet 容器：**

```swift
.background(Color(hex: "#100e26"))
.cornerRadius(10, corners: [.topLeft, .topRight])
.padding(.horizontal, 12)
.padding(.top, 6)
.padding(.bottom, 16)
```

**拖曳條：**

```swift
RoundedRectangle(cornerRadius: 18)
    .fill(Color(hex: "#d9d9d9"))
    .frame(width: 60, height: 4)
```

**Bookie 選項按鈕：**

| 狀態 | 背景色 | 文字色 |
|------|--------|--------|
| 未選中 | `#464272` (50% opacity) | `#ffffff` |
| 選中 | `#9ff611` | `#464272` |

```swift
// 未選中
RoundedRectangle(cornerRadius: 10)
    .fill(Color(hex: "#464272").opacity(0.5))

// 選中
RoundedRectangle(cornerRadius: 10)
    .fill(Color(hex: "#9ff611"))
```

**選項按鈕尺寸：**

```swift
.frame(height: 40)
.padding(.horizontal, 12)
```

**列間距：** `8px`
**欄間距：** `12px`

---

### 漸層遮罩

```swift
LinearGradient(
    gradient: Gradient(colors: [
        Color(hex: "#100e26").opacity(0),
        Color(hex: "#100e26")
    ]),
    startPoint: .top,
    endPoint: .bottom
)
.frame(height: 12)
```

---

### Bookie 清單 + Country 對應

| Bookie | 支援的 Country | 選擇行為 |
|--------|----------------|----------|
| F.com | NG, GH | 需選 Country |
| Sporty | NG, GH | 需選 Country |
| MSport | NG, TZ | 需選 Country |
| Bet9ja | NG | ✅ 自動選 NG 並關閉 |
| Bangbet | NG, GH, TZ, KE, UG | 需選 Country |
| BetKing | NG | ✅ 自動選 NG 並關閉 |
| 1xBet | NG | ✅ 自動選 NG 並關閉 |
| Betway | NG | ✅ 自動選 NG 並關閉 |

---

## 🔔 Toast Message (Partial Error)

### Figma Node ID

`26428:71769`

### 視覺規格

```
┌───────────────────────────────────────────────────────────┐
│  ⚠  2 selections failed to convert                       │
└───────────────────────────────────────────────────────────┘
```

**SwiftUI 實作：**

```swift
struct PartialErrorToast: View {
    let failedCount: Int
    
    var body: some View {
        HStack(spacing: 4) {
            Image("icon/exclamtion/2")  // 12px
                .resizable()
                .frame(width: 12, height: 12)
                .foregroundColor(Color(hex: "#e7e7e9"))
            
            Text("\(failedCount) selection\(failedCount > 1 ? "s" : "") failed to convert")
                .font(.system(size: 12, weight: .regular))
                .foregroundColor(Color(hex: "#e7e7e9"))
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(Color(hex: "#fb4d3d"))
        )
        .shadow(
            color: Color(hex: "#1c1a31").opacity(0.25),
            radius: 12,
            x: 0,
            y: 4
        )
    }
}
```

**位置：** 螢幕底部，距離左右 `10px`

---

## 🖼️ Icons

| Icon 名稱 | 用途 | 尺寸 | 顏色 |
|-----------|------|------|------|
| `icon/arrow_3/down` | Dropdown 下拉箭頭 | 12px | `#ffffff` |
| `icon/loading` | Load 按鈕 Loading | 12px | - |
| `icon/cancel` (xmark.circle.fill) | 清除輸入框 | 20px | `#878693` |
| `icon/exclamtion/2` | Toast 警告 | 12px | `#e7e7e9` |

---

## 📐 響應式規則

> ⚠️ 設計基於 **360px** 寬度

| 元件 | 寬度規則 | SwiftUI |
|------|----------|---------|
| Load Code Widget | 滿版 - padding | `.frame(maxWidth: .infinity)` |
| Bookie Dropdown | 固定 `104px` | `.frame(width: 104)` |
| Input Container | 彈性填滿 | `.frame(maxWidth: .infinity)` |
| Bottom Sheet | 滿版 | `.frame(maxWidth: .infinity)` |
| Toast Message | 滿版 - 20px | `.padding(.horizontal, 10)` |

---

## ✅ 實作 Checklist

### Load Code Widget

- [ ] 外框容器（#28263c, 10px 圓角, 8px padding）
- [ ] Bookie Dropdown（104px × 44px）
- [ ] Input Container（44px 高）
- [ ] 6 種狀態切換
- [ ] 清除按鈕 ⊗
- [ ] Load 按鈕（啟用/禁用狀態）
- [ ] Focus 邊框（#9ff611）
- [ ] Error 邊框（#fb4d3d）
- [ ] Loading 提示文字
- [ ] Error 訊息文字

### Bookie Selector

- [ ] Bottom Sheet 容器（#100e26）
- [ ] 拖曳條（60px × 4px）
- [ ] 雙欄選擇器
- [ ] 選中/未選中狀態
- [ ] 漸層遮罩
- [ ] 單一國家自動關閉
- [ ] 多國家選擇流程

### Toast Message

- [ ] 容器（#fb4d3d, 10px 圓角）
- [ ] Warning icon
- [ ] 動態文字
- [ ] 陰影效果

