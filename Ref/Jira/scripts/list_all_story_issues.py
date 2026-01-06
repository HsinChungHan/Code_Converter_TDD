#!/usr/bin/env python3
"""
列出 Story FOOTBALL-8686 下的所有 Issues

使用方式：
python scripts/list_all_story_issues.py
"""

import requests
import os
from dotenv import load_dotenv
from typing import Dict, List
from collections import defaultdict

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

PARENT_KEY = "FOOTBALL-8686"


def get_all_child_issues(parent_key: str) -> List[Dict]:
    """取得所有子 Issues"""
    url = f"{JIRA_URL}/rest/api/3/search/jql"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    jql = f'parent = {parent_key} ORDER BY created ASC'
    payload = {
        "jql": jql,
        "maxResults": 1000
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
                timeout=30
            )
            if detail_response.status_code == 200:
                detailed_issues.append(detail_response.json())
        
        return detailed_issues
    except requests.exceptions.RequestException as e:
        print(f"❌ 查詢失敗：{e}")
        return []


def main():
    print(f"📋 查詢 Story {PARENT_KEY} 下的所有 Issues...\n")
    
    issues = get_all_child_issues(PARENT_KEY)
    
    if not issues:
        print("❌ 沒有找到任何 Issues")
        return
    
    print(f"✅ 找到 {len(issues)} 個 Issues\n")
    
    # 按類型分組
    by_type = defaultdict(list)
    by_status = defaultdict(list)
    by_summary = defaultdict(list)
    
    for issue in issues:
        key = issue.get("key")
        summary = issue.get("fields", {}).get("summary", "")
        issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "Unknown")
        status = issue.get("fields", {}).get("status", {}).get("name", "Unknown")
        
        by_type[issue_type].append(issue)
        by_status[status].append(issue)
        by_summary[summary].append(issue)
    
    # 統計資訊
    print("="*70)
    print("📊 統計資訊")
    print("="*70)
    print()
    
    print("按類型統計：")
    for issue_type, items in sorted(by_type.items()):
        print(f"  {issue_type}: {len(items)} 個")
    print()
    
    print("按狀態統計：")
    for status, items in sorted(by_status.items()):
        print(f"  {status}: {len(items)} 個")
    print()
    
    # 找出重複的 Issues（相同 summary）
    print("重複的 Issues（相同標題）：")
    duplicates = {summary: items for summary, items in by_summary.items() if len(items) > 1}
    if duplicates:
        for summary, items in sorted(duplicates.items()):
            print(f"  \"{summary[:50]}...\": {len(items)} 個")
            for item in items[:3]:
                key = item.get("key")
                status = item.get("fields", {}).get("status", {}).get("name", "")
                print(f"    - {key} ({status})")
            if len(items) > 3:
                print(f"    ... 還有 {len(items) - 3} 個")
            print()
    else:
        print("  （無）")
    print()
    
    # 列出所有 Issues
    print("="*70)
    print("📋 所有 Issues 清單")
    print("="*70)
    print()
    
    for i, issue in enumerate(issues, 1):
        key = issue.get("key")
        summary = issue.get("fields", {}).get("summary", "")
        issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "")
        status = issue.get("fields", {}).get("status", {}).get("name", "")
        created = issue.get("fields", {}).get("created", "")[:10] if issue.get("fields", {}).get("created") else ""
        
        print(f"{i:3d}. [{key}](https://opennetltd.atlassian.net/browse/{key})")
        print(f"     類型: {issue_type} | 狀態: {status} | 建立: {created}")
        print(f"     標題: {summary}")
        print()


if __name__ == "__main__":
    main()

