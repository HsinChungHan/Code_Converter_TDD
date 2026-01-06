# Jira 整合指南

本文件說明如何將 TDD Ticket 串接到 Jira 來建立開發 Ticket。

---

## 1. 前置需求

### 1.1 Jira 設定

- **Jira 帳號**：需要有建立 Issue 的權限
- **Jira Project Key**：例如 `PROJ`、`TDD`、`LIVECHAT` 等
- **Issue Type**：通常使用 `Task` 或 `Story`
- **Jira API Token**：用於 API 認證

### 1.2 取得 Jira API Token

1. 登入 Jira
2. 點擊右上角頭像 → **Account settings**
3. 左側選單選擇 **Security**
4. 找到 **API tokens** 區塊
5. 點擊 **Create API token**
6. 複製生成的 Token（只會顯示一次）

**⚠️ 安全注意事項**：
- API Token 是敏感資訊，請妥善保管
- **不要**將 Token 提交到 Git 倉庫
- **不要**在公開場合分享 Token
- 如果 Token 洩露，請立即在 Jira 中撤銷並重新生成

### 1.3 Jira API 端點

- **Jira Cloud**：`https://{your-domain}.atlassian.net/rest/api/3/issue`
- **Jira Server**：`https://{your-domain}/rest/api/2/issue`

---

## 2. 資料對應表

### 2.1 TDD Ticket → Jira Issue 欄位對應

| TDD Ticket 欄位 | Jira Issue 欄位 | 說明 | 必填 |
|----------------|---------------|------|------|
| **Ticket ID** | `key` | Jira 會自動生成，但可以設定 `summary` 前綴 | 否 |
| **標題** | `summary` | Issue 標題 | ✅ 是 |
| **類型** | `issuetype.name` | 通常使用 `Task` 或 `Story` | ✅ 是 |
| **優先級** | `priority.name` | `Highest` / `High` / `Medium` / `Low` | 是 |
| **所屬 Feature** | `customfield_XXXXX` 或 `labels` | 使用 Labels 或自訂欄位 | 否 |
| **依賴 Ticket** | `issuelinks` | 使用 `blocks` 或 `depends on` 連結 | 否 |
| **描述** | `description` | Issue 描述（Markdown 格式） | ✅ 是 |
| **需求** | `description` 的一部分 | 放在描述中 | 否 |
| **驗收條件** | `customfield_XXXXX` 或 `description` | 使用 Acceptance Criteria 欄位或放在描述中 | 否 |
| **相關文件** | `description` 的一部分 | 放在描述中 | 否 |
| **Story Point** | `customfield_XXXXX` | 使用 Story Points 自訂欄位 | 否 |
| **估時** | `timetracking.originalEstimate` | 使用時間追蹤功能 | 否 |

### 2.2 優先級對應

| TDD 優先級 | Jira 優先級 |
|----------|------------|
| **P0** | `Highest` |
| **P1** | `High` |
| **P2** | `Medium` |
| **P3** | `Low` |

### 2.3 Issue Type 建議

| TDD 類型 | Jira Issue Type | 說明 |
|---------|----------------|------|
| **Domain Model** | `Task` | 技術任務 |
| **API** | `Task` | 技術任務 |
| **Client** | `Task` | 技術任務 |
| **Repository** | `Task` | 技術任務 |
| **UseCase** | `Story` | 功能故事 |
| **Feature** | `Story` | 功能故事 |
| **View** | `Story` | 功能故事 |

---

## 3. Jira API 請求格式

### 3.1 建立 Issue 的基本格式

```json
{
  "fields": {
    "project": {
      "key": "PROJ"
    },
    "summary": "實作 Comment Entity",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "定義 Comment Entity Domain Model。"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "Highest"
    },
    "labels": [
      "PrematchComment",
      "Domain-Model"
    ],
    "customfield_10016": 1,
    "timetracking": {
      "originalEstimate": "0.3d"
    }
  }
}
```

### 3.2 使用 Markdown 格式的描述

