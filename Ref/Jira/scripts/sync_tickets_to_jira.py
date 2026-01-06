#!/usr/bin/env python3
"""
將 TDD Ticket 同步到 Jira

使用方式：
1. 安裝依賴：pip install requests python-dotenv
2. 建立 .env 檔案並填入 Jira 設定
3. 執行：python scripts/sync_tickets_to_jira.py
"""

import os
import re
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# Jira 設定（從環境變數讀取）
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

# 受託人和回報者設定
ASSIGNEE_EMAIL = os.getenv("ASSIGNEE_EMAIL", "reed.hsin@fortball.com")
REPORTER_EMAIL = os.getenv("REPORTER_EMAIL", "reed.hsin@fortball.com")

# 父系 Issue Key
PARENT_ISSUE_KEY = os.getenv("PARENT_ISSUE_KEY", "FOOTBALL-8686")

# 驗證必要環境變數
if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY]):
    print("❌ 錯誤：請設定以下環境變數：")
    print("   - JIRA_URL")
    print("   - JIRA_EMAIL")
    print("   - JIRA_API_TOKEN")
    print("   - JIRA_PROJECT_KEY")
    print("\n請建立 .env 檔案或設定環境變數")
    sys.exit(1)

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
    
    # 解析估時（標準估時）
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
    """建立 Jira 描述格式（ADF - Atlassian Document Format）"""
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
        req_items = []
        for req in ticket["requirements"]:
            req_items.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": req}]
                }]
            })
        content.append({
            "type": "bulletList",
            "content": req_items
        })
    
    # 驗收條件區塊
    if ticket["acceptance_criteria"]:
        content.append({
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "驗收條件"}]
        })
        ac_items = []
        for ac in ticket["acceptance_criteria"]:
            ac_items.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": ac}]
                }]
            })
        content.append({
            "type": "bulletList",
            "content": ac_items
        })
    
    return {
        "type": "doc",
        "version": 1,
        "content": content
    }


def get_user_account_id(email: str) -> Optional[str]:
    """根據 Email 取得 Jira 用戶的 accountId"""
    url = f"{JIRA_URL}/rest/api/3/user/search"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    # 嘗試多種查詢方式
    query_methods = [
        email,  # 直接使用 email
        email.split("@")[0],  # 使用 email 的用戶名部分
    ]
    
    for query in query_methods:
        params = {
            "query": query
        }
        
        try:
            response = requests.get(url, headers=headers, auth=auth, params=params)
            response.raise_for_status()
            
            users = response.json()
            if users and len(users) > 0:
                # 找到完全匹配的 email
                for user in users:
                    user_email = user.get("emailAddress", "")
                    if user_email and user_email.lower() == email.lower():
                        return user.get("accountId")
                # 如果沒有完全匹配，返回第一個結果
                if users:
                    return users[0].get("accountId")
        except requests.exceptions.RequestException as e:
            continue
    
    # 如果所有方法都失敗，嘗試使用當前登入用戶
    try:
        url = f"{JIRA_URL}/rest/api/3/myself"
        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()
        user_info = response.json()
        if user_info.get("emailAddress", "").lower() == email.lower():
            return user_info.get("accountId")
    except:
        pass
    
    return None


def create_jira_issue(ticket: Dict, assignee_account_id: Optional[str] = None, 
                     reporter_account_id: Optional[str] = None, 
                     parent_issue_key: Optional[str] = None,
                     dry_run: bool = False) -> Optional[str]:
    """在 Jira 建立 Issue"""
    url = f"{JIRA_URL}/rest/api/3/issue"
    
    # 建立 Issue 資料
    issue_data = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": ticket["title"],
            "description": create_jira_description(ticket),
            "issuetype": {"name": "任務"},  # 使用中文 Issue Type
            "priority": {"name": PRIORITY_MAP.get(ticket["priority"], "Medium")},
            "labels": []
        }
    }
    
    # 設定受託人
    if assignee_account_id:
        issue_data["fields"]["assignee"] = {"accountId": assignee_account_id}
    
    # 注意：reporter 欄位通常由 Jira 自動設定為建立 Issue 的用戶，無法手動設定
    # 如果需要設定回報者，需要在 Jira 的 Screen 配置中允許編輯 reporter 欄位
    
    # 設定父系（如果指定）
    if parent_issue_key:
        issue_data["fields"]["parent"] = {"key": parent_issue_key}
    
    # 加入 Feature Label
    if ticket["feature"]:
        # 將標籤中的空格和特殊字符替換為連字符（Jira 標籤不能包含空格）
        feature_label = ticket["feature"].replace(" ", "-").replace("&", "And")
        issue_data["fields"]["labels"].append(feature_label)
        type_label = ticket["type"].replace(" ", "-")
        issue_data["fields"]["labels"].append(type_label)
    
    # 加入時間估時
    if ticket["estimate"]:
        issue_data["fields"]["timetracking"] = {
            "originalEstimate": f"{ticket['estimate']}d"
        }
    
    if dry_run:
        print(f"🔍 [DRY RUN] 將建立 Issue:")
        print(f"   Summary: {ticket['title']}")
        print(f"   Type: 任務")
        print(f"   Priority: {PRIORITY_MAP.get(ticket['priority'], 'Medium')}")
        print(f"   Assignee: {assignee_account_id or 'N/A'}")
        print(f"   Reporter: 自動設定（建立 Issue 的用戶）")
        print(f"   Parent: {parent_issue_key or 'N/A'}")
        print(f"   Estimate: {ticket['estimate']}d" if ticket['estimate'] else "   Estimate: N/A")
        print(f"   JSON: {json.dumps(issue_data, indent=2, ensure_ascii=False)}")
        return f"DRY-RUN-{ticket['ticket_id']}"
    
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


