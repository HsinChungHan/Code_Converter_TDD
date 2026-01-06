# Jira 同步疑難排解指南

本文件說明常見的錯誤和解決方法。

---

## 常見錯誤

### 1. 401 Unauthorized - "You do not have permission to create issues in this project"

**錯誤訊息**：
```
401 Client Error: Unauthorized for url: https://opennetltd.atlassian.net/rest/api/3/issue
回應: {"errorMessages":["You do not have permission to create issues in this project."],"errors":{}}
```

**原因**：
- 使用的 Jira 帳號（`JIRA_EMAIL`）沒有在 `FOOTBALL` Project 中建立 Issue 的權限

**解決方法**：

#### 方法 1：檢查並取得權限

1. 登入 Jira
2. 進入 `FOOTBALL` Project
3. 嘗試手動建立一個 Issue
4. 如果無法建立，請聯繫 Project Administrator 授予權限

#### 方法 2：使用有權限的帳號

1. 確認哪個 Jira 帳號有權限在 `FOOTBALL` Project 中建立 Issue
2. 使用該帳號的 Email 和 API Token 更新 `.env` 檔案

#### 方法 3：檢查 Project 角色

1. 進入 `FOOTBALL` Project → **Project settings**
2. 查看 **People** 區塊
3. 確認您的帳號是否有以下角色之一：
   - **Administrators**
   - **Developers**
   - **Users**（需要建立 Issue 的權限）

---

### 2. 無法取得用戶 accountId

**錯誤訊息**：
```
⚠️  無法取得受託人 accountId (reed.hsin@fortball.com)
⚠️  無法取得回報者 accountId (reed.hsin@fortball.com)
```

**原因**：
- Email 地址在 Jira 中不存在
- Email 地址拼寫錯誤
- 用戶尚未被加入 Jira

**解決方法**：

#### 方法 1：確認正確的 Email

1. 登入 Jira
2. 點擊右上角頭像 → **Account settings**
3. 查看 **Email** 欄位，確認正確的 Email 地址

#### 方法 2：手動查詢 accountId

執行以下腳本查詢 accountId：

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

# 查詢當前用戶
url = f"{JIRA_URL}/rest/api/3/myself"
headers = {"Accept": "application/json"}
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

response = requests.get(url, headers=headers, auth=auth)
user_info = response.json()

print(f"Email: {user_info.get('emailAddress')}")
print(f"Account ID: {user_info.get('accountId')}")
print(f"Display Name: {user_info.get('displayName')}")
```

#### 方法 3：直接使用 accountId

如果知道 accountId，可以直接在 `.env` 中設定：

```bash
# .env
ASSIGNEE_ACCOUNT_ID=557058:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
REPORTER_ACCOUNT_ID=557058:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

然後修改腳本使用 `ASSIGNEE_ACCOUNT_ID` 和 `REPORTER_ACCOUNT_ID`。

#### 方法 4：不設定受託人和回報者

如果無法找到 accountId，Issue 仍會建立，但不會設定受託人和回報者。後續可以在 Jira UI 中手動設定。

---

### 3. 父系 Issue 不存在

**錯誤訊息**：
```
400 Bad Request
回應: {"errorMessages":["Parent issue FOOTBALL-8686 does not exist."],"errors":{}}
```

**原因**：
- 父系 Issue Key `FOOTBALL-8686` 不存在
- 父系 Issue 已被刪除

**解決方法**：

1. 確認父系 Issue 是否存在：
   - 訪問 `https://opennetltd.atlassian.net/browse/FOOTBALL-8686`
   - 如果無法訪問，表示 Issue 不存在或沒有權限

2. 如果 Issue 不存在：
   - 建立新的父系 Issue
   - 或移除 `PARENT_ISSUE_KEY` 設定（不設定父系）

3. 如果 Issue 存在但無法訪問：
   - 確認您有該 Issue 的查看權限

---

### 4. Issue Type 不存在