Jira 支援多種描述格式，建議使用 **Atlassian Document Format (ADF)** 或 **Markdown**：

**Markdown 格式（簡化版）**：
```json
{
  "fields": {
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "定義 Comment Entity Domain Model。\n\n## 需求\n\n1. 定義 Comment 結構\n2. 實作 Identifiable 和 Equatable\n3. 定義所有必要欄位（id、content、likeCount、authorId 等）\n\n## 驗收條件\n\n- [ ] Comment Entity 定義完成\n- [ ] 所有欄位類型正確\n- [ ] Equatable 實作正確（透過 id 比較）\n- [ ] Unit Test 覆蓋率 ≥ 80%"
            }
          ]
        }
      ]
    }
  }
}
```

---

## 4. 自動化腳本範例

### 4.1 Python 腳本範例

建立 `scripts/sync_tickets_to_jira.py`：

```python
#!/usr/bin/env python3
"""
將 TDD Ticket 同步到 Jira
"""

import os
import json
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional

# Jira 設定
JIRA_URL = "https://your-domain.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_API_TOKEN = "your-api-token"
JIRA_PROJECT_KEY = "PROJ"

# 優先級對應
PRIORITY_MAP = {
    "P0": "Highest",
    "P1": "High",
    "P2": "Medium",
    "P3": "Low"
}

# Issue Type 對應
ISSUE_TYPE_MAP = {
    "Domain Model": "Task",
    "API": "Task",
    "Client": "Task",
    "Repository": "Task",
    "UseCase": "Story",
    "Feature": "Story",
    "View": "Story"
}


def parse_ticket_markdown(file_path: Path) -> Dict:
    """解析 TDD Ticket Markdown 文件"""
    content = file_path.read_text(encoding='utf-8')
    
    ticket = {
        "ticket_id": None,
        "title": None,
        "type": None,
        "priority": None,
        "feature": None,
        "dependencies": [],
        "story_point": None,
        "estimate": None,
        "description": "",
        "requirements": [],
        "acceptance_criteria": [],
        "related_files": []
    }
    
    # 解析 Ticket ID
    ticket_id_match = re.search(r'# (TDD-\d+):', content)
    if ticket_id_match:
        ticket["ticket_id"] = ticket_id_match.group(1)
    
    # 解析表格資訊
    table_match = re.search(r'\| \*\*Ticket ID\*\* \| (.+?) \|', content)
    if table_match:
        ticket["ticket_id"] = table_match.group(1).strip()
    
    # 解析標題
    title_match = re.search(r'\| \*\*標題\*\* \| (.+?) \|', content)
    if title_match:
        ticket["title"] = title_match.group(1).strip()
    
    # 解析類型
    type_match = re.search(r'\| \*\*類型\*\* \| (.+?) \|', content)
    if type_match:
        ticket["type"] = type_match.group(1).strip()
    
    # 解析優先級
    priority_match = re.search(r'\| \*\*優先級\*\* \| (.+?) \|', content)
    if priority_match:
        ticket["priority"] = priority_match.group(1).strip()
    
    # 解析所屬 Feature
    feature_match = re.search(r'\| \*\*所屬 Feature\*\* \| (.+?) \|', content)
    if feature_match:
        ticket["feature"] = feature_match.group(1).strip()
    
    # 解析依賴 Ticket
    deps_match = re.search(r'\| \*\*依賴 Ticket\*\* \| (.+?) \|', content)
    if deps_match:
        deps_str = deps_match.group(1).strip()
        if deps_str and deps_str != "-":
            ticket["dependencies"] = [d.strip() for d in deps_str.split(",")]
    
    # 解析 Story Point
    sp_match = re.search(r'\| \*\*Story Point\*\* \| (\d+) \|', content)
    if sp_match:
        ticket["story_point"] = int(sp_match.group(1))
    
    # 解析估時
    estimate_match = re.search(r'\| \*\*估時.*?\*\* \| 標準：(\d+(?:\.\d+)?) 天', content)
    if estimate_match:
        ticket["estimate"] = float(estimate_match.group(1))
    
    # 解析描述
    desc_match = re.search(r'## 描述\n\n(.+?)\n\n##', content, re.DOTALL)
    if desc_match:
        ticket["description"] = desc_match.group(1).strip()
    
    # 解析需求
    req_match = re.search(r'## 需求\n\n((?:\d+\. .+?\n)+)', content)
    if req_match:
        requirements = req_match.group(1).strip().split('\n')
        ticket["requirements"] = [r.strip() for r in requirements if r.strip()]
    
    # 解析驗收條件
    ac_match = re.search(r'## 驗收條件\n\n((?:- \[ \].+?\n)+)', content)
    if ac_match:
        criteria = ac_match.group(1).strip().split('\n')
        ticket["acceptance_criteria"] = [c.strip() for c in criteria if c.strip()]
    
    return ticket


def create_jira_description(ticket: Dict) -> Dict:
    """建立 Jira 描述格式（ADF）"""
    content = []
    
    # 描述段落
    if ticket["description"]:
        content.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": ticket["description"]}]
        })
    
    # 需求區塊
    if ticket["requirements"]:
        content.append({
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "需求"}]
        })
        for req in ticket["requirements"]:
            content.append({
                "type": "bulletList",
                "content": [{
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": req}]
                    }]
                }]
            })
    
    # 驗收條件區塊
    if ticket["acceptance_criteria"]:
        content.append({
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "驗收條件"}]
        })
        for ac in ticket["acceptance_criteria"]:
            content.append({
                "type": "bulletList",
                "content": [{
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": ac}]
                    }]
                }]
            })
    
    return {
        "type": "doc",
        "version": 1,
        "content": content
    }


def create_jira_issue(ticket: Dict) -> Optional[str]:
    """在 Jira 建立 Issue"""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    # 建立 Issue 資料
    issue_data = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": ticket["title"],
            "description": create_jira_description(ticket),
            "issuetype": {"name": ISSUE_TYPE_MAP.get(ticket["type"], "Task")},
            "priority": {"name": PRIORITY_MAP.get(ticket["priority"], "Medium")},
            "labels": []
        }
    }
    
    # 加入 Feature Label
    if ticket["feature"]:
        issue_data["fields"]["labels"].append(ticket["feature"])
        issue_data["fields"]["labels"].append(ticket["type"].replace(" ", "-"))
    
    # 加入 Story Point（需要知道自訂欄位 ID）
    # issue_data["fields"]["customfield_10016"] = ticket["story_point"]
    
    # 加入時間估時
    if ticket["estimate"]:
        issue_data["fields"]["timetracking"] = {
            "originalEstimate": f"{ticket['estimate']}d"
        }
    
    # 發送請求
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.post(url, json=issue_data, headers=headers, auth=auth)
        response.raise_for_status()
        
        result = response.json()
        issue_key = result.get("key")
        print(f"✅ 建立 Issue: {issue_key} - {ticket['title']}")
        return issue_key
    except requests.exceptions.RequestException as e:
        print(f"❌ 建立 Issue 失敗: {ticket['title']}")
        print(f"   錯誤: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   回應: {e.response.text}")
        return None


def create_issue_links(issue_key: str, dependencies: List[str], jira_issue_map: Dict[str, str]):
    """建立 Issue 之間的連結"""
    if not dependencies:
        return
    
    url = f"{JIRA_URL}/rest/api/3/issueLink"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    for dep in dependencies:
        # 假設依賴的 Ticket 已經建立，並有對應的 Jira Issue Key
        if dep in jira_issue_map:
            link_data = {
                "type": {"name": "Blocks"},
                "inwardIssue": {"key": issue_key},
                "outwardIssue": {"key": jira_issue_map[dep]}
            }
            
            try:
                response = requests.post(url, json=link_data, headers=headers, auth=auth)
                response.raise_for_status()
                print(f"✅ 建立連結: {jira_issue_map[dep]} blocks {issue_key}")
            except requests.exceptions.RequestException as e:
                print(f"❌ 建立連結失敗: {dep} -> {issue_key}")
                print(f"   錯誤: {e}")


def main():
    """主函數"""
    # 讀取所有 Ticket 文件
    tickets_dir = Path("output/LiveChat&PrematchComment/12_Tickets")
    
    # 按照依賴順序處理 Ticket
    ticket_files = []
    for subdir in ["01_domain_model", "02_api", "03_client", "04_repository", 
                   "05_usecase", "06_feature", "07_view"]:
        subdir_path = tickets_dir / subdir
        if subdir_path.exists():
            ticket_files.extend(subdir_path.glob("*.md"))
    
    # 解析所有 Ticket
    tickets = []
    for file_path in sorted(ticket_files):
        ticket = parse_ticket_markdown(file_path)
        tickets.append((file_path, ticket))
    
    # 建立 Jira Issue 並記錄對應關係
    jira_issue_map = {}  # TDD Ticket ID -> Jira Issue Key
    
    for file_path, ticket in tickets:
        issue_key = create_jira_issue(ticket)
        if issue_key and ticket["ticket_id"]:
            jira_issue_map[ticket["ticket_id"]] = issue_key
    
    # 建立 Issue 連結
    for file_path, ticket in tickets:
        if ticket["ticket_id"] in jira_issue_map:
            create_issue_links(
                jira_issue_map[ticket["ticket_id"]],
                ticket["dependencies"],
                jira_issue_map
            )


if __name__ == "__main__":
    main()
```

