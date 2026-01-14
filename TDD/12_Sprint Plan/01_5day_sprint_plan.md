# Code Converter Phase 1 - 5 Day Sprint Plan

> **Sprint 期間**: 2025-01-07 (週二) ~ 2025-01-13 (週一，跳過週末)  
> **Epic**: FOOTBALL-9161 - Booking Code Converter  
> **開發者**: @Reed Hsin

---

## 📊 Sprint 總覽

| Day | 日期 | 主題 | Story Points |
|-----|------|------|--------------|
| Day 1 | 01/07 (二) | 基礎架構 + UI 骨架 | 5 |
| Day 2 | 01/08 (三) | Bookie Selector + Config API | 5 |
| Day 3 | 01/09 (四) | Convert API 整合 | 5 |
| Day 4 | 01/10 (五) | Betslip 串接 + 結果顯示 | 5 |
| Day 5 | 01/13 (一) | 錯誤處理 + 測試 + Polish | 5 |

**Total**: 25 Story Points

---

## 📋 Jira Tickets 詳細規劃

---

### Day 1: 基礎架構 + UI 骨架 (01/07)

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
實作 Load Code Widget 的主要容器視圖。

**Acceptance Criteria**:
- [ ] 實作 `LoadBookingCodeSectionView` 主視圖
  - 包含 `BookieDropdownView` placeholder
  - 包含 `BookingCodeInputView` placeholder
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

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - BookieDropdownView
**Type**: Story  
**Story Points**: 1  
**Labels**: `ui`, `view`, `component`

**Description**:
實作 Bookie 選擇下拉按鈕元件。

**Acceptance Criteria**:
- [ ] 顯示選中的 Bookie Logo
- [ ] 顯示 Bookie 名稱 (若無則顯示 "Select")
- [ ] 顯示下拉箭頭 icon
- [ ] 點擊觸發 `onTap` callback
- [ ] 固定寬度: 104

**Figma Reference**:
- Node: `26769-88873` (Default)

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - BookingCodeInputView
**Type**: Story  
**Story Points**: 1  
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
- [ ] 字型: `Font.b1_m`

**Figma Reference**:
- Node: `26769-88873` (Default)
- Node: `26769-88868` (Focus)
- Node: `26769-88863` (Typing)
- Node: `26769-88878` (Filled)
- Node: `26453-93276` (Loading)
- Node: `26453-93353` (Error)

---

### Day 2: Bookie Selector + Config API (01/08)

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - BookieSelectorSheet UI
**Type**: Story  
**Story Points**: 2  
**Labels**: `ui`, `view`, `sheet`

**Description**:
實作 Bookie 選擇器 Bottom Sheet。

**Acceptance Criteria**:
- [ ] Sheet 標題: "Select bookie"
- [ ] 可滾動的 Bookie 列表
- [ ] 支援單一國家 Bookie (直接選擇)
- [ ] 支援多國家 Bookie (展開選擇國家)
- [ ] 支援 ALL 國家 Provider (預設 "ALL")
- [ ] Submit 按鈕
- [ ] 底部漸層遮罩效果

**Figma Reference**:
- Node: `26753-64425` (開啟選單)
- Node: `26753-64480` (單一國家 Bookie)
- Node: `26753-64517` (多國家 Bookie)
- Node: `26921-96820` (ALL 國家 Provider)
- Node: `26753-85011` (結果 - 最終狀態)

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - LoadProviderConfigUseCase
**Type**: Story  
**Story Points**: 1  
**Labels**: `usecase`, `domain`

**Description**:
實作載入 Provider 設定的 UseCase。

**Acceptance Criteria**:
- [ ] Input: 無
- [ ] Output: `[ProviderConfig]`
- [ ] 調用 `CodeConverterRepository.fetchProviderConfig()`
- [ ] 錯誤處理: 回傳 `.failure(error)`

**API Reference**:
- `GET /orders/converter/config/providerCountries`

**Reference**:
- TDD: `07_UseCase Input and Output Model/01_usecase_input_output.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - CodeConverterRepository (Config)
**Type**: Story  
**Story Points**: 1  
**Labels**: `repository`, `data`

**Description**:
實作 Repository 層的 Config API 呼叫。

**Acceptance Criteria**:
- [ ] 實作 `fetchProviderConfig()` 方法
- [ ] DTO to Domain Model 轉換
- [ ] 依賴 `CodeConverterClient`

**Reference**:
- TDD: `03_Module Responsibility/01_module_responsibility.md`
- TDD: `08_API Spec and Mapping/02_dto_mapping.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - CodeConverterClient (Config API)
**Type**: Story  
**Story Points**: 1  
**Labels**: `client`, `network`

**Description**:
實作 Client 層的 Config API 網路請求。

**Acceptance Criteria**:
- [ ] 實作 `getProviderCountryConfig()` 方法
- [ ] Method: `GET`
- [ ] Endpoint: `/orders/converter/config/providerCountries`
- [ ] Response DTO: `ProviderCountryConfigResponse`

**Reference**:
- TDD: `08_API Spec and Mapping/01_api_spec.md`

---

### Day 3: Convert API 整合 (01/09)

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - ConvertBookingCodeUseCase
**Type**: Story  
**Story Points**: 1  
**Labels**: `usecase`, `domain`

