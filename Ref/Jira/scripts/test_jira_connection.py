#!/usr/bin/env python3
"""
測試 Jira 連線和權限

使用方式：
python scripts/test_jira_connection.py
"""

import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

if not all([JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
    print("❌ 錯誤：請設定 JIRA_URL、JIRA_EMAIL、JIRA_API_TOKEN")
    sys.exit(1)

headers = {"Accept": "application/json"}
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

print("=== Jira 連線診斷 ===\n")
print(f"Jira URL: {JIRA_URL}")
print(f"Jira Email: {JIRA_EMAIL}")
print(f"API Token: {'*' * 20}...{JIRA_API_TOKEN[-10:] if len(JIRA_API_TOKEN) > 10 else '***'}")
print(f"Project Key: {JIRA_PROJECT_KEY}")
print()

# 測試 1：基本連線
print("1. 測試基本連線（查詢當前用戶）")
try:
    url = f"{JIRA_URL}/rest/api/3/myself"
    response = requests.get(url, headers=headers, auth=auth, timeout=10)
    response.raise_for_status()
    user_info = response.json()
    print(f"   ✅ 連線成功！")
    print(f"   使用者：{user_info.get('displayName')}")
    print(f"   Email：{user_info.get('emailAddress')}")
    print(f"   Account ID：{user_info.get('accountId')}")
    print()
    
    # 如果 Email 不匹配，提醒
    if user_info.get('emailAddress', '').lower() != JIRA_EMAIL.lower():
        print(f"   ⚠️  警告：設定的 Email ({JIRA_EMAIL}) 與登入帳號 ({user_info.get('emailAddress')}) 不同")
        print()
    
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print(f"   ❌ 認證失敗（401 Unauthorized）")
        print(f"   可能原因：")
        print(f"     1. API Token 不正確")
        print(f"     2. Email 地址不正確")
        print(f"     3. API Token 已過期或被撤銷")
        print(f"   回應：{e.response.text}")
    else:
        print(f"   ❌ HTTP 錯誤：{e.response.status_code}")
        print(f"   回應：{e.response.text}")
except Exception as e:
    print(f"   ❌ 連線失敗：{e}")
    sys.exit(1)

print()

# 測試 2：查詢 Project
if JIRA_PROJECT_KEY:
    print(f"2. 測試 Project 存取（{JIRA_PROJECT_KEY}）")
    try:
        url = f"{JIRA_URL}/rest/api/3/project/{JIRA_PROJECT_KEY}"
        response = requests.get(url, headers=headers, auth=auth, timeout=10)
        response.raise_for_status()
        project_info = response.json()
        print(f"   ✅ Project 存在！")
        print(f"   Project Key：{project_info.get('key')}")
        print(f"   Project 名稱：{project_info.get('name')}")
        print(f"   可用的 Issue Types：")
        for issue_type in project_info.get("issueTypes", [])[:5]:
            print(f"     - {issue_type.get('name')} (id: {issue_type.get('id')})")
        print()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"   ❌ Project 不存在（404 Not Found）")
            print(f"   可能原因：")
            print(f"     1. Project Key 不正確（應該是：{JIRA_PROJECT_KEY}）")
            print(f"     2. Project 已被刪除")
            print(f"     3. 您沒有該 Project 的存取權限")
            print(f"   建議：")
            print(f"     - 確認 Project Key 是否正確")
            print(f"     - 嘗試訪問：{JIRA_URL}/projects/{JIRA_PROJECT_KEY}")
        elif e.response.status_code == 403:
            print(f"   ❌ 沒有存取權限（403 Forbidden）")
            print(f"   您沒有 {JIRA_PROJECT_KEY} Project 的存取權限")
        else:
            print(f"   ❌ HTTP 錯誤：{e.response.status_code}")
            print(f"   回應：{e.response.text}")
    except Exception as e:
        print(f"   ❌ 查詢失敗：{e}")

print()

# 測試 3：測試建立 Issue 權限
if JIRA_PROJECT_KEY:
    print("3. 測試建立 Issue 權限")
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
        response = requests.post(url, json=test_issue, headers=headers, auth=auth, timeout=10)
        response.raise_for_status()
        result = response.json()
        print(f"   ✅ 可以建立 Issue！")
        print(f"   建立的 Issue Key：{result.get('key')}")
        print(f"   ⚠️  請手動刪除這個測試 Issue：{result.get('key')}")
        print(f"   連結：{JIRA_URL}/browse/{result.get('key')}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(f"   ❌ 權限不足（401 Unauthorized）")
            print(f"   您沒有在 {JIRA_PROJECT_KEY} Project 中建立 Issue 的權限")
            print(f"   回應：{e.response.text}")
        elif e.response.status_code == 400:
            print(f"   ❌ 請求錯誤（400 Bad Request）")
            print(f"   回應：{e.response.text}")
        else:
            print(f"   ❌ HTTP 錯誤：{e.response.status_code}")
            print(f"   回應：{e.response.text}")
    except Exception as e:
        print(f"   ❌ 建立失敗：{e}")

print()

# 測試 4：查詢用戶
ASSIGNEE_EMAIL = os.getenv("ASSIGNEE_EMAIL", "")
if ASSIGNEE_EMAIL:
    print(f"4. 測試查詢用戶 accountId（{ASSIGNEE_EMAIL}）")
    try:
        url = f"{JIRA_URL}/rest/api/3/user/search"
        params = {"query": ASSIGNEE_EMAIL}
        response = requests.get(url, headers=headers, auth=auth, params=params, timeout=10)
        response.raise_for_status()
        users = response.json()
        if users:
            print(f"   ✅ 找到 {len(users)} 個用戶")
            for user in users[:3]:
                email_match = "✅" if user.get("emailAddress", "").lower() == ASSIGNEE_EMAIL.lower() else "⚠️"
                print(f"   {email_match} {user.get('displayName')} ({user.get('emailAddress')})")
                print(f"      Account ID: {user.get('accountId')}")
        else:
            print(f"   ⚠️  找不到用戶：{ASSIGNEE_EMAIL}")
            print(f"   建議：使用當前登入用戶的 Account ID")
    except Exception as e:
        print(f"   ⚠️  查詢失敗：{e}")

print()
print("=== 診斷完成 ===")