### 4.2 使用方式

1. **安裝依賴**：
```bash
pip install requests python-dotenv
```

2. **建立 `.env` 檔案**（不要提交到 Git）：
```bash
# .env
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
JIRA_PROJECT_KEY=PROJ
```

3. **更新腳本以讀取環境變數**：
```python
from dotenv import load_dotenv
import os

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
```

4. **執行腳本**：
```bash
python scripts/sync_tickets_to_jira.py
```

**⚠️ 重要**：
- 確保 `.env` 檔案已加入 `.gitignore`
- 不要將真實的 API Token 寫入代碼或配置文件

---

## 5. 手動建立方式

### 5.1 使用 Jira UI

1. 登入 Jira
2. 選擇對應的 Project
3. 點擊 **Create** 按鈕
4. 填入以下資訊：
   - **Summary**：Ticket 標題
   - **Issue Type**：Task 或 Story
   - **Priority**：對應的優先級
   - **Description**：Ticket 描述、需求、驗收條件
   - **Labels**：Feature 名稱、Ticket 類型
   - **Story Points**：Story Point 數值
   - **Original Estimate**：估時（例如：0.3d）

### 5.2 使用 Jira CSV 匯入

1. 準備 CSV 檔案（範例格式）：

```csv
Summary,Issue Type,Priority,Description,Labels,Story Points,Original Estimate
實作 Comment Entity,Task,Highest,"定義 Comment Entity Domain Model。",PrematchComment Domain-Model,1,0.3d
實作 CommentMeta Entity,Task,Highest,"定義 CommentMeta Entity Domain Model。",PrematchComment Domain-Model,1,0.3d
```

