# State ↔ Figma Node Mapping

> **用途**：讓 AI 在實作時透過 Figma MCP 自動抓取對應狀態的設計規格  
> **File Key**：`SvcTlADMZ7gUPIa7nN2hT1`  
> **版本**：01_09 (2025-01-09) - 已移除 Bookie Selector

---

## ⚠️ 01_09 版本變更

| 項目 | 舊版 (01_01) | 新版 (01_09) |
|------|--------------|--------------|
| 按鈕文字 | "Load" | "Import" |
| Placeholder | "Booking Code" | "Paste any booking code" |
| Bookie Selector | ✅ 有 | ❌ 移除 |
| Info Tip Icon | ❌ 沒有 | ✅ 新增 |

---

## 🔗 WidgetInputState → Figma Node Mapping

| State Enum | Figma Node ID | 觸發條件 (Action/Condition) | 對應 UI 變化 |
|------------|---------------|---------------------------|--------------|
| `.default` | `26769:88873` | 初始狀態 / `.inputBlurred` + 無輸入 | 無邊框、Import 灰色 |
| `.focus` | `26769:88868` | `.inputFocused` + 無輸入 | 綠色邊框、游標 |
| `.typing` | `26769:88869` | `.bookingCodeChanged` + 有輸入 + 聚焦 | 綠色邊框、清除按鈕、Import 綠色 |
| `.filled` | `26769:88870` | `.inputBlurred` + 有輸入 | 無邊框、清除按鈕、Import 綠色 |
| `.loading` | `26769:88872` | `.loadBookingCode` 執行中 | 無邊框、Spinner、提示文字 |
| `.error(message)` | `26769:88871` | `.convertCodeCompleted(.failure)` | 紅色邊框、錯誤訊息、Import 綠色 |

---

## 📱 主流程畫面 → Figma Node Mapping (01_09 簡化版)

| 流程步驟 | 畫面 | Figma Node ID | 對應 Feature Action |
|----------|------|---------------|---------------------|
| 1.0.0 | 首頁 Default | `26453:93262` | 初始狀態 |
| 1.0.1 | 首頁 Focus | `26453:94175` | `.inputFocused` |
| 1.0.2 | 首頁 Typing | `26453:95089` | `.bookingCodeChanged("...")` |
| ~~1.0.3~~ | ~~Bookie 選擇器~~ | - | ❌ 已移除 |
| ~~1.0.4~~ | ~~輸入完成~~ | - | ❌ 已移除 |
| 1.0.5 | Loading | `26453:96003` | `.loadBookingCode` |
| 1.0.6 | Error | `26453:96916` | `.convertCodeCompleted(.failure)` |
| 1.0.8 | Betslip | `26428:71768` | `.presentBetslip` |

---

## ~~🧩 Bookie Selector Sheet → Figma Node Mapping~~

> ❌ **01_09 版本已移除此功能**  
> Bookie Selector Sheet 不再需要，API 會自動判斷 Bookie

---

## 🔔 Toast → Figma Node Mapping

| Toast 類型 | Figma Node ID | 觸發條件 |
|------------|---------------|----------|
| Partial Error | `26428:71769` | `convertResult.failCnt > 0 && convertResult.successCnt > 0` |

---

## 🤖 AI 實作工作流程

### Step 1: 讀取 TDD 取得 State Mapping

```
讀取: 03_state_to_figma_mapping.md
取得: WidgetInputState → Figma Node ID 對照表
```

### Step 2: 透過 Figma MCP 抓取設計

```
對於每個需要實作的 State:
  1. 從 mapping 表取得 Figma Node ID
  2. 呼叫 mcp_Figma_get_design_context(fileKey, nodeId)
  3. 取得該狀態的詳細設計規格
```

### Step 3: 根據 TDD 的 State/Action 實作

```
根據 06_Feature State and Action:
  1. 實作 WidgetInputState enum
  2. 實作狀態轉換邏輯 (Reducer)
  3. 在 View 中根據 inputState 渲染對應 UI
```

---

## 📋 實作時的 Figma MCP 呼叫範例

### 抓取 Default 狀態設計

```json
{
  "tool": "mcp_Figma_get_design_context",
  "params": {
    "fileKey": "SvcTlADMZ7gUPIa7nN2hT1",
    "nodeId": "26769:88873",
    "clientLanguages": "swift",
    "clientFrameworks": "swiftui"
  }
}
```

### 抓取 Error 狀態設計

```json
{
  "tool": "mcp_Figma_get_design_context",
  "params": {
    "fileKey": "SvcTlADMZ7gUPIa7nN2hT1",
    "nodeId": "26769:88871",
    "clientLanguages": "swift",
    "clientFrameworks": "swiftui"
  }
}
```

### 抓取 Bookie Selector 設計

```json
{
  "tool": "mcp_Figma_get_design_context",
  "params": {
    "fileKey": "SvcTlADMZ7gUPIa7nN2hT1",
    "nodeId": "26748:63712",
    "clientLanguages": "swift",
    "clientFrameworks": "swiftui"
  }
}
```

---

## ⚡ 快速對照表（實作用）

```swift
// WidgetInputState → Figma Node ID
extension WidgetInputState {
    var figmaNodeId: String {
        switch self {
        case .default:        return "26769:88873"
        case .focus:          return "26769:88868"
        case .typing:         return "26769:88869"
        case .filled:         return "26769:88870"
        case .loading:        return "26769:88872"
        case .error:          return "26769:88871"
        }
    }
}

// 主流程畫面對應
enum LoadBookingCodeSectionScreen {
    case homepage_default     // 26453:93262
    case homepage_focus       // 26453:94175
    case homepage_typing      // 26453:95089
    case bookie_selector      // 26479:188518
    case homepage_filled      // 26479:195612
    case homepage_loading     // 26453:96003
    case homepage_error       // 26453:96916
    case betslip_result       // 26428:71768
}
```

---

## 🔄 State 轉換圖 + Figma Node (01_09 簡化版)

```mermaid
stateDiagram-v2
    [*] --> default: 初始化
    
    default --> focus: inputFocused
    note right of default: 26769:88873
    
    focus --> typing: bookingCodeChanged (有輸入)
    focus --> default: inputBlurred (無輸入)
    note right of focus: 26769:88868
    
    typing --> focus: clearButtonTapped
    typing --> filled: inputBlurred
    typing --> loading: loadBookingCode (Import 按鈕)
    note right of typing: 26769:88869
    
    filled --> focus: inputFocused
    filled --> typing: bookingCodeChanged
    filled --> loading: loadBookingCode (Import 按鈕)
    note right of filled: 26769:88870
    
    loading --> default: convertCodeCompleted (success) → Betslip
    loading --> error: convertCodeCompleted (failure)
    note right of loading: 26769:88872
    
    error --> typing: bookingCodeChanged
    error --> focus: clearButtonTapped
    note right of error: 26769:88871
```

> **01_09 變更**：移除了 Bookie Selector 相關的狀態轉換