**錯誤訊息**：
```
400 Bad Request
回應: {"errorMessages":["The issue type 'Task' is not available for this project."],"errors":{}}
```

**原因**：
- Project 中沒有 `Task` 這個 Issue Type
- Project 的 Issue Type 設定不同

**解決方法**：

1. 查詢 Project 可用的 Issue Type：

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

url = f"{JIRA_URL}/rest/api/3/project/{JIRA_PROJECT_KEY}"
headers = {"Accept": "application/json"}
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

response = requests.get(url, headers=headers, auth=auth)
project_info = response.json()

print("可用的 Issue Types:")
for issue_type in project_info.get("issueTypes", []):
    print(f"  - {issue_type.get('name')} (id: {issue_type.get('id')})")
```

2. 根據查詢結果，修改腳本中的 `ISSUE_TYPE_MAP` 或直接使用正確的 Issue Type 名稱。

---

## 測試連線

執行以下腳本測試 Jira 連線和權限：

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

headers = {"Accept": "application/json"}
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

# 測試 1：查詢當前用戶
print("測試 1：查詢當前用戶")
try:
    url = f"{JIRA_URL}/rest/api/3/myself"
    response = requests.get(url, headers=headers, auth=auth)
    response.raise_for_status()
    user_info = response.json()
    print(f"✅ 連線成功！")
    print(f"   使用者：{user_info.get('displayName')}")
    print(f"   Email：{user_info.get('emailAddress')}")
    print(f"   Account ID：{user_info.get('accountId')}")
except Exception as e:
    print(f"❌ 連線失敗：{e}")

print()

# 測試 2：查詢 Project
print("測試 2：查詢 Project")
try:
    url = f"{JIRA_URL}/rest/api/3/project/{JIRA_PROJECT_KEY}"
    response = requests.get(url, headers=headers, auth=auth)
    response.raise_for_status()
    project_info = response.json()
    print(f"✅ Project 存在！")
    print(f"   Project Key：{project_info.get('key')}")
    print(f"   Project 名稱：{project_info.get('name')}")
    print(f"   可用的 Issue Types：")
    for issue_type in project_info.get("issueTypes", []):
        print(f"     - {issue_type.get('name')}")
except Exception as e:
    print(f"❌ Project 不存在或無法存取：{e}")
    if hasattr(e, 'response') and e.response:
        print(f"   回應：{e.response.text}")

print()

# 測試 3：測試建立 Issue 權限
print("測試 3：測試建立 Issue 權限")
try:
    url = f"{JIRA_URL}/rest/api/3/issue"
    test_issue = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": "測試 Issue（請刪除）",
            "issuetype": {"name": "Task"},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "這是一個測試 Issue，請刪除"}]
                }]
            }
        }
    }
    response = requests.post(url, json=test_issue, headers=headers, auth=auth)
    response.raise_for_status()
    result = response.json()
    print(f"✅ 可以建立 Issue！")
    print(f"   建立的 Issue Key：{result.get('key')}")
    print(f"   ⚠️  請手動刪除這個測試 Issue：{result.get('key')}")
except Exception as e:
    print(f"❌ 無法建立 Issue：{e}")
    if hasattr(e, 'response') and e.response:
        print(f"   回應：{e.response.text}")
```

---

## 快速檢查清單

在執行同步腳本之前，請確認：

- [ ] Jira URL 正確（從瀏覽器網址列確認）
- [ ] Jira Email 正確（用於 API 認證的帳號）
- [ ] Jira API Token 正確（從 Jira Account Settings 取得）
- [ ] Project Key 正確（從 URL 或 Issue Key 確認）
- [ ] 帳號有在 Project 中建立 Issue 的權限
- [ ] 父系 Issue 存在（如果設定了 `PARENT_ISSUE_KEY`）
- [ ] 受託人和回報者的 Email 正確（如果設定了）

---

**最後更新**：2024-11-21