2. 在 Jira 中選擇 **Import** → **CSV**

---

## 6. 需要的資料清單

### 6.1 必備資料

- ✅ **Jira URL**：Jira 實例的網址
- ✅ **Jira Email**：Jira 帳號 Email
- ✅ **Jira API Token**：API 認證 Token
- ✅ **Jira Project Key**：目標 Project 的 Key
- ✅ **Ticket 標題**：每個 Ticket 的標題
- ✅ **Ticket 描述**：每個 Ticket 的描述內容

### 6.2 選填資料

- ⚪ **Issue Type**：預設為 Task 或 Story
- ⚪ **Priority**：預設為 Medium
- ⚪ **Labels**：Feature 名稱、Ticket 類型
- ⚪ **Story Points**：需要知道自訂欄位 ID
- ⚪ **Original Estimate**：時間估時
- ⚪ **Issue Links**：依賴關係連結

### 6.3 自訂欄位 ID 查詢

如果需要使用 Story Points 等自訂欄位，需要先查詢欄位 ID：

```python
import requests

url = f"{JIRA_URL}/rest/api/3/field"
headers = {"Accept": "application/json"}
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

response = requests.get(url, headers=headers, auth=auth)
fields = response.json()

# 尋找 Story Points 欄位
for field in fields:
    if "Story Points" in field.get("name", ""):
        print(f"Story Points 欄位 ID: {field['id']}")
```

