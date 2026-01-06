# Risks and Questions

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
| Provider Config 更新頻率？ | 是否需要緩存 | 影響 API 調用次數 | 建議首次開啟 Sheet 時載入，後續使用緩存 |
| Provider Config 是否依賴用戶登入？ | 未登入用戶是否可用 | 影響 Guest 用戶體驗 | 與後端確認 |

---

### 3. UI/UX 相關

| 問題 | 背景 | 影響 | 建議 |
|------|------|------|------|
| 多國家 Bookie 的 UI 交互？ | 設計稿顯示雙欄選擇器 | 需確認是先選 Bookie 再選 Country，還是並列顯示 | 參考 Figma 設計 |
| Partial Failure Toast 顯示時長？ | 需要讓用戶注意到部分失敗 | 影響用戶感知 | 建議 3 秒自動消失 |
| 長 Bookie 名稱截斷策略？ | Dropdown 空間有限 | 影響可讀性 | 設計稿指定 12 字元後截斷 |

---

### 4. 效能相關

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
| **Provider Config 載入失敗** | 無法開啟 Bookie 選擇器 | 顯示錯誤 Toast，允許重試 |

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
| `GET /orders/converter/config/providerCountries` | 待確認 | Backend | 需確認 Response 格式 |
| `POST /orders/converter/code` | 待確認 | Backend | 需確認錯誤碼完整性 |
| Figma 設計稿 | ✅ 已提供 | Design | 已有 Node IDs |

### 內部依賴

| 依賴 | 狀態 | 備註 |
|------|------|------|
| `BetslipRepository` | ✅ 既有 | 用於 Liabilities 檢查 |
| `LoadCodeManager` | ✅ 既有 | 保持不變，向後相容 |
| `Region` enum | ⚠️ 可能需擴展 | 新增 CountryCode mapping |

---

## 開放性問題

### 產品層面

1. **Feature Flag 策略**：Code Converter 功能是否需要 Remote Config 控制開關？
2. **用戶分群**：是否只對特定國家/用戶開放？
3. **Analytics**：需要追蹤哪些 GA Events？

### 技術層面

1. **緩存策略**：Provider Config 是否需要持久化緩存？
2. **離線支援**：離線時是否需要 graceful degradation？
3. **深連結**：是否需要支援深連結直接帶入 Booking Code？

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

- [ ] 與後端確認 API Response 完整格式
- [ ] 與設計確認多國家 Bookie 選擇交互
- [ ] 確認 Feature Flag 需求
- [ ] 確認 Analytics Events 清單
- [ ] 確認 Timeout 與重試策略
