# Phase 1 - Code2Code Sequence Diagram (Complete)

> **版本**：2 - 完整版（含所有資訊）  
> **更新**：2025-01-14

---

## ⚠️ BE 新設計更新 (2025-01-14)

此文件需根據 BE 新設計更新。請參考以下文件：

| 文件 | 說明 |
|------|------|
| [Phase1_Sequence_Diagram_1_Basic.md](./Phase1_Sequence_Diagram_1_Basic.md) | 基礎版（Business Logic + API） |
| [Phase1_Sequence_Diagram_2_Figma.md](./Phase1_Sequence_Diagram_2_Figma.md) | 含 Figma 資訊 |
| [Phase1_Sequence_Diagram_3_GA.md](./Phase1_Sequence_Diagram_3_GA.md) | 含 GA 資訊 |

---

## 主要變更

| 變更項目 | 舊版 | 新版 |
|----------|------|------|
| **Provider/Country 選擇** | 需先選擇 Bookie | ❌ 廢棄 |
| **Config API** | `GET /orders/converter/config/providerCountries` | ❌ 廢棄 |
| **Convert API** | `{provider, country, bookingCode}` | `{bookingCode}` |
| **Bookie Selector Sheet** | 需實作 | ❌ 廢棄 |
| **Tooltip** | 無 | 🆕 新增 |

---

## 簡化後的流程

```
舊流程（已廢棄）:
User → 選擇 Bookie → 輸入 Code → 轉換

新流程:
User → (Tooltip 首次顯示) → 輸入 Code → POST /orders/converter/code → 走原有 Load Code 流程
```
