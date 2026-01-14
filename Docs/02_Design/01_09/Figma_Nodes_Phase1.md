# Phase 1 - Figma Node 清單 (2025-01-09 更新)

> **目的**：提供 Figma node-id 讓 AI 透過 Figma MCP 抓取設計資訊  
> **更新日期**：2025-01-09  
> **變更原因**：需求調整，簡化 Bookie 選擇流程

---

## 📁 Figma 檔案資訊

| 項目 | 值 |
|------|-----|
| **File Key** | `SvcTlADMZ7gUPIa7nN2hT1` |
| **File Name** | Code-Converter |
| **Base URL** | `https://www.figma.com/design/SvcTlADMZ7gUPIa7nN2hT1/Code-Converter` |

---

## ⚠️ 與舊版 (01_01) 的主要差異

| 變更項目 | 舊版 (01_01) | 新版 (01_09) | 備註 |
|----------|--------------|--------------|------|
| **Bookie/Country 選擇器** | ✅ 有（Bottom Sheet 雙欄選擇器） | ❌ 移除 | 重大變更 |
| **按鈕文字** | "Load" | "Import" | UI 文字變更 |
| **輸入框 Placeholder** | "Booking Code" | "Paste any booking code" | UI 文字變更 |
| **Bookie Dropdown** | ✅ 有（顯示 F.com ▼ NG） | ❌ 移除 | 重大變更 |
| **Widget 位置** | 獨立區塊 | Quick Panel 下方 (Load Code Highlight) | 佈局變更 |
| **1.0.3 Bookie Selection** | ✅ 有 | ❌ 移除 | 流程簡化 |
| **1.0.4 Type Done** | ✅ 有 | ❌ 移除（合併至 Typing） | 流程簡化 |

---

## 🏠 Part 1. Homepage - 主流程畫面

### 使用者流程圖 (新版)

```
                              Homepage default sorting
                                       │
Before ──────────────────────────────► After
(Mostly Area)                           │
                                        ▼
                    ┌───────────────────────────────────────┐
                    │  Story                                │
                    │  Quick Panel                          │
                    │  Load Code Highlight  ◄── 新增位置    │
                    │  Banner (Move to Last one)            │
                    └───────────────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
    1.0.0 Default                   1.0.1 Focus                    1.0.2 Typing
    [Paste any booking code] [Import]   │                         [3RA3FA] [Import]
        │                               │                               │
        └───────────────────────────────┴───────────────────────────────┘
                                        │
                                        ▼
                                1.0.5 Loading
                    "Conversion may take up to 10 seconds..."
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
            1.0.6 Error                              1.0.8 Betslip
    "We couldn't find this booking code..."     ┌─────────┴─────────┐
                    │                           ▼                   ▼
                    ▼                       Success             Partial
            重新輸入 (1.0.1)           (Replace existing    "2 selections 
                                        selections)         failed to convert"
```

### 主要流程 Frames

| # | Figma 名稱 | 說明 | node-id | 狀態 |
|---|------------|------|---------|------|
| Before | Mostly Area | 既有首頁區塊（變更前） | 26337-14354 | - |
| 1.0.0 | Homepage Load Code Default | 新增 Load Code Widget（預設狀態） |  26453-93262 | ✅ 保留 |
| 1.0.1 | Homepage Load Code Focus | 輸入框聚焦，鍵盤彈出 | 26453-94175 | ✅ 保留 |
| 1.0.2 | Homepage Load Code Typing | 使用者輸入 "3RA3FA"，Import 變綠 | 26453-95089 | ✅ 保留 |
| ~~1.0.3~~ | ~~Homepage Load Code Select Bookie~~ | ~~Bookie 選擇器~~ | - | ❌ 已移除 |
| ~~1.0.4~~ | ~~Homepage Load Code Type Done~~ | ~~已選 Bookie + 已填入 Code~~ | - | ❌ 已移除 |
| 1.0.5 | Homepage Load Code Loading | 轉換中，提示最多等待 10 秒 | 26453-96003 | ✅ 保留 |
| 1.0.6 | Homepage Load Code Error | 轉換失敗（紅字錯誤訊息） | 26453-96916 | ✅ 保留 |
| 1.0.8 | Homepage Load Code to Betslip | Betslip 載入結果（含 Partial 狀態） | 26428-71768 | ✅ 保留 |

