# Code Converter Phase 1 - 5 Day Sprint Plan

> **Sprint 期間**: 2025-01-15 (週三) ~ 2025-01-21 (週二，跳過週末)  
> **Epic**: FOOTBALL-9161 - Booking Code Converter  
> **開發者**: @Reed Hsin  
> **最後更新**: 2025-01-14
>
> **BE 新設計更新**：
> - 不再需要 Provider/Country 選擇
> - Config API 已廢棄
> - Convert API 只需傳入 `bookingCode`
> - 新增一次性 Tooltip 顯示邏輯

---

## 📊 Sprint 總覽

| Day | 日期 | 主題 | Story Points |
|-----|------|------|--------------|
| Day 1 | 01/15 (三) | 基礎架構 + UI 骨架 | 5 |
| Day 2 | 01/16 (四) | Convert API 整合 | 5 |
| Day 3 | 01/17 (五) | Betslip 串接 + 結果顯示 | 5 |
| Day 4 | 01/20 (一) | Tooltip + 錯誤處理 | 5 |
| Day 5 | 01/21 (二) | 測試 + Polish | 5 |

**Total**: 25 Story Points

---

## 📋 Jira Tickets 詳細規劃

---

### Day 1: 基礎架構 + UI 骨架 (01/15)

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - Module 架構設定
**Type**: Task  
**Story Points**: 1  
**Labels**: `architecture`, `setup`

**Description**:
設定 Code Converter 功能的 Module 架構，包含資料夾結構和基本檔案。

**Acceptance Criteria**:
- [ ] 建立 `CodeConverter/` 資料夾結構
  - `Feature/`
  - `View/`
  - `UseCase/`
  - `Repository/`
  - `Client/`
  - `Model/`
- [ ] 建立 `CodeConverterAPI.swift` 檔案 (空殼)
- [ ] 建立 `CodeConverterClient.swift` 檔案 (空殼)

**Reference**:
- TDD: `02_Architecture/01_clean_architecture_diagram.md`
- TDD: `03_Module Responsibility/01_module_responsibility.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - LoadBookingCodeSectionView 基礎 UI
**Type**: Story  
**Story Points**: 2  
**Labels**: `ui`, `view`

**Description**:
實作 Load Code Widget 的主要容器視圖（簡化版，無 Bookie Dropdown）。

**Acceptance Criteria**:
- [ ] 實作 `LoadBookingCodeSectionView` 主視圖
  - 包含 `BookingCodeInputView`
  - 背景色: `Color.backgroundType1Tertiary`
  - CornerRadius: 10
  - Padding: 8
- [ ] 實作底部錯誤訊息區域
- [ ] SwiftUI Preview 可正常顯示

**Figma Reference**:
- Node: `26769-88873` (Default State)
- Node: `26342-46244` (Component Set)

**Reference**:
- TDD: `05_Module Sequence Diagram/LoadBookingCodeSection/01_view_implementation.md`
- TDD: `05_Module Sequence Diagram/LoadBookingCodeSection/02_view_design_specs.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - BookingCodeInputView
**Type**: Story  
**Story Points**: 2  
**Labels**: `ui`, `view`, `component`

**Description**:
實作 Booking Code 輸入欄位元件。

**Acceptance Criteria**:
- [ ] 支援以下狀態:
  - Default (placeholder 顯示)
  - Focus (編輯中)
  - Typing (輸入中)
  - Filled (已填寫)
  - Loading (API 請求中)
  - Error (顯示錯誤)
- [ ] 右側 "Load" 按鈕
  - 啟用時: `Color.brandSecondary`
  - 停用時: `Color.brandSecondaryDisable`
- [ ] 清除按鈕 (Typing/Filled 狀態)
- [ ] 字型: `Font.b1_m`

**Figma Reference**:
- Node: `26769-88873` (Default)
- Node: `26769-88868` (Focus)
- Node: `26769-88869` (Typing)
- Node: `26769-88870` (Filled)
- Node: `26769-88872` (Loading)
- Node: `26769-88871` (Error)

---

### Day 2: Convert API 整合 (01/16)

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - ConvertBookingCodeUseCase
**Type**: Story  
**Story Points**: 1  
**Labels**: `usecase`, `domain`

**Description**:
實作轉換 Booking Code 的 UseCase（簡化版）。

**Acceptance Criteria**:
- [ ] Input: `ConvertBookingCodeInput` (只需 `bookingCode`)
- [ ] Output: `ConvertBookingCodeOutput` (shareCode, successCnt, failCnt)
- [ ] 調用 `CodeConverterRepository.convertCode()`
- [ ] 錯誤處理

**API Reference**:
- `POST /orders/converter/code`
- Request: `{ bookingCode }`

