#!/usr/bin/env python3
"""
從 Jira 同步 Issue 資訊到本地資料庫

使用方式：
python scripts/sync_from_jira.py [--parent-key PARENT_KEY]
"""

import sqlite3
import requests
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")
PARENT_ISSUE_KEY = os.getenv("PARENT_ISSUE_KEY", "")

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"


def get_jira_issues_by_parent(parent_key: str) -> List[Dict]:
    """根據父系 Issue 取得所有子 Issue"""
    # 使用新的 JQL API 取得 Issue IDs
    url = f"{JIRA_URL}/rest/api/3/search/jql"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    # JQL 查詢：取得所有子 Issue
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
        
        print(f"   ✅ 找到 {len(all_issue_ids)} 個 Issue，正在取得詳細資訊...")
        
        # 為每個 Issue ID 取得完整資訊
        detailed_issues = []
        for issue_id in all_issue_ids:
            detailed_issue = get_issue_details_by_id(issue_id)
            if detailed_issue:
                detailed_issues.append(detailed_issue)
        
        return detailed_issues
    except requests.exceptions.RequestException as e:
        print(f"❌ 查詢 Jira Issues 失敗：{e}")
        if hasattr(e, 'response') and e.response:
            print(f"   回應：{e.response.text[:500]}")
        return []


def get_issue_details_by_id(issue_id: str) -> Optional[Dict]:
    """根據 Issue ID 取得 Issue 的詳細資訊"""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_id}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  取得 Issue 詳細資訊失敗 (ID: {issue_id})：{e}")
        return None


def get_issue_details(jira_key: str) -> Optional[Dict]:
    """取得 Issue 的詳細資訊"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  取得 Issue 詳細資訊失敗 ({jira_key})：{e}")
        return None


def get_issue_links(jira_key: str) -> List[Dict]:
    """取得 Issue 的連結關係"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    params = {
        "fields": "issuelinks"
    }
    
    try:
        response = requests.get(url, headers=headers, auth=auth, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("fields", {}).get("issuelinks", [])
    except requests.exceptions.RequestException as e:
        print(f"⚠️  取得 Issue 連結失敗 ({jira_key})：{e}")
        return []


def parse_ticket_id_from_summary(summary: str) -> Optional[str]:
    """從 Summary 中解析 Ticket ID（例如：從 "實作 Comment Entity" 無法直接解析，需要從本地 tickets 表匹配）"""
    # 這個函數需要與本地 tickets 表匹配
    # 暫時返回 None，後續可以通過 title 匹配
    return None


def sync_issue_to_database(issue: Dict, conn: sqlite3.Connection) -> Optional[str]:
    """將 Jira Issue 同步到資料庫"""
    cursor = conn.cursor()
    
    jira_key = issue["key"]
    fields = issue.get("fields", {})
    
    # 嘗試從 summary 匹配本地 ticket
    summary = fields.get("summary", "")
    cursor.execute("SELECT ticket_id FROM tickets WHERE title = ?", (summary,))
    ticket_row = cursor.fetchone()
    
    if not ticket_row:
        # 如果找不到匹配的 ticket，記錄但不同步
        print(f"⚠️  找不到對應的本地 Ticket：{summary}")
        return None
    
    ticket_id = ticket_row[0]
    
    # 解析欄位
    status = fields.get("status", {}).get("name", "")
    assignee = fields.get("assignee")
    reporter = fields.get("reporter")
    priority = fields.get("priority", {}).get("name", "")
    issue_type = fields.get("issuetype", {}).get("name", "")
    labels = ",".join(fields.get("labels", []))
    parent = fields.get("parent", {}).get("key", "")
    timetracking = fields.get("timetracking", {})
    
    # 解析時間
    created_at = fields.get("created")
    updated_at = fields.get("updated")
    resolved_at = fields.get("resolutiondate")
    
    # 插入或更新 jira_issues 表
    cursor.execute("""
        INSERT OR REPLACE INTO jira_issues (
            ticket_id, jira_key, jira_id, summary, status,
            assignee_account_id, assignee_display_name,
            reporter_account_id, reporter_display_name,
            priority, issue_type, labels, parent_key,
            original_estimate, time_spent, time_remaining,
            created_at, updated_at, resolved_at, url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        jira_key,
        issue.get("id"),
        summary,
        status,
        assignee.get("accountId") if assignee else None,
        assignee.get("displayName") if assignee else None,
        reporter.get("accountId") if reporter else None,
        reporter.get("displayName") if reporter else None,
        priority,
        issue_type,
        labels,
        parent,
        timetracking.get("originalEstimate"),
        timetracking.get("timeSpent"),
        timetracking.get("remainingEstimate"),
        created_at,
        updated_at,
        resolved_at,
        f"{JIRA_URL}/browse/{jira_key}"
    ))
    
    return ticket_id


def sync_issue_links(jira_key: str, conn: sqlite3.Connection):
    """同步 Issue 連結關係"""
    cursor = conn.cursor()
    links = get_issue_links(jira_key)
    
    for link in links:
        link_type = link.get("type", {})
        inward_issue = link.get("inwardIssue")
        outward_issue = link.get("outwardIssue")
        
        if inward_issue and outward_issue:
            # 判斷連結方向
            if inward_issue.get("key") == jira_key:
                target_key = outward_issue.get("key")
                link_type_name = link_type.get("inward", "")
            else:
                target_key = inward_issue.get("key")
                link_type_name = link_type.get("outward", "")
            
            # 只記錄 "blocks" 類型的連結
            if "blocks" in link_type_name.lower() or "blocked" in link_type_name.lower():
                cursor.execute("""
                    INSERT OR IGNORE INTO issue_links (
                        source_jira_key, target_jira_key, link_type
                    ) VALUES (?, ?, ?)
                """, (jira_key, target_key, link_type_name))


def sync_from_jira(parent_key: Optional[str] = None):
    """從 Jira 同步所有 Issue 到本地資料庫"""
    if not parent_key:
        parent_key = PARENT_ISSUE_KEY
    
    if not parent_key:
        print("❌ 錯誤：請提供 PARENT_ISSUE_KEY 或使用 --parent-key 參數")
        sys.exit(1)
    
    print(f"📋 開始從 Jira 同步 Issue（Parent: {parent_key}）...")
    
    # 取得所有子 Issue
    issues = get_jira_issues_by_parent(parent_key)
    print(f"   找到 {len(issues)} 個 Issue")
    
    if not issues:
        print("⚠️  沒有找到任何 Issue")
        return
    
    # 連線資料庫
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    synced_count = 0
    links_count = 0
    
    # 同步每個 Issue
    for issue in issues:
        jira_key = issue["key"]
        ticket_id = sync_issue_to_database(issue, conn)
        
        if ticket_id:
            synced_count += 1
            print(f"   ✅ 同步：{jira_key} -> {ticket_id}")
            
            # 同步連結關係
            sync_issue_links(jira_key, conn)
            links_count += 1
    
    # 記錄同步歷史
    cursor.execute("""
        INSERT INTO sync_history (
            sync_type, tickets_synced, issues_updated, links_created, status
        ) VALUES (?, ?, ?, ?, ?)
    """, ("jira_sync", synced_count, synced_count, links_count, "success"))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 同步完成！")
    print(f"   同步 Issue 數：{synced_count}")
    print(f"   處理連結數：{links_count}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="從 Jira 同步 Issue 資訊到本地資料庫")
    parser.add_argument("--parent-key", help="父系 Issue Key")
    args = parser.parse_args()
    
    sync_from_jira(args.parent_key)