> ⚠️ **注意**：1.0.3 和 1.0.4 已移除，Bookie 選擇流程已簡化

---

## 🧩 Part 1. Homepage - 元件 (Components)

### Load Code Widget - Input 狀態 (新版)

> 📍 Widget 結構簡化：輸入框 + Import 按鈕 + Info Tip Icon

| 狀態 | 外觀說明 | node-id | ✅ 已驗證 |
|------|----------|---------|----------|
| Default | `Paste any booking code` placeholder + `Import` 按鈕（灰色） | `26769:88873` | ✅ |
| Focus | 輸入框高亮，鍵盤彈出，placeholder 仍在 | `26769:88868` | - |
| Typing | `3RA3FA` + `Import`（綠色啟用） | `26769:88869` | - |
| Filled | 同 Typing，已完成輸入 | `26769:88870` | - |
| Loading | Loading icon + 提示文字 | `26769:88872` | ✅ |
| Error | 紅色邊框 + 清除按鈕 + 錯誤文字 | `26769:88871` | ✅ |

### 元件結構 (新版 - 已從 Figma 確認)

```
Load Code Widget (外框)
├── Input Row
│   ├── Input Container
│   │   ├── Placeholder / 輸入文字
│   │   ├── Clear Icon (⊗) ← Typing/Error 狀態顯示
│   │   └── Import 按鈕 / Loading Icon
│   └── Info Tip Icon (ⓘ) ← 新增元件
└── Helper Text (Loading/Error 狀態)
    ├── Loading: "Conversion may take up to 10 seconds..."
    └── Error: "We couldn't find this booking code..."
```

---

### ~~Bookie Selection Flow~~ (已移除)

> ❌ **此功能在新版中已移除**  
> 舊版的 Bookie + Country 雙欄選擇器（Bottom Sheet）不再需要

---

### Betslip 結果狀態

| 狀態 | 說明 | node-id | ✅ |
|------|------|---------|---|
| Success/Partial | 轉換結果 Betslip（含 Partial Error Toast） | `26428:71768` | ✅ |

> 📍 **Toast 訊息**：「⚠ 2 selections failed to convert」（紅底，數字動態替換）

> ⚠️ **重要規則**：
> - **If there are selections in betslip, replace them.**
> - **Can only convert football match**

---

## 🎨 Design Tokens (已從 Figma 驗證 ✅)

### 顏色

| 變數名稱 | 值 | 用途 | ✅ |
|----------|-----|------|---|
| `background/type1/background_type1_tertiary` | `#28263c` | Load Code Widget 背景 | ✅ |
| `background/type1/background_type1_secondary` | `#100e26` | 輸入框背景 | ✅ |
| `text/type1/text_type1_primary` | `#e7e7e9` | 主要文字、Loading 提示文字 | ✅ |
| `text/type1/text_type1_secondary` | `#878693` | Placeholder 文字、Info Tip Icon | ✅ |
| `text/type1/text_disable_type1_primary` | `#9c9bab` | Import 按鈕禁用文字 | ✅ |
| `brand/brand_secondary` | `#9ff611` | Import 按鈕啟用狀態 | ✅ |
| `brand/brand_tertiary` | `#100e26` | Import 按鈕啟用文字 | ✅ |
| `brand/brand_secondary_disable` | `#343247` | Import 按鈕禁用背景 | ✅ |
| `warning/warning_primary` | `#fb4d3d` | 錯誤邊框、錯誤文字 | ✅ |

### 字型 (已從 Figma 驗證 ✅)