**Description**:
實作轉換 Booking Code 的 UseCase。

**Acceptance Criteria**:
- [ ] Input: `ConvertBookingCodeInput` (provider, country, bookingCode)
- [ ] Output: `ConvertBookingCodeOutput` (shareCode, successCnt, failCnt)
- [ ] 調用 `CodeConverterRepository.convertCode()`
- [ ] 錯誤處理

**API Reference**:
- `POST /orders/converter/code`

**Reference**:
- TDD: `07_UseCase Input and Output Model/01_usecase_input_output.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - CodeConverterRepository (Convert)
**Type**: Story  
**Story Points**: 1  
**Labels**: `repository`, `data`

**Description**:
實作 Repository 層的 Convert API 呼叫。

**Acceptance Criteria**:
- [ ] 實作 `convertCode(input:)` 方法
- [ ] DTO to Domain Model 轉換
- [ ] 錯誤處理與回傳

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - CodeConverterClient (Convert API)
**Type**: Story  
**Story Points**: 1  
**Labels**: `client`, `network`

**Description**:
實作 Client 層的 Convert API 網路請求。

**Acceptance Criteria**:
- [ ] 實作 `convertCode(request:)` 方法
- [ ] Method: `POST`
- [ ] Endpoint: `/orders/converter/code`
- [ ] Request Body: `{ provider, country, bookingCode }`
- [ ] Response DTO: `Code2CodeResponse`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - TCA Feature 整合
**Type**: Story  
**Story Points**: 2  
**Labels**: `tca`, `feature`

**Description**:
整合 TCA Feature State 和 Action。

**Acceptance Criteria**:
- [ ] 實作 `LoadBookingCodeSection.Feature.State` 新增屬性
  - `providerConfigs: [ProviderConfig]`
  - `selectedProvider: ProviderConfig?`
  - `selectedCountry: String?`
  - `bookingCode: String`
  - `conversionState: ConversionState`
- [ ] 實作 `LoadBookingCodeSection.Feature.Action` 新增項目
  - `.loadProviderConfig`
  - `.providerConfigResponse(Result<...>)`
  - `.bookieDropdownTapped`
  - `.bookieSelected(ProviderConfig, String?)`
  - `.bookingCodeChanged(String)`
  - `.loadButtonTapped`
  - `.convertResponse(Result<...>)`
- [ ] Reducer 邏輯實作

**Reference**:
- TDD: `06_Feature State and Action (TCA)/01_feature_state_action.md`

---

### Day 4: Betslip 串接 + 結果顯示 (01/10)

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - Betslip 流程串接
**Type**: Story  
**Story Points**: 2  
**Labels**: `integration`, `betslip`

**Description**:
將轉換成功後的 shareCode 串接到既有 Betslip 流程。

**Acceptance Criteria**:
- [ ] Convert API 成功後:
  1. 呼叫 `GET /bookingCode/[shareCode]/liabilities` [既有流程]
  2. 呼叫 `GET /orders/share/[shareCode]` [既有流程]
  3. Pop up Betslip 並顯示轉換結果
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
- Node: `26453-93353` (Error)

---

### Day 5: 錯誤處理 + 測試 + Polish (01/13)

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - 完整錯誤處理
**Type**: Story  
**Story Points**: 2  
**Labels**: `error-handling`

**Description**:
實作完整的錯誤處理邏輯。

**Acceptance Criteria**:
- [ ] Config API 失敗: 顯示 "Config Load Failed" 錯誤
- [ ] Convert API 失敗: 顯示 API 錯誤訊息 (1.0.6 Error)
- [ ] Liabilities API 失敗: 按照 Betslip 既有流程顯示錯誤 UI
- [ ] Betslip API 失敗: 按照 Betslip 既有流程顯示錯誤 UI
- [ ] 網路錯誤處理
- [ ] Retry 機制 (如有需要)

**Reference**:
- TDD: `09_Error Handling/01_error_handling.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - Unit Tests
**Type**: Task  
**Story Points**: 2  
**Labels**: `testing`, `unit-test`

**Description**:
撰寫核心邏輯的 Unit Tests。

**Acceptance Criteria**:
- [ ] `LoadProviderConfigUseCase` tests
- [ ] `ConvertBookingCodeUseCase` tests
- [ ] `LoadBookingCodeSection.Feature` reducer tests
  - Config 載入成功/失敗
  - Bookie 選擇邏輯
  - 轉換成功/部分成功/失敗

**Reference**:
- TDD: `10_Test Scenarios/01_test_scenarios.md`

---

#### 🎫 FOOTBALL-XXXX: [iOS] Code Converter - UI Polish & Review
**Type**: Task  
**Story Points**: 1  
**Labels**: `polish`, `review`

**Description**:
最終 UI 調整和程式碼 Review。

**Acceptance Criteria**:
- [ ] 對照 Figma 檢查所有 UI 狀態
- [ ] 動畫和轉場效果
- [ ] Code Review 修改
- [ ] 文件更新 (如有需要)

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
| Figma 設計細節不明確 | UI 實作延遲 | 提前與 UED 確認 |
| 既有 Betslip 流程不熟悉 | 整合困難 | Day 4 前先研究既有程式碼 |

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





