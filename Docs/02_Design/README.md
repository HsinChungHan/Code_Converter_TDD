# 02_Design - 設計文件版本管理

> 此資料夾使用日期版本管理 Figma 設計文件

---

## 📁 資料夾結構

| 資料夾 | 日期 | 說明 |
|--------|------|------|
| `01_01/` | 2025-01-01 | 初版設計（需求變更前） |
| `01_09/` | 2025-01-09 | 需求調整後的新版設計 |

---

## 📝 版本變更紀錄

### 01_09 (2025-01-09) + 01_12 更新
- **變更原因**：需求調整，簡化 Bookie 選擇流程
- **API 狀態**：待 BE 討論後更新
- **主要變更**：
  - ❌ 移除 Bookie/Country 選擇器 (Bottom Sheet)
  - ❌ 移除 Bookie Dropdown
  - ❌ 移除 1.0.3 (Select Bookie) 和 1.0.4 (Type Done) 畫面
  - 🔄 按鈕文字 "Load" → "Import"
  - 🔄 Placeholder "Booking Code" → "Paste any booking code"
  - 🔄 Widget 位置移至 Quick Panel 下方 (Load Code Highlight)
  - ✅ 確認 Betslip 替換規則：轉換成功會替換既有 selections
  - ✅ 確認限制：僅支援足球賽事 (Can only convert football match)
  - 🆕 **One-Time Tooltip** (2025-01-12)：Feature 上線後顯示一次性提示
    - node-id: `27526:71304`
    - 文字: "Supports booking codes from many platforms"
    - 按 device ID 存儲，只顯示一次

### 01_01 (2025-01-01)
- **狀態**：已封存
- **內容**：
  - `Figma_Nodes_Phase1.md` - Figma node-id 清單
  - `Phase1_Design_Specs.md` - 設計規格（Design Tokens、元件規格）

---

## 🔗 Figma 檔案資訊

| 項目 | 值 |
|------|-----|
| **File Key** | `SvcTlADMZ7gUPIa7nN2hT1` |
| **File Name** | Code-Converter |
| **Base URL** | `https://www.figma.com/design/SvcTlADMZ7gUPIa7nN2hT1/Code-Converter` |

---

## 💡 如何新增版本

1. 創建新的日期資料夾（格式：`MM_DD`）
2. 複製上一版的檔案作為模板
3. 更新 node-id 和設計規格
4. 更新此 README 的版本變更紀錄