| 樣式名稱 | Font | Weight | Size | Line Height | 用途 |
|----------|------|--------|------|-------------|------|
| `Body/B1_R` | Roboto | Regular (400) | 14px | 21px | 輸入框文字、Placeholder |
| `Body/B2_M (btn-s)` | Roboto | Medium (500) | 12px | 16px | Import 按鈕 |
| `Body/B2_R` | Roboto | Regular (400) | 12px | auto | 提示文字、錯誤訊息 |

### 尺寸 (已從 Figma 驗證 ✅)

| 元件 | 屬性 | 值 |
|------|------|-----|
| Load Code Widget | padding | `8px` |
| Load Code Widget | gap | `4px` (垂直)、`8px` (水平) |
| Load Code Widget | border-radius | `10px` |
| Input Container | height | `44px` |
| Input Container | border-radius | `10px` |
| Import 按鈕 | height | `28px` |
| Import 按鈕 | border-radius | `2px` |
| Import 按鈕 | padding | `12px` (水平) |
| Info Tip Icon | size | `16px` |
| Clear Icon | size | `20px` |
| Loading Icon | size | `12px` |

---

## 📌 UI 文字內容

### Loading 狀態
```
Conversion may take up to 10 seconds, please stay here and wait for the result.
```

### Error 狀態
```
We couldn't find this booking code. Please check and try again.
```

### Partial Error Toast
```
⚠ 2 selections failed to convert
```
（數字動態替換）

---

## 🆕 Info Icon → GuideDialog (2025-01-12 新增)

> **點擊 Info Icon (ⓘ) 彈出說明 Dialog**

