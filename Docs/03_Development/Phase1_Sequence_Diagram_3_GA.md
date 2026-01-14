# Phase 1 - Code2Code Sequence Diagram (With GA)

> **版本**：2 - 含 GA 資訊  
> **更新**：2025-01-14

---

## ⚠️ BE 新設計更新 (2025-01-14)

此文件需根據 BE 新設計更新。請參考：

- [Phase1_Sequence_Diagram_1_Basic.md](./Phase1_Sequence_Diagram_1_Basic.md) - 基礎版

---

## 主要變更

| 變更項目 | 說明 |
|----------|------|
| **Config API 廢棄** | 不再需要 Config API 相關的 GA 事件 |
| **Bookie 選擇廢棄** | 不再需要 Bookie 選擇相關的 GA 事件 |
| **Tooltip 新增** | 需新增 Tooltip 相關的 GA 事件（待補充） |

---

## GA 事件（待更新）

| 事件 | 觸發時機 | 狀態 |
|------|----------|------|
| ~~`bookie_dropdown_tapped`~~ | ~~點擊 Bookie Dropdown~~ | ❌ 廢棄 |
| ~~`bookie_selected`~~ | ~~選擇 Bookie~~ | ❌ 廢棄 |
| `code_input_focused` | 輸入框聚焦 | ✅ |
| `load_button_tapped` | 點擊 Load 按鈕 | ✅ |
| `convert_success` | 轉換成功 | ✅ |
| `convert_error` | 轉換失敗 | ✅ |
| `tooltip_displayed` | Tooltip 顯示 | 🆕 待補充 |
| `tooltip_dismissed` | Tooltip 關閉 | 🆕 待補充 |
