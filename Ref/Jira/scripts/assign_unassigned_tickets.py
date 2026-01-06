#!/usr/bin/env python3
"""
將未指派的 Tickets 指派給指定用戶

使用方式：
python scripts/assign_unassigned_tickets.py [--assignee-email EMAIL] [--dry-run] [--force]
"""

import requests
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

PARENT_KEY = "FOOTBALL-8686"
DEFAULT_ASSIGNEE_EMAIL = "reed.hsin@football.com"


def get_account_id_by_email(email: str) -> Optional[str]:
    """根據 email 取得 Jira account ID"""
    url = f"{JIRA_URL}/rest/api/3/user/search"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    params = {
        "query": email,
        "maxResults": 50
    }
    
    try:
        response = requests.get(url, headers=headers, auth=auth, params=params, timeout=30)
        response.raise_for_status()
        users = response.json()
        
        # 尋找完全匹配的 email
        for user in users:
            if user.get("emailAddress", "").lower() == email.lower():
                return user.get("accountId")
        
        # 如果沒有完全匹配，返回第一個結果
        if users:
            return users[0].get("accountId")
        
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️  查詢用戶失敗：{e}")
        return None


def get_unassigned_issues(parent_key: str) -> List[Dict]:
    """取得所有未指派的 Issues"""
    url = f"{JIRA_URL}/rest/api/3/search/jql"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    # 查詢所有未完成且未指派的 Issues（包括 Main Tasks 和 Sub Tasks）
    jql = f'parent = {parent_key} AND status = Backlog AND assignee is EMPTY'
    payload = {
        "jql": jql,
        "fields": ["key", "summary", "status", "assignee", "issuetype"],
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
                params={"fields": "key,summary,status,assignee,issuetype"},
                timeout=30
            )
            if detail_response.status_code == 200:
                detailed_issues.append(detail_response.json())
        
        return detailed_issues
    except requests.exceptions.RequestException as e:
        print(f"❌ 查詢失敗：{e}")
        return []


def assign_issue(jira_key: str, account_id: str) -> bool:
    """指派 Issue 給指定用戶"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}/assignee"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    payload = {
        "accountId": account_id
    }
    
    try:
        response = requests.put(url, json=payload, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"⚠️  指派失敗 ({jira_key})：{e}")
        return False


def assign_unassigned_tickets(assignee_email: str, dry_run: bool = False, force: bool = False):
    """將未指派的 Tickets 指派給指定用戶"""
    print("📋 開始指派未指派的 Tickets...\n")
    
    if not dry_run and not force:
        try:
            confirm = input(f"⚠️  確定要將未指派的 Tickets 指派給 {assignee_email} 嗎？(yes/no): ")
            if confirm.lower() != "yes":
                print("❌ 操作已取消")
                return
        except EOFError:
            print("❌ 無法讀取輸入，請使用 --force 參數跳過確認")
            return
    
    # 取得 account ID
    print(f"正在查詢用戶 {assignee_email} 的 account ID...")
    account_id = get_account_id_by_email(assignee_email)
    
    if not account_id:
        print(f"❌ 找不到用戶 {assignee_email}")
        return
    
    print(f"✅ 找到用戶 account ID: {account_id}\n")
    
    # 取得未指派的 Issues
    print(f"正在查詢 Story {PARENT_KEY} 下未指派的 Issues...")
    issues = get_unassigned_issues(PARENT_KEY)
    
    if not issues:
        print("✅ 沒有找到未指派的 Issues")
        return
    
    print(f"✅ 找到 {len(issues)} 個未指派的 Issues\n")
    
    # 顯示未指派的 Issues
    print("="*70)
    print("未指派的 Issues 清單")
    print("="*70)
    print()
    
    for i, issue in enumerate(issues, 1):
        key = issue.get("key")
        summary = issue.get("fields", {}).get("summary", "")
        status = issue.get("fields", {}).get("status", {}).get("name", "")
        issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "")
        print(f"{i:3d}. {key} ({issue_type}) - {summary[:60]}... ({status})")
    
    print()
    
    if dry_run:
        print("="*70)
        print("🔍 DRY RUN 模式 - 不會實際執行指派")
        print("="*70)
        return
    
    # 執行指派
    print("="*70)
    print("📝 開始指派...")
    print("="*70)
    print()
    
    assigned_count = 0
    failed_count = 0
    
    for issue in issues:
        key = issue.get("key")
        summary = issue.get("fields", {}).get("summary", "")[:50]
        
        if assign_issue(key, account_id):
            print(f"  ✅ 已指派：{key} - {summary}...")
            assigned_count += 1
        else:
            print(f"  ❌ 指派失敗：{key}")
            failed_count += 1
    
    print()
    print("="*70)
    print("✅ 指派完成！")
    print("="*70)
    print(f"   成功指派：{assigned_count} 個")
    print(f"   失敗：{failed_count} 個")
    print("="*70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將未指派的 Tickets 指派給指定用戶")
    parser.add_argument("--assignee-email", default=DEFAULT_ASSIGNEE_EMAIL, help="指派給的 email（預設：reed.hsin@football.com）")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際執行）")
    parser.add_argument("--force", action="store_true", help="強制執行，跳過確認")
    args = parser.parse_args()
    
    assign_unassigned_tickets(
        assignee_email=args.assignee_email,
        dry_run=args.dry_run,
        force=args.force
    )

