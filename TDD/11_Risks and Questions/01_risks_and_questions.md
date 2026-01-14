# Risks and Questions

## ⚠️ BE 新設計更新 (2025-01-14)

| 變更項目 | 說明 |
|----------|------|
| **移除 Config API 相關問題** | Provider Config API 已廢棄 |
| **移除 Bookie 選擇相關問題** | 不再需要選擇 Bookie/Country |
| **新增 Tooltip 相關問題** | 新增一次性 Tooltip 功能 |

---

## 待確認事項

### 1. 向後相容性

| 問題 | 背景 | 影響 | 建議 |
|------|------|------|------|
| `LoadCodeManager` 是否需要修改？ | 現有 `LoadBookingCodeSection.Feature` 依賴 `LoadCodeManager` | 如需修改可能影響其他使用者 | 保持 `LoadCodeManager` 不變，新邏輯走 UseCase |
| `enableCodeConverter` 預設值？ | 決定新功能的啟用策略 | 影響 rollout 計畫 | 建議預設 `false`，逐步開啟 |

---

### 2. API 相關

| 問題 | 背景 | 影響 | 建議 |
|------|------|------|------|
| `POST /orders/converter/code` 返回的 `shareCode` 是否只包含成功的 selections？ | 部分失敗時需要知道如何載入 Betslip | 影響 Betslip 顯示 | 與後端確認 |
| BE 如何識別 Provider？ | 新設計不需傳入 provider/country | 需確認識別邏輯 | 與後端確認 |
| API 最長等待時間？ | 轉換可能需要較長時間 | 影響 Timeout 設置 | 建議 30 秒 timeout |

---

### 3. UI/UX 相關

| 問題 | 背景 | 影響 | 建議 |
|------|------|------|------|
| Partial Failure Toast 顯示時長？ | 需要讓用戶注意到部分失敗 | 影響用戶感知 | 建議 3 秒自動消失 |
| Tooltip 內容？ | 需確認說明文字 | 影響用戶理解 | 與 UED 確認最終文案 |
| Tooltip 樣式規格？ | Figma 設計稿待補 | 影響 UI 實作 | 等待設計稿更新 |

---

### 4. Tooltip 相關

| 問題 | 背景 | 影響 | 建議 |
|------|------|------|------|
| Device ID 取得方式？ | 需要判斷是否同一裝置 | 影響 Tooltip 持久化 | 使用 `identifierForVendor` 或 UserDefaults |
| 跨 App 版本行為？ | 用戶更新 App 後是否重新顯示？ | 影響用戶體驗 | UserDefaults 會保留，不會重新顯示 |
| 重裝 App 行為？ | 用戶重裝後是否重新顯示？ | 影響用戶體驗 | UserDefaults 會重置，會重新顯示 |

---

### 5. 效能相關

| 問題 | 背景 | 影響 | 建議 |
|------|------|------|------|
| 轉換 API 最長耗時？ | PRD 提到可能需要 10 秒 | 影響 Loading 提示 | 顯示 "Conversion may take up to 10 seconds" 提示 |
| Timeout 設置？ | 需要合理的超時時間 | 影響錯誤處理 | 建議 30 秒 timeout |

---

## 風險評估

### 高風險

| 風險 | 描述 | 緩解措施 |
|------|------|----------|
| **原有功能 regression** | 擴展 `LoadBookingCodeSectionView` 可能影響首頁 Widget | 完整的單元測試 + `enableCodeConverter = false` 時完全走原有邏輯 |
| **API 格式不匹配** | DTO 定義與實際 API 不符 | 與後端同步 API 文檔，增加 Response 驗證 |

### 中風險

| 風險 | 描述 | 緩解措施 |
|------|------|----------|
| **Betslip 導航失敗** | 轉換成功但 Betslip 載入失敗 | 增加錯誤處理，回滾到 Error 狀態 |
| **Tooltip 跨入口同步** | 多個入口需要同步 Tooltip 狀態 | 使用統一的 TooltipStorage |

### 低風險

| 風險 | 描述 | 緩解措施 |
|------|------|----------|
| **UI 狀態不一致** | 快速操作可能導致狀態混亂 | TCA 保證狀態一致性 |
| **長時間 Loading** | 用戶可能離開頁面 | 提示文字 + 考慮背景處理 |

---

## 依賴項

### 外部依賴

| 依賴 | 狀態 | 負責團隊 | 備註 |
|------|------|----------|------|
| `POST /orders/converter/code` | ✅ 已確認 | Backend | 只需 bookingCode 參數 |
| ~~`GET /orders/converter/config/providerCountries`~~ | ❌ 廢棄 | Backend | 不再需要 |
| Figma 設計稿 | ⚠️ 待更新 | Design | Tooltip 設計待補 |

### 內部依賴

| 依賴 | 狀態 | 備註 |
|------|------|------|
| `BetslipRepository` | ✅ 既有 | 用於 Liabilities 檢查 |
| `LoadCodeManager` | ✅ 既有 | 保持不變，向後相容 |
| `UserDefaults` | ✅ 既有 | 用於 Tooltip 狀態儲存 |

---

## 開放性問題

### 產品層面

1. **Feature Flag 策略**：Code Converter 功能是否需要 Remote Config 控制開關？
2. **用戶分群**：是否只對特定國家/用戶開放？
3. **Analytics**：需要追蹤哪些 GA Events？

### 技術層面

1. **離線支援**：離線時是否需要 graceful degradation？
2. **深連結**：是否需要支援深連結直接帶入 Booking Code？
3. **Tooltip 動畫**：是否需要入場/出場動畫？

---

## 後續迭代考量

### Phase 2: OCR2Code（預留）

- 需要增加相機/圖片選擇功能
- 可能需要新的 UI 入口
- UseCase 可復用，只需新增 OCR 前處理

### Phase 3: Prompt2Code（預留）

- 需要整合 LLM/AI 服務
- 可能需要對話式 UI
- 考慮 Streaming Response

---

## Checklist（開發前確認）

- [x] 與後端確認 API Response 完整格式
- [x] 確認不再需要 Provider/Country 選擇
- [ ] 與設計確認 Tooltip 樣式規格
- [ ] 確認 Feature Flag 需求
- [ ] 確認 Analytics Events 清單
- [ ] 確認 Timeout 與重試策略

---

## 廢棄項目清單

| 項目 | 類型 | 原因 |
|------|------|------|
| Config API 相關問題 | 待確認事項 | API 已廢棄 |
| Bookie 選擇交互問題 | 待確認事項 | 不再需要選擇 |
| Provider Config 緩存問題 | 待確認事項 | 不再需要 Config |
| 多國家 Bookie UI 問題 | 待確認事項 | 不再需要選擇國家 |
