# Code Converter Phase 1 - Technical Design Document

> **最後更新**: 2025-01-14  
> **BE 新設計更新**：Config API 廢棄、不需 Provider/Country 選擇、新增 Tooltip

---

## 📋 目錄

| 章節 | 說明 | 路徑 |
|------|------|------|
| **00. Overview** | 功能概述、復用策略、實作優先級 | [01_overview.md](./00_Overview/01_overview.md) |
| **01. Integrated Flow** | 完整服務流程序列圖 | [01_full_integration_flow.md](./01_Integrated%20Service-Level%20Sequence%20Diagram/01_full_integration_flow.md) |
| **02. Architecture** | Clean Architecture 分層圖 | [01_clean_architecture_diagram.md](./02_Architecture/01_clean_architecture_diagram.md) |
| **03. Module Responsibility** | 各模組職責定義 | [01_module_responsibility.md](./03_Module%20Responsibility/01_module_responsibility.md) |
| **04. Domain Model** | Domain 模型定義 | [01_domain_model.md](./04_Domain%20Model/01_domain_model.md) |
| **05. Module Sequence** | 模組層級序列圖 | [Module Sequence Diagrams/](./05_Module%20Sequence%20Diagram/Module%20Sequence%20Diagrams/) |
| **05b. View Design Specs** | Figma 設計規格（顏色、字型、間距） | [02_view_design_specs.md](./05_Module%20Sequence%20Diagram/LoadBookingCodeSection/02_view_design_specs.md) |
| **05c. Tooltip 邏輯** | Tooltip 顯示邏輯 | [04_tooltip_display_logic.md](./05_Module%20Sequence%20Diagram/Module%20Sequence%20Diagrams/04_tooltip_display_logic.md) |
| **06. Feature State/Action** | TCA State & Action 定義 | [01_feature_state_action.md](./06_Feature%20State%20and%20Action%20(TCA)/01_feature_state_action.md) |
| **07. UseCase I/O** | UseCase 輸入輸出模型 | [01_usecase_input_output.md](./07_UseCase%20Input%20and%20Output%20Model/01_usecase_input_output.md) |
| **08. API Spec** | API 規格與 DTO Mapping | [01_api_spec.md](./08_API%20Spec%20and%20Mapping/01_api_spec.md) |
| **09. Error Handling** | 錯誤處理策略 | [01_error_handling.md](./09_Error%20Handling/01_error_handling.md) |
| **10. Test Scenarios** | 測試情境與範例 | [01_test_scenarios.md](./10_Test%20Scenarios/01_test_scenarios.md) |
| **11. Risks & Questions** | 風險評估與待確認事項 | [01_risks_and_questions.md](./11_Risks%20and%20Questions/01_risks_and_questions.md) |
| **12. Sprint Plan** | 5 天開發計劃與 Jira Tickets | [01_5day_sprint_plan.md](./12_Sprint%20Plan/01_5day_sprint_plan.md) |

---

## 🎯 核心設計決策

### 最大化復用 LoadBookingCodeSectionView（簡化版）