**Reference**:
- TDD: `07_UseCase Input and Output Model/01_usecase_input_output.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - CodeConverterRepository
**Type**: Story  
**Story Points**: 1  
**Labels**: `repository`, `data`

**Description**:
實作 Repository 層的 Convert API 呼叫。

**Acceptance Criteria**:
- [ ] 實作 `convertCode(bookingCode:)` 方法
- [ ] DTO to Domain Model 轉換
- [ ] 錯誤處理與回傳

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - CodeConverterClient
**Type**: Story  
**Story Points**: 1  
**Labels**: `client`, `network`

**Description**:
實作 Client 層的 Convert API 網路請求。

**Acceptance Criteria**:
- [ ] 實作 `convertCode(request:)` 方法
- [ ] Method: `POST`
- [ ] Endpoint: `/orders/converter/code`
- [ ] Request Body: `{ bookingCode }`
- [ ] Response DTO: `Code2CodeResponse`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - TCA Feature 整合
**Type**: Story  
**Story Points**: 2  
**Labels**: `tca`, `feature`

**Description**:
整合 TCA Feature State 和 Action（簡化版）。

**Acceptance Criteria**:
- [ ] 實作 `LoadBookingCodeSection.Feature.State` 新增屬性
  - `bookingCode: String`
  - `inputState: WidgetInputState`
  - `errorMessage: String?`
  - `convertResult: ConvertResult?`
  - `isTooltipVisible: Bool`
- [ ] 實作 `LoadBookingCodeSection.Feature.Action` 新增項目
  - `.bookingCodeChanged(String)`
  - `.clearButtonTapped`
  - `.loadButtonTapped`
  - `.convertResponse(Result<...>)`
  - `.tooltipDismissed`
- [ ] Reducer 邏輯實作

**Reference**:
- TDD: `06_Feature State and Action (TCA)/01_feature_state_action.md`

---

### Day 3: Betslip 串接 + 結果顯示 (01/17)

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - Betslip 流程串接
**Type**: Story  
**Story Points**: 2  
**Labels**: `integration`, `betslip`

**Description**:
將轉換成功後的 shareCode 串接到既有 Betslip 流程。

**Acceptance Criteria**:
- [ ] Convert API 成功後:
  1. 記錄 `failCnt` 用於後續 Toast 顯示
  2. 呼叫 `GET /bookingCode/[shareCode]/liabilities` [既有流程]
  3. 呼叫 `GET /orders/share/[shareCode]` [既有流程]
  4. Pop up Betslip 並顯示轉換結果
- [ ] 使用既有的 `BetslipRepository` / `BetslipClient`
- [ ] 錯誤時按照 Betslip 既有流程顯示錯誤 UI

**Reference**:
- TDD: `01_Integrated Service-Level Sequence Diagram/01_full_integration_flow.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - PartialErrorToast
**Type**: Story  
**Story Points**: 1  
**Labels**: `ui`, `component`, `toast`

**Description**:
實作部分轉換失敗的 Toast 提示。

**Acceptance Criteria**:
- [ ] 當 `failCnt > 0` 時顯示
- [ ] 顯示失敗數量: "X selections failed to convert"
- [ ] 自動消失 (3 秒)
- [ ] 底部顯示，不遮擋 Betslip 內容

**Figma Reference**:
- Node: `26428-71769` (Partial)

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - 轉換結果 UI 狀態
**Type**: Story  
**Story Points**: 2  
**Labels**: `ui`, `state`

**Description**:
實作轉換結果的各種 UI 狀態。

**Acceptance Criteria**:
- [ ] 完全成功: Betslip 正常顯示所有 selections
- [ ] 部分成功: Betslip 顯示 + PartialErrorToast
- [ ] 完全失敗: 顯示 1.0.6 Error UI

**Figma Reference**:
- Node: `26428-71768` (Success)
- Node: `26428-71769` (Partial)
- Node: `26769-88871` (Error)

---

### Day 4: Tooltip + 錯誤處理 (01/20)

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - Tooltip 元件
**Type**: Story  
**Story Points**: 2  
**Labels**: `ui`, `component`, `tooltip`

**Description**:
實作一次性說明 Tooltip。

**Acceptance Criteria**:
- [ ] 首次開啟包含 Widget 的頁面時顯示
- [ ] 點擊關閉後永久不再顯示
- [ ] 以 Device ID 記錄顯示狀態（使用 UserDefaults）
- [ ] 跨頁面同步（任一頁面關閉後，其他頁面也不再顯示）
- [ ] Tooltip 指向 Load Code Widget