| 項目 | 值 |
|------|-----|
| **Frame node-id** | `27536:81442` |
| **Dialog node-id** | `27536:84826` |
| **Figma URL** | [Dialog Link](https://www.figma.com/design/SvcTlADMZ7gUPIa7nN2hT1/Code-Converter?node-id=27536-84826&m=dev) |

### Dialog 規格

| 屬性 | 值 |
|------|-----|
| **標題** | "Import Booking Code" |
| **內容** | • Paste a booking code to load its selections into your betslip.<br>• Supports our codes and codes from other betting sites. |
| **按鈕** | "Ok" (綠色，brand_secondary #9ff611) |
| **背景色** | `#100e26` (background_type1_secondary) |
| **標題字型** | Headline/H3_M (Roboto Medium 18px) |
| **內容字型** | Body/B1_R (Roboto Regular 14px, line-height 21px) |
| **按鈕字型** | Body/B1_M (Roboto Medium 14px) |
| **Padding** | 20px (horizontal), 32px (vertical) |
| **內容間距** | 24px (title↔button), 20px (title↔description) |

### 復用現有 GuideDialog 元件

```swift
// 路徑: FComUI/Sources/FComUI/GuideDialog/

import FComUI

// 建立 ViewState（單頁，無圖片）
let viewState = GuideDialog.ViewState(
    pages: [
        GuideDialog.Page(
            title: "Import Booking Code",
            description: """
            • Paste a booking code to load its selections into your betslip.
            • Supports our codes and codes from other betting sites.
            """,
            contentSource: .image(.asset(name: "")) // 無圖片可傳空
        )
    ],
    finalButtonTitle: "Ok",
    theme: GuideDialog.Theme(
        backgroundStyle: .absoluteType1,  // #100e26
        titleStyle: .h3m,
        descriptionStyle: .h4r
    ),
    contentTopPadding: 0  // 無圖片不需要 top padding
)

// 建立 ViewAction
let viewAction = GuideDialog.ViewAction(
    onDoneButtonTapped: {
        // 關閉 Dialog
        dismiss()
    }
)

// 建立 View
let dialogView = FComUIFactory.createGuideDialogView(
    viewState: viewState,
    viewAction: viewAction
)
```

### 觸發條件

| 事件 | 行為 |
|------|------|
| 點擊 Info Icon (ⓘ) | 彈出 GuideDialog |
| 點擊 "Ok" 按鈕 | 關閉 Dialog |

---

## 🆕 One-Time Tooltip (2025-01-12 新增)

> **Feature 上線後顯示一次性 Tooltip，點擊後消失，按 device ID 存儲**

| 項目 | 值 |
|------|-----|
| **Frame node-id** | `27526:67890` |
| **Tooltip node-id** | `27526:71304` |
| **Figma URL** | [Tooltip Link](https://www.figma.com/design/SvcTlADMZ7gUPIa7nN2hT1/Code-Converter?node-id=27526-71304&m=dev) |

### Tooltip 規格

| 屬性 | 值 |
|------|-----|
| **文字** | "Supports booking codes from many platforms" |
| **背景色** | `#4d5fae` (hint_background_type1) |
| **文字色** | `#e7e7e9` (text_type1_primary) |
| **字型** | Body/B2_R (Roboto Regular 12px) |
| **圓角** | 4px |
| **Padding** | 12px (horizontal), 6px (vertical) |
| **關閉按鈕** | 12px 圓形，內含 8px cancel icon |
| **箭頭** | 向上，寬 16px，高 12px |
| **位置** | Widget 下方 (downLeading) |

### 行為規則

| 規則 | 說明 |
|------|------|
| **顯示條件** | Feature 上線後首次進入首頁 |
| **儲存方式** | 按 device ID 存儲到 local storage |
| **消失條件** | 用戶點擊關閉按鈕 or 點擊 Tooltip 外部 |
| **顯示次數** | 每個 device 只顯示一次 |

### 復用現有 Tooltip 元件

```swift
// 使用 FComUI/Tooltip
import FComUI

// 1. 在 View 外層加上 tooltipOverlay()
SomeParentView()
    .tooltipOverlay()

// 2. 在 Widget 上加上 showTooltip modifier
LoadBookingCodeSectionView(...)
    .showTooltip(config: Tooltip.TooltipSwiftUIConfig(
        isPresented: $showCodeConverterTooltip,
        anchorFrame: $widgetFrame,
        placement: .downLeading,
        description: "Supports booking codes from many platforms",
        onClose: { 
            // 標記已顯示，存儲到 UserDefaults/Keychain by device ID
            CodeConverterTooltipStorage.markAsShown()
        },
        duration: 0  // 不自動消失，等用戶點擊
    ))
```

### 儲存邏輯建議

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

---

## ✅ 填寫完成確認

- [x] 填入 **1.0.0 ~ 1.0.2** 主流程的 node-id ✅
- [x] 填入 **1.0.5 ~ 1.0.6** 主流程的 node-id ✅
- [x] 填入 **1.0.8** Betslip 的 node-id ✅
- [x] 填入 **Load Code Widget** 所有狀態的 node-id ✅
- [x] 確認 Design Tokens ✅ (已從 Figma MCP 驗證)
- [x] 發現新元件：**Info Tip Icon** (`icon/tip/1`) ✅
- [x] 新增 **One-Time Tooltip** (`27526:71304`) ✅ (2025-01-12)

---

## 📝 備註區

```
【2025-01-09 更新重點 - 已從 Figma MCP 驗證】

🔄 流程簡化:
- 移除 Bookie/Country 選擇器 (1.0.3)
- 移除 Type Done 狀態 (1.0.4)
- 使用者直接輸入 Booking Code 即可

🎯 UI 變更:
- "Load" → "Import"
- "Booking Code" → "Paste any booking code"
- Widget 位置移至 Quick Panel 下方
- 新增 Info Tip Icon (icon/tip/1) 在輸入框右側

🆕 新發現元件:
- icon/tip/1: Info 提示 icon (16x16px, #878693)
- icon/loading: Loading 動畫 icon (12x12px)
- Clear Icon: 清除輸入按鈕 (20x20px, #878693)

✅ 已驗證的 UI 文字:
- Loading: "Conversion may take up to 10 seconds, please stay here and wait for the result."
- Error: "We couldn't find this booking code. Please check and try again."

⚠️ 業務規則:
- 轉換成功會「替換」Betslip 中既有的 selections
- 僅支援足球賽事 (Can only convert football match)

❓ 待確認:
- API 如何判斷 Bookie？（不再由用戶選擇）
- BE 討論中，待更新
```
