# Jira 設定快速指南

本文件幫助您快速找到並設定 Jira URL 和 Project Key。

---

## 1. Jira URL 是什麼？

**Jira URL** 是您登入 Jira 時使用的基礎網址。

### 意義

- Jira URL 是您的 Jira 實例的唯一識別
- 用於 API 請求的基礎網址
- 所有 API 請求都會基於這個 URL

### 如何找到

#### 方法 1：從瀏覽器網址列（最簡單）

1. 打開瀏覽器，登入 Jira
2. 查看網址列，通常格式為：
   ```
   https://{your-company}.atlassian.net
   ```
   或
   ```
   https://jira.{your-company}.com
   ```

**範例**：
- 如果網址是 `https://mycompany.atlassian.net` → Jira URL 就是 `https://mycompany.atlassian.net`
- 如果網址是 `https://jira.example.com` → Jira URL 就是 `https://jira.example.com`

#### 方法 2：從 Jira 設定

1. 登入 Jira
2. 點擊右上角頭像 → **Account settings**
3. 在個人資料頁面可以看到您的 Jira 實例網址

### 注意事項

- ✅ **正確格式**：`https://mycompany.atlassian.net`
- ❌ **錯誤格式**：`https://mycompany.atlassian.net/`（不要有尾部斜線）
- ❌ **錯誤格式**：`https://mycompany.atlassian.net/rest/api/3`（不需要 API 路徑）

---

## 2. Project Key 是什麼？

**Project Key** 是 Jira Project 的唯一識別碼，用於區分不同的 Project。

### 意義

- Project Key 是 Project 的簡短代碼（通常 2-10 個大寫字母）
- 每個 Issue 的 Key 都包含 Project Key（例如：`PROJ-123`）
- 用於 API 請求中指定要建立 Issue 的 Project

### 如何找到

#### 方法 1：從 URL 查看（最簡單）

1. 進入您要建立 Issue 的 Project
2. 查看瀏覽器網址列

**範例**：
- URL 為 `https://mycompany.atlassian.net/projects/PROJ` → Project Key 是 `PROJ`
- URL 為 `https://mycompany.atlassian.net/browse/TDD-123` → Project Key 是 `TDD`

#### 方法 2：從 Issue Key 推斷

1. 查看該 Project 中的任何 Issue
2. Issue Key 的格式為：`{PROJECT_KEY}-{ISSUE_NUMBER}`

**範例**：
- Issue Key 為 `PROJ-123` → Project Key 是 `PROJ`
- Issue Key 為 `TDD-456` → Project Key 是 `TDD`
- Issue Key 為 `LIVECHAT-789` → Project Key 是 `LIVECHAT`

#### 方法 3：從 Project 設定查看

1. 登入 Jira
2. 進入 Project
3. 點擊左側選單的 **Project settings**（齒輪圖示）
4. 在 **Details** 區塊可以看到 **Project key**

**截圖位置**：
```
Project Settings
  └─ Details
      └─ Project key: PROJ
```

### 常見的 Project Key 範例

| Project Key | 說明 |
|------------|------|
| `PROJ` | Project 的縮寫 |
| `TDD` | Technical Design Document |
| `LIVECHAT` | Live Chat Feature |
| `IOS` | iOS Development |
| `MOBILE` | Mobile App |
| `WEB` | Web Development |
| `API` | API Development |

### 注意事項

- Project Key 通常是大寫字母
- Project Key 一旦建立就無法修改
- 如果 Project Key 不存在，API 請求會失敗

---

## 3. 完整設定範例

### 情境 1：Jira Cloud

假設您的 Jira 網址是 `https://mycompany.atlassian.net`，Project Key 是 `PROJ`：

```bash
# .env
JIRA_URL=https://mycompany.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
JIRA_PROJECT_KEY=PROJ
```

### 情境 2：自訂網域的 Jira Server