**Reference**:
- TDD: `05_Module Sequence Diagram/Module Sequence Diagrams/04_tooltip_display_logic.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - 完整錯誤處理
**Type**: Story  
**Story Points**: 2  
**Labels**: `error-handling`

**Description**:
實作完整的錯誤處理邏輯。

**Acceptance Criteria**:
- [ ] Convert API 失敗: 顯示 API 錯誤訊息 (1.0.6 Error)
  - CODE_NOT_FOUND: "We couldn't find this booking code"
  - TIMEOUT: "Request timed out"
  - INTERNAL_ERROR: 通用錯誤訊息
- [ ] Liabilities API 失敗: 按照 Betslip 既有流程顯示錯誤 UI
- [ ] Betslip API 失敗: 按照 Betslip 既有流程顯示錯誤 UI
- [ ] 網路錯誤處理

**Reference**:
- TDD: `09_Error Handling/01_error_handling.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - TooltipStorageClient
**Type**: Task  
**Story Points**: 1  
**Labels**: `client`, `storage`

**Description**:
實作 Tooltip 顯示狀態的本地儲存。

**Acceptance Criteria**:
- [ ] 實作 `TooltipStorageClient` 使用 UserDefaults
- [ ] 儲存 key: 以 Device ID 為基礎
- [ ] 支援 `hasBeenDismissed()` 讀取
- [ ] 支援 `setDismissed()` 寫入

---

### Day 5: 測試 + Polish (01/21)

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - Unit Tests
**Type**: Task  
**Story Points**: 2  
**Labels**: `testing`, `unit-test`

**Description**:
撰寫核心邏輯的 Unit Tests。

**Acceptance Criteria**:
- [ ] `ConvertBookingCodeUseCase` tests
  - 成功轉換
  - 部分轉換
  - 轉換失敗
  - 網路錯誤
- [ ] `LoadBookingCodeSection.Feature` reducer tests
  - 輸入變更
  - 轉換成功/部分成功/失敗
  - Tooltip 邏輯
- [ ] `TooltipStorageClient` tests

**Reference**:
- TDD: `10_Test Scenarios/01_test_scenarios.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - UI Polish & Review
**Type**: Task  
**Story Points**: 2  
**Labels**: `polish`, `review`

**Description**:
最終 UI 調整和程式碼 Review。

**Acceptance Criteria**:
- [ ] 對照 Figma 檢查所有 UI 狀態
- [ ] 動畫和轉場效果
- [ ] Loading 狀態的提示文字
- [ ] Error 狀態的紅色邊框和錯誤訊息
- [ ] Code Review 修改
- [ ] 文件更新 (如有需要)

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - Integration Testing
**Type**: Task  
**Story Points**: 1  
**Labels**: `testing`, `integration`

**Description**:
整合測試確保完整流程正常運作。

**Acceptance Criteria**:
- [ ] 完整轉換流程 E2E 測試
- [ ] 與 Betslip 既有流程整合測試
- [ ] Tooltip 顯示邏輯測試
- [ ] 錯誤處理流程測試

---

## 📊 Sprint Burndown 追蹤

| Day | 完成 Tickets | 累計 SP | 剩餘 SP |
|-----|-------------|---------|---------|
| Day 1 | | | 25 |
| Day 2 | | | |
| Day 3 | | | |
| Day 4 | | | |
| Day 5 | | | 0 |

---

## 🚨 風險與阻塞

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| BE API 尚未完成 | 無法進行整合測試 | 使用 Mock Data 開發 |
| Figma Tooltip 設計不明確 | UI 實作延遲 | 提前與 UED 確認 |
| 既有 Betslip 流程不熟悉 | 整合困難 | Day 3 前先研究既有程式碼 |
| Device ID 取得方式 | Tooltip 儲存邏輯 | 確認使用 `identifierForVendor` |

---

## 📝 Daily Standup Template

```
### [日期] Standup

**昨天完成:**
- 

**今天計劃:**
- 

**阻塞:**
- 無 / 有: [描述]
```

---

## 🔗 相關連結

- **Epic**: [FOOTBALL-9161](https://jira.example.com/browse/FOOTBALL-9161)
- **Figma**: [Code-Converter](https://www.figma.com/design/SvcTlADMZ7gUPIa7nN2hT1/Code-Converter)
- **PRD**: `PRDs/01_PRD/01_06/Fcom_PRD_Booking_Code_Converter_01_06_zh-TW.md`
- **API Doc**: `Docs/API_Doc/Code_Converter_API_Doc.md`

---

## 📋 變更記錄

| 日期 | 變更內容 |
|------|----------|
| 2025-01-14 | BE 新設計更新：移除 Bookie Selector、Config API；簡化 Convert API；新增 Tooltip |
| 2025-01-07 | 初版建立 |