```
                    復用策略圖（BE 新設計）
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  LoadBookingCodeSectionView  ───擴展───►  LoadCodeWidgetView  │
│       └── BookingCodeInputView  ─擴展─►  BookingCodeInputView │
│                                              (+ 6 種狀態)  │
│                                                          │
│  LoadBookingCodeSection.Feature  ─擴展─►  LoadCodeWidget.Feature │
│                                                          │
│  新增：TooltipView (SwiftUI)                             │
│                                                          │
│  ❌ 廢棄：BookieDropdownView, BookieSelectorSheet        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 入口點替換

| 入口點 | 現有 | Phase 1 完成後 |
|--------|------|----------------|
| 首頁 Widget | `LoadBookingCodeSectionView` | `LoadCodeWidgetView` + Tooltip |
| Code Center | `LoadCodeViewWrapper` → UIKit | `LoadCodeWidgetView` (純 SwiftUI) |
| Betslip Empty | 既有空狀態 | 嵌入 `LoadCodeWidgetView` |

---

## 🏗️ 架構總覽

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                             │
│  LoadCodeWidgetView │ TooltipView │ PartialErrorToast       │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      Domain Layer (TCA)                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  LoadCodeWidget.Feature (擴展自 LoadBookingCodeSection) │ │
│  └──────────────────────────┬──────────────────────────────┘ │
│                             │                                │
│            ┌────────────────▼────────────────┐               │
│            │ ConvertBookingCodeUseCase       │               │
│            └────────────────┬────────────────┘               │
└─────────────────────────────┼────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────┐
│                   Data & Infrastructure                      │
│  ┌─────────────────────────┐  ┌────────────────────────┐     │
│  │ CodeConverterRepository │  │ BetslipRepository (既有) │     │
│  └───────────┬─────────────┘  └────────────┬───────────┘     │
│              │                             │                  │
│  ┌───────────▼─────────────┐  ┌────────────▼───────────┐     │
│  │  CodeConverterClient    │  │  BetslipClient (既有)   │     │
│  └───────────┬─────────────┘  └────────────────────────┘     │
│              │                                                │
│  ┌───────────▼─────────────┐  ┌────────────────────────┐     │
│  │  POST /converter/code   │  │  TooltipStorage        │     │
│  └─────────────────────────┘  │  (UserDefaults)        │     │
│                               └────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

---

## 📅 實作優先級

### Phase 1.1: 擴展現有元件
- [ ] 擴展 `LoadBookingCodeSection.State/Action/Feature`
- [ ] 擴展 `BookingCodeInputView`（6 種狀態）
- [ ] 新增 `TooltipView`
- [ ] 實作 `TooltipStorage` (UserDefaults)

### Phase 1.2: 新增 Data Layer
- [ ] 定義 Domain Models
- [ ] 實作 `CodeConverterRepository`
- [ ] 實作 `CodeConverterClient`
- [ ] 實作 `ConvertBookingCodeUseCase`

### Phase 1.3: 替換入口點
- [ ] 首頁 Widget：`enableCodeConverter = true` + Tooltip
- [ ] Code Center：替換為 `LoadCodeWidgetView` + Tooltip
- [ ] Betslip Empty：嵌入 `LoadCodeWidgetView` + Tooltip

### Phase 1.4: 清理
- [ ] 移除 `LoadCodeViewController`
- [ ] 移除 `LoadCodeViewController.xib`
- [ ] 移除 `LoadCodeViewWrapper`

---

## 📁 目錄結構

```
TDD/
├── README.md                                    # 本文件
├── index.md                                     # MkDocs 首頁
├── 00_Overview/
│   └── 01_overview.md
├── 01_Integrated Service-Level Sequence Diagram/
│   └── 01_full_integration_flow.md
├── 02_Architecture/
│   └── 01_clean_architecture_diagram.md
├── 03_Module Responsibility/
│   └── 01_module_responsibility.md
├── 04_Domain Model/
│   ├── 01_domain_model.md
│   └── 02_domain_model_uml.md
├── 05_Module Sequence Diagram/
│   ├── LoadBookingCodeSection/
│   │   ├── 01_view_implementation.md
│   │   ├── 02_view_design_specs.md
│   │   └── ...
│   └── Module Sequence Diagrams/
│       ├── 01_data_initialization_load_provider_config.md  ❌ 廢棄
│       ├── 02_data_interaction_convert_code.md
│       ├── 03_data_interaction_bookie_selection.md  ❌ 廢棄
│       └── 04_tooltip_display_logic.md  🆕 新增
├── 06_Feature State and Action (TCA)/
│   └── 01_feature_state_action.md
├── 07_UseCase Input and Output Model/
│   └── 01_usecase_input_output.md
├── 08_API Spec and Mapping/
│   ├── 01_api_spec.md
│   └── 02_dto_mapping.md
├── 09_Error Handling/
│   └── 01_error_handling.md
├── 10_Test Scenarios/
│   └── 01_test_scenarios.md
├── 11_Risks and Questions/
│   └── 01_risks_and_questions.md
└── 12_Sprint Plan/
    └── 01_5day_sprint_plan.md
```

---

## ⚠️ 廢棄項目清單

| 項目 | 類型 | 原因 |
|------|------|------|
| `BookieSelectorSheet` | UI | 不再需要選擇 Bookie |
| `BookieDropdownView` | UI | 不再需要 Dropdown |
| `LoadProviderConfigUseCase` | UseCase | Config API 已廢棄 |
| `GET /orders/converter/config/providerCountries` | API | BE 新設計不需要 |
| `ProviderConfig` | Domain Model | 不再需要 Config 資料 |
| `SelectedBookie` | Domain Model | 不再需要 Bookie 選擇 |
