# Module Sequence Diagrams - LoadBookingCodeSection

本資料夾包含 LoadBookingCodeSection Feature 的模組序列圖。

## ⚠️ BE 新設計更新 (2025-01)

| 變更項目 | 說明 |
|----------|------|
| **Config API 廢棄** | `01_data_initialization_load_provider_config.md` 已廢棄 |
| **Bookie Selection 廢棄** | `03_data_interaction_bookie_selection.md` 已廢棄 |
| **Tooltip 新增** | `04_tooltip_display_logic.md` 新增 |

---

## 文件列表

| 文件 | 類型 | 狀態 | 說明 |
|------|------|------|------|
| [01_data_initialization_load_provider_config.md](./01_data_initialization_load_provider_config.md) | Data Initialization | ❌ 廢棄 | ~~載入 Provider Config 流程~~ |
| [02_data_interaction_convert_code.md](./02_data_interaction_convert_code.md) | Data Interaction | ✅ 更新 | Code2Code 轉換流程 (簡化版) |
| [03_data_interaction_bookie_selection.md](./03_data_interaction_bookie_selection.md) | Data Interaction | ❌ 廢棄 | ~~Bookie 選擇流程~~ |
| [04_tooltip_display_logic.md](./04_tooltip_display_logic.md) | UI Logic | 🆕 新增 | Tooltip 顯示邏輯 |

---

## 簡化後的流程

```
舊流程（已廢棄）:
User → 選擇 Bookie → 輸入 Code → 轉換

新流程:
User → (Tooltip 首次顯示) → 輸入 Code → 轉換 → 原有 Load Code 流程
```

