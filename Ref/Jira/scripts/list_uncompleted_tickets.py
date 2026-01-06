#!/usr/bin/env python3
"""
列出所有未完成的 Tickets 及其指派狀態

使用方式：
python scripts/list_uncompleted_tickets.py
"""

import requests
import os
from dotenv import load_dotenv
from typing import List, Dict
from collections import defaultdict

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

PARENT_KEY = "FOOTBALL-8686"


def get_all_uncompleted_issues(parent_key: str) -> List[Dict]:
    """取得所有未完成的 Issues"""
    url = f"{JIRA_URL}/rest/api/3/search/jql"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    jql = f'parent = {parent_key} AND status != Done'
    payload = {
        "jql": jql,
        "fields": ["key", "summary", "status", "assignee", "issuetype", "parent"],
        "maxResults": 200
    }
    
    all_issue_ids = []
    next_page_token = None
    
    try:
        # 處理分頁
        while True:
            if next_page_token:
                payload["pageToken"] = next_page_token
            
            response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            issue_ids = [issue["id"] for issue in data.get("issues", [])]
            all_issue_ids.extend(issue_ids)
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token or data.get("isLast", False):
                break
        
        if not all_issue_ids:
            return []
        
        # 取得詳細資訊
        detailed_issues = []
        for issue_id in all_issue_ids:
            detail_url = f"{JIRA_URL}/rest/api/3/issue/{issue_id}"
            detail_response = requests.get(
                detail_url,
                headers={"Accept": "application/json"},
                auth=auth,
                params={"fields": "key,summary,status,assignee,issuetype,parent"},
                timeout=30
            )
            if detail_response.status_code == 200:
                detailed_issues.append(detail_response.json())
        
        return detailed_issues
    except requests.exceptions.RequestException as e:
        print(f"❌ 查詢失敗：{e}")
        return []


def main():
    print(f"📋 查詢 Story {PARENT_KEY} 下所有未完成的 Tickets...\n")
    
    issues = get_all_uncompleted_issues(PARENT_KEY)
    
    if not issues:
        print("✅ 沒有未完成的 Tickets")
        return
    
    print(f"✅ 找到 {len(issues)} 個未完成的 Tickets\n")
    
    # 分類
    main_tasks = []
    sub_tasks = []
    unassigned_main = []
    unassigned_sub = []
    
    for issue in issues:
        key = issue.get("key")
        summary = issue.get("fields", {}).get("summary", "")
        status = issue.get("fields", {}).get("status", {}).get("name", "")
        assignee = issue.get("fields", {}).get("assignee")
        issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "")
        parent = issue.get("fields", {}).get("parent")
        
        assignee_name = assignee.get("displayName", "未指派") if assignee else "未指派"
        assignee_email = assignee.get("emailAddress", "") if assignee else ""
        
        if parent:
            # Sub Task
            sub_tasks.append({
                "key": key,
                "summary": summary,
                "status": status,
                "assignee": assignee_name,
                "assignee_email": assignee_email,
                "parent_key": parent.get("key", ""),
                "issue_type": issue_type
            })
            if not assignee:
                unassigned_sub.append(key)
        else:
            # Main Task
            main_tasks.append({
                "key": key,
                "summary": summary,
                "status": status,
                "assignee": assignee_name,
                "assignee_email": assignee_email,
                "issue_type": issue_type
            })
            if not assignee:
                unassigned_main.append(key)
    
    # 顯示結果
    print("="*70)
    print("📊 未完成的 Tickets 統計")
    print("="*70)
    print(f"\nMain Tasks: {len(main_tasks)} 個（未指派：{len(unassigned_main)} 個）")
    print(f"Sub Tasks: {len(sub_tasks)} 個（未指派：{len(unassigned_sub)} 個）")
    print(f"總計: {len(issues)} 個（未指派：{len(unassigned_main) + len(unassigned_sub)} 個）")
    
    print("\n" + "="*70)
    print("📋 Main Tasks 清單")
    print("="*70)
    if main_tasks:
        for task in main_tasks:
            marker = "⚠️  " if task["key"] in unassigned_main else "✅ "
            print(f"{marker}{task['key']} - {task['summary'][:50]}...")
            print(f"    狀態: {task['status']} | 指派給: {task['assignee']}")
            if task['assignee_email']:
                print(f"    Email: {task['assignee_email']}")
            print()
    else:
        print("（無）")
    
    print("="*70)
    print("📋 Sub Tasks 清單")
    print("="*70)
    
    # 按 parent 分組
    by_parent = defaultdict(list)
    for task in sub_tasks:
        by_parent[task["parent_key"]].append(task)
    
    for parent_key in sorted(by_parent.keys()):
        tasks = by_parent[parent_key]
        print(f"\n📁 {parent_key} ({len(tasks)} 個 Sub Tasks):")
        for task in tasks:
            marker = "⚠️  " if task["key"] in unassigned_sub else "✅ "
            print(f"  {marker}{task['key']} - {task['summary'][:50]}...")
            print(f"      狀態: {task['status']} | 指派給: {task['assignee']}")
            if task['assignee_email']:
                print(f"      Email: {task['assignee_email']}")
    
    # 未指派的清單
    if unassigned_main or unassigned_sub:
        print("\n" + "="*70)
        print("⚠️  未指派的 Tickets")
        print("="*70)
        if unassigned_main:
            print(f"\nMain Tasks ({len(unassigned_main)} 個):")
            for key in unassigned_main:
                print(f"  - {key}")
        if unassigned_sub:
            print(f"\nSub Tasks ({len(unassigned_sub)} 個):")
            for key in unassigned_sub:
                print(f"  - {key}")
    else:
        print("\n✅ 所有 Tickets 都已指派")


if __name__ == "__main__":
    main()

