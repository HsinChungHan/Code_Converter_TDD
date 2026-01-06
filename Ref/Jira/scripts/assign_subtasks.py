#!/usr/bin/env python3
"""
將所有未指派的 Sub Tasks 指派給指定用戶

使用方式：
python scripts/assign_subtasks.py [--assignee-email EMAIL] [--dry-run] [--force]
"""

import requests
import os
import argparse
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

DEFAULT_ASSIGNEE_EMAIL = "reed.hsin@football.com"

# Sub Tasks 的 Keys（FOOTBALL-9059 到 FOOTBALL-9084）
SUBTASK_KEYS = [f"FOOTBALL-{i}" for i in range(9059, 9085)]


def get_account_id_by_email(email: str) -> str:
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


def get_issue_info(jira_key: str) -> dict:
    """取得 Issue 的資訊"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    params = {"fields": "key,summary,status,assignee,issuetype,parent"}
    
    try:
        response = requests.get(url, headers=headers, auth=auth, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  查詢 Issue 失敗 ({jira_key})：{e}")
        return None


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


def main():
    parser = argparse.ArgumentParser(description="將所有未指派的 Sub Tasks 指派給指定用戶")
    parser.add_argument("--assignee-email", default=DEFAULT_ASSIGNEE_EMAIL, help="指派給的 email（預設：reed.hsin@football.com）")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際執行）")
    parser.add_argument("--force", action="store_true", help="強制執行，跳過確認")
    args = parser.parse_args()
    
    print("📋 開始檢查並指派未指派的 Sub Tasks...\n")
    
    # 取得 account ID
    print(f"正在查詢用戶 {args.assignee_email} 的 account ID...")
    account_id = get_account_id_by_email(args.assignee_email)
    
    if not account_id:
        print(f"❌ 找不到用戶 {args.assignee_email}")
        return
    
    print(f"✅ 找到用戶 account ID: {account_id}\n")
    
    # 檢查所有 Sub Tasks
    print(f"正在檢查 {len(SUBTASK_KEYS)} 個 Sub Tasks...\n")
    
    unassigned = []
    assigned = []
    completed = []
    
    for key in SUBTASK_KEYS:
        issue_data = get_issue_info(key)
        if not issue_data:
            continue
        
        summary = issue_data.get("fields", {}).get("summary", "")
        status = issue_data.get("fields", {}).get("status", {}).get("name", "")
        assignee = issue_data.get("fields", {}).get("assignee")
        parent = issue_data.get("fields", {}).get("parent", {})
        parent_key = parent.get("key", "") if parent else ""
        
        if status == "完成":
            completed.append((key, summary, parent_key))
        elif not assignee:
            unassigned.append((key, summary, status, parent_key))
        else:
            assignee_name = assignee.get("displayName", "")
            assigned.append((key, summary, status, assignee_name, parent_key))
    
    # 顯示統計
    print("="*70)
    print("📊 Sub Tasks 統計")
    print("="*70)
    print(f"總數：{len(SUBTASK_KEYS)} 個")
    print(f"未指派：{len(unassigned)} 個")
    print(f"已指派：{len(assigned)} 個")
    print(f"已完成：{len(completed)} 個")
    print()
    
    if unassigned:
        print("="*70)
        print("⚠️  未指派的 Sub Tasks")
        print("="*70)
        for i, (key, summary, status, parent_key) in enumerate(unassigned, 1):
            print(f"{i:3d}. {key} ({parent_key}) - {summary[:50]}... ({status})")
        print()
    
    if assigned:
        print("="*70)
        print("✅ 已指派的 Sub Tasks")
        print("="*70)
        for i, (key, summary, status, assignee_name, parent_key) in enumerate(assigned[:10], 1):
            print(f"{i:3d}. {key} ({parent_key}) - {summary[:40]}... ({status}) - {assignee_name}")
        if len(assigned) > 10:
            print(f"... 還有 {len(assigned) - 10} 個已指派的 Sub Tasks")
        print()
    
    if not unassigned:
        print("✅ 所有未完成的 Sub Tasks 都已指派")
        return
    
    if args.dry_run:
        print("="*70)
        print("🔍 DRY RUN 模式 - 不會實際執行指派")
        print("="*70)
        return
    
    if not args.force:
        try:
            confirm = input(f"⚠️  確定要將 {len(unassigned)} 個未指派的 Sub Tasks 指派給 {args.assignee_email} 嗎？(yes/no): ")
            if confirm.lower() != "yes":
                print("❌ 操作已取消")
                return
        except EOFError:
            print("❌ 無法讀取輸入，請使用 --force 參數跳過確認")
            return
    
    # 執行指派
    print("="*70)
    print("📝 開始指派...")
    print("="*70)
    print()
    
    assigned_count = 0
    failed_count = 0
    
    for key, summary, status, parent_key in unassigned:
        if assign_issue(key, account_id):
            print(f"  ✅ 已指派：{key} ({parent_key}) - {summary[:50]}...")
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
    main()