假設您的 Jira 網址是 `https://jira.example.com`，Project Key 是 `TDD`：

```bash
# .env
JIRA_URL=https://jira.example.com
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
JIRA_PROJECT_KEY=TDD
```

---

## 4. 驗證設定是否正確

### 方法 1：使用 API 測試

建立一個測試腳本 `test_jira_connection.py`：

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

# 測試連線
url = f"{JIRA_URL}/rest/api/3/myself"
headers = {"Accept": "application/json"}
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

try:
    response = requests.get(url, headers=headers, auth=auth)
    response.raise_for_status()
    user_info = response.json()
    print(f"✅ 連線成功！")
    print(f"   使用者：{user_info.get('displayName')}")
    print(f"   Email：{user_info.get('emailAddress')}")
except requests.exceptions.RequestException as e:
    print(f"❌ 連線失敗：{e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"   回應：{e.response.text}")

# 測試 Project 是否存在
url = f"{JIRA_URL}/rest/api/3/project/{JIRA_PROJECT_KEY}"
try:
    response = requests.get(url, headers=headers, auth=auth)
    response.raise_for_status()
    project_info = response.json()
    print(f"✅ Project 存在！")
    print(f"   Project Key：{project_info.get('key')}")
    print(f"   Project 名稱：{project_info.get('name')}")
except requests.exceptions.RequestException as e:
    print(f"❌ Project 不存在或無法存取：{e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"   回應：{e.response.text}")
```

執行測試：

```bash
python test_jira_connection.py
```

### 方法 2：使用 curl 測試

```bash
# 測試連線
curl -u "your-email@example.com:your-api-token" \
  -H "Accept: application/json" \
  "https://mycompany.atlassian.net/rest/api/3/myself"

# 測試 Project
curl -u "your-email@example.com:your-api-token" \
  -H "Accept: application/json" \
  "https://mycompany.atlassian.net/rest/api/3/project/PROJ"
```

---

## 5. 常見問題

### Q1：我不知道我的 Jira URL 是什麼？

**A**：最簡單的方法是查看瀏覽器網址列。當您登入 Jira 時，網址列會顯示您的 Jira URL。

### Q2：我有多個 Project，應該用哪個 Project Key？

**A**：選擇您要建立 Issue 的 Project。如果您要為 TDD Ticket 建立 Issue，建議建立一個專門的 Project（例如：`TDD`）。

### Q3：Project Key 可以修改嗎？

**A**：不可以。Project Key 一旦建立就無法修改。如果 Project Key 不符合需求，需要建立新的 Project。

### Q4：如何建立新的 Project？

**A**：
1. 登入 Jira
2. 點擊左上角的 **Projects** → **Create project**
3. 選擇 Project 類型（例如：Software）
4. 選擇 Project 模板
5. 輸入 Project 名稱和 Key
6. 點擊 **Create**

### Q5：API 請求失敗，顯示 "Project not found"？

**A**：可能的原因：
- Project Key 輸入錯誤（注意大小寫）
- 您的帳號沒有該 Project 的存取權限
- Project 已被刪除或停用

### Q6：如何確認我的帳號有建立 Issue 的權限？

**A**：
1. 進入 Project
2. 嘗試手動建立一個 Issue
3. 如果可以建立，表示有權限
4. 如果無法建立，請聯繫 Project Administrator

---

## 6. 快速檢查清單

在執行同步腳本之前，請確認：

- [ ] 已找到正確的 Jira URL（從瀏覽器網址列）
- [ ] 已找到正確的 Project Key（從 URL 或 Issue Key）
- [ ] 已取得 Jira API Token
- [ ] 已建立 `.env` 檔案並填入所有資訊
- [ ] 已確認 `.env` 檔案已加入 `.gitignore`
- [ ] 已測試連線（使用測試腳本或 curl）
- [ ] 已確認帳號有建立 Issue 的權限

---

**最後更新**：2024-11-21