---

## 7. 最佳實踐

### 7.1 批次建立

- 先建立所有 Issue，再建立 Issue Links
- 按照依賴順序建立（Domain Model → API → Client → Repository → UseCase → Feature → View）

### 7.2 錯誤處理

- 記錄建立失敗的 Ticket
- 提供重試機制
- 驗證 API Token 和權限

### 7.3 更新機制

- 如果 Ticket 已存在，可以選擇更新或跳過
- 使用 Jira Issue Key 對應表來追蹤

### 7.4 測試建議

- 先在測試 Project 中建立少量 Issue 測試
- 確認欄位對應正確
- 確認依賴關係連結正確

---

## 8. 範例配置檔案

建立 `.env` 檔案（推薦方式，更安全）：

```bash
# .env
JIRA_URL=https://opennetltd.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
JIRA_PROJECT_KEY=FOOTBALL

# 受託人和回報者設定
ASSIGNEE_EMAIL=reed.hsin@fortball.com
REPORTER_EMAIL=reed.hsin@fortball.com

# 父系 Issue Key（可選）
PARENT_ISSUE_KEY=FOOTBALL-8686
```

**⚠️ 注意**：`.env` 檔案應加入 `.gitignore`，不要提交到 Git。

### 9.1 Issue 欄位設定

腳本會自動設定以下欄位：

- **Issue Type**：固定為 `Task`（任務）
- **Assignee（受託人）**：從 `ASSIGNEE_EMAIL` 環境變數取得，自動查詢 accountId
- **Reporter（回報者）**：從 `REPORTER_EMAIL` 環境變數取得，自動查詢 accountId
- **Parent（父系）**：從 `PARENT_ISSUE_KEY` 環境變數取得（例如：`FOOTBALL-8686`）

**注意**：
- 如果無法找到用戶的 accountId，Issue 仍會建立，但不會設定受託人和回報者
- 父系 Issue Key 必須存在，否則會建立失敗

或使用 `jira_config.json`（不推薦，因為會將敏感資訊寫入文件）：

```json
{
  "jira": {
    "url": "https://your-domain.atlassian.net",
    "email": "your-email@example.com",
    "api_token": "your-api-token",
    "project_key": "PROJ"
  },
  "mappings": {
    "priority": {
      "P0": "Highest",
      "P1": "High",
      "P2": "Medium",
      "P3": "Low"
    },
    "issue_type": {
      "Domain Model": "Task",
      "API": "Task",
      "Client": "Task",
      "Repository": "Task",
      "UseCase": "Story",
      "Feature": "Story",
      "View": "Story"
    }
  },
  "custom_fields": {
    "story_points": "customfield_10016"
  }
}
```

---

## 9. 疑難排解

### 9.1 常見錯誤

**401 Unauthorized**：
- 檢查 API Token 是否正確
- 檢查 Email 是否正確

**403 Forbidden**：
- 檢查帳號是否有建立 Issue 的權限
- 檢查 Project 權限設定

**400 Bad Request**：
- 檢查 Issue Type 是否存在
- 檢查 Priority 名稱是否正確
- 檢查必填欄位是否都有提供

### 9.2 除錯技巧

- 使用 `--dry-run` 模式先測試，不實際建立 Issue
- 記錄完整的請求與回應
- 使用 Jira API 測試工具（如 Postman）先測試

---

## 10. 參考資源

- [Jira REST API 文件](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [建立 Issue API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-post)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)

---

**最後更新**：2024-11-21

