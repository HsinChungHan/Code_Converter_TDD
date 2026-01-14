# Phase 1 - Code2Code Sequence Diagram (Basic - Confluence 格式)

> **版本**：2 - 基礎版（Business Logic + API + App State）  
> **來源**：PRD (2025-01-06 版本) + API Doc + BE 新設計 (2025-01-14)  
> **範圍**：Phase 1 - Any Booking Code → Fcom Booking Code  
> **更新**：2025-01-14 - BE 新設計：移除 Provider/Country 選擇，新增 Tooltip

---

## ⚠️ BE 新設計更新 (2025-01-14)

| 變更項目 | 舊版 | 新版 |
|----------|------|------|
| Provider/Country 選擇 | 需先選擇 Bookie | ❌ 廢棄 |
| Config API | GET /orders/converter/config/providerCountries | ❌ 廢棄 |
| Convert API | {provider, country, bookingCode} | {bookingCode} |
| Bookie Selector Sheet | 需實作 | ❌ 廢棄 |
| Tooltip | 無 | 🆕 新增 |

---

## App 角色拆分說明

| 角色 | 說明 | 拆分依據 |
|------|------|----------|
| **Load Code Widget** | 主要輸入元件，負責 Code 輸入、狀態顯示、Tooltip | PRD 定義 |
| ~~**Bookie Selector Sheet**~~ | ~~Bottom Sheet 選擇器~~ | ❌ 廢棄 |
| **Betslip** | 投注單，負責載入轉換後的 selections | PRD 定義 |

---

## 主流程：Code2Code 轉換

{plantuml}
@startuml
actor User
box "Client Side" #LightBlue
    participant "Load Code Widget" as Widget
    participant Betslip
end box
participant "Backend" as BE

== 0. Tooltip 顯示 (首次使用) ==
alt 首次使用（未關閉過）
    Widget --> User : 顯示 Tooltip "Insert a booking code from any provider"
    User -> Widget : 點擊關閉 Tooltip
    Widget -> Widget : 儲存 Device ID（不再顯示）
else 已關閉過
    note over Widget : 不顯示 Tooltip
end

== 1. 初始化階段 ==
User -> Widget : 開啟首頁
Widget --> User : 顯示 Widget (Default 狀態)

== 2. 輸入 Booking Code ==
User -> Widget : 點擊輸入框
Widget --> User : 顯示 Focus 狀態 (綠色邊框)
User -> Widget : 輸入任意 Booking Code
Widget --> User : 顯示 Filled 狀態 (Load 按鈕啟用)

== 3. 轉換流程 ==
User -> Widget : 點擊 Load 按鈕
Widget --> User : 顯示 Loading 狀態
Widget -> BE : POST /orders/converter/code\n{bookingCode}

alt Convert API Success
    BE --> Widget : {shareCode, successCnt, failCnt}
    note over Widget : 記錄 failCnt
    
    == 4. Check Liabilities [既有流程] ==
    Widget -> BE : GET /bookingCode/{shareCode}/liabilities
    
    alt Liabilities API Success
        BE --> Widget : {isTrusted}
        
        == 5. Get Betslip Data [既有流程] ==
        Widget -> BE : GET /orders/share/{shareCode}
        
        alt Share API Success
            BE --> Widget : {selections}
            
            == 6. 彈出 Betslip ==
            Widget -> Betslip : Pop up Betslip
            Betslip --> User : 顯示 Betslip
            
            opt failCnt > 0
                Betslip --> User : 顯示 Toast "X selections failed"
            end
            
        else Share API Failure
            Widget --> User : 按照既有流程顯示錯誤 UI
        end
        
    else Liabilities API Failure
        Widget --> User : 按照既有流程顯示錯誤 UI
    end
    
else Convert API Error
    BE --> Widget : error
    Widget --> User : 顯示 Error 狀態
end

@enduml
{plantuml}

---

## API 調用順序

| 順序 | API | Method | 狀態 |
|:----:|-----|--------|------|
| ~~1~~ | ~~/orders/converter/config/providerCountries~~ | ~~GET~~ | ❌ 廢棄 |
| 1 | /orders/converter/code | POST | ✅ |
| 2 | /bookingCode/{shareCode}/liabilities | GET | ✅ 既有 |
| 3 | /orders/share/{shareCode} | GET | ✅ 既有 |

---

## 廢棄項目

- ❌ Bookie Selector Sheet
- ❌ Config API
- ❌ `provider` 參數
- ❌ `country` 參數