def create_issue_links(issue_key: str, dependencies: List[str], jira_issue_map: Dict[str, str], dry_run: bool = False):
    """建立 Issue 之間的連結"""
    if not dependencies:
        return
    
    if dry_run:
        for dep in dependencies:
            if dep in jira_issue_map:
                print(f"🔍 [DRY RUN] 將建立連結: {jira_issue_map[dep]} blocks {issue_key}")
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
    import argparse
    
    parser = argparse.ArgumentParser(description="將 TDD Ticket 同步到 Jira")
    parser.add_argument("--dry-run", action="store_true", help="測試模式，不實際建立 Issue")
    args = parser.parse_args()
    
    # 讀取所有 Ticket 文件
    script_dir = Path(__file__).parent
    tickets_dir = script_dir.parent
    
    # 按照依賴順序處理 Ticket
    ticket_files = []
    for subdir in ["01_domain_model", "02_api", "03_client", "04_repository", 
                   "05_usecase", "06_feature", "07_view"]:
        subdir_path = tickets_dir / subdir
        if subdir_path.exists():
            ticket_files.extend(subdir_path.glob("*.md"))
    
    if not ticket_files:
        print(f"❌ 找不到 Ticket 文件，請確認路徑：{tickets_dir}")
        sys.exit(1)
    
    # 解析所有 Ticket
    tickets = []
    for file_path in sorted(ticket_files):
        ticket = parse_ticket_markdown(file_path)
        if ticket["ticket_id"]:
            tickets.append((file_path, ticket))
    
    print(f"📋 找到 {len(tickets)} 個 Ticket\n")
    
    if args.dry_run:
        print("🔍 DRY RUN 模式：不會實際建立 Issue\n")
    
    # 取得受託人和回報者的 accountId
    print("🔍 查詢用戶 accountId...")
    assignee_account_id = get_user_account_id(ASSIGNEE_EMAIL)
    reporter_account_id = get_user_account_id(REPORTER_EMAIL)
    
    if assignee_account_id:
        print(f"✅ 受託人 accountId: {assignee_account_id}")
    else:
        print(f"⚠️  無法取得受託人 accountId ({ASSIGNEE_EMAIL})")
    
    if reporter_account_id:
        print(f"✅ 回報者 accountId: {reporter_account_id}")
    else:
        print(f"⚠️  無法取得回報者 accountId ({REPORTER_EMAIL})")
    
    print()
    
    # 建立 Jira Issue 並記錄對應關係
    jira_issue_map = {}  # TDD Ticket ID -> Jira Issue Key
    
    for file_path, ticket in tickets:
        issue_key = create_jira_issue(
            ticket, 
            assignee_account_id=assignee_account_id,
            reporter_account_id=reporter_account_id,
            parent_issue_key=PARENT_ISSUE_KEY if PARENT_ISSUE_KEY else None,
            dry_run=args.dry_run
        )
        if issue_key and ticket["ticket_id"]:
            jira_issue_map[ticket["ticket_id"]] = issue_key
    
    # 建立 Issue 連結
    for file_path, ticket in tickets:
        if ticket["ticket_id"] in jira_issue_map:
            create_issue_links(
                jira_issue_map[ticket["ticket_id"]],
                ticket["dependencies"],
                jira_issue_map,
                dry_run=args.dry_run
            )
    
    if not args.dry_run:
        print(f"\n✅ 完成！共建立 {len(jira_issue_map)} 個 Issue")


if __name__ == "__main__":
    main()

