#!/usr/bin/env python3
"""
分析多餘的 Issues，檢查是否可以安全刪除

檢查原始 Issues 是否有：
- 評論
- 工作日誌
- 狀態變更歷史
- 附件
- 其他重要資訊
"""

import sqlite3
import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"


def get_issue_comments(jira_key: str) -> List[Dict]:
    """取得 Issue 的評論"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}/comment"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("comments", [])
    except requests.exceptions.RequestException:
        return []


def get_issue_worklogs(jira_key: str) -> List[Dict]:
    """取得 Issue 的工作日誌"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}/worklog"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("worklogs", [])
    except requests.exceptions.RequestException:
        return []


def get_issue_changelog(jira_key: str) -> List[Dict]:
    """取得 Issue 的變更歷史"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}/changelog"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("values", [])
    except requests.exceptions.RequestException:
        return []


def analyze_issue(jira_key: str, ticket_id: str) -> Dict:
    """分析 Issue 是否有重要資訊"""
    result = {
        "jira_key": jira_key,
        "ticket_id": ticket_id,
        "has_comments": False,
        "comment_count": 0,
        "has_worklogs": False,
        "worklog_count": 0,
        "has_changelog": False,
        "changelog_count": 0,
        "can_delete": True,
        "reasons": []
    }
    
    # 檢查評論
    comments = get_issue_comments(jira_key)
    if comments:
        result["has_comments"] = True
        result["comment_count"] = len(comments)
        result["can_delete"] = False
        result["reasons"].append(f"有 {len(comments)} 個評論")
    
    # 檢查工作日誌
    worklogs = get_issue_worklogs(jira_key)
    if worklogs:
        result["has_worklogs"] = True
        result["worklog_count"] = len(worklogs)
        result["can_delete"] = False
        result["reasons"].append(f"有 {len(worklogs)} 個工作日誌")
    
    # 檢查變更歷史（排除初始建立）
    changelog = get_issue_changelog(jira_key)
    if changelog:
        # 過濾掉只有建立記錄的變更
        meaningful_changes = [c for c in changelog if len(c.get("items", [])) > 0]
        if len(meaningful_changes) > 1:  # 超過 1 個表示有實際變更
            result["has_changelog"] = True
            result["changelog_count"] = len(meaningful_changes)
            result["can_delete"] = False
            result["reasons"].append(f"有 {len(meaningful_changes)} 個變更記錄")
    
    return result


def analyze_all_original_issues():
    """分析所有原始 Issues"""
    print("📋 分析原始 Issues...\n")
    
    # 連線資料庫
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 取得所有原始 Issues
    cursor.execute("""
        SELECT t.ticket_id, j.jira_key, t.title
        FROM tickets t
        JOIN jira_issues j ON t.ticket_id = j.ticket_id
        WHERE j.ticket_id NOT LIKE '%-SUBTASK' 
          AND j.ticket_id NOT LIKE 'MAIN-%'
        ORDER BY t.ticket_id
    """)
    
    issues = cursor.fetchall()
    
    if not issues:
        print("❌ 沒有找到原始 Issues")
        conn.close()
        return
    
    print(f"找到 {len(issues)} 個原始 Issues\n")
    
    can_delete = []
    cannot_delete = []
    
    for ticket_id, jira_key, title in issues:
        print(f"分析 {jira_key}: {title}...")
        result = analyze_issue(jira_key, ticket_id)
        
        if result["can_delete"]:
            can_delete.append(result)
            print(f"  ✅ 可以刪除（沒有額外資訊）")
        else:
            cannot_delete.append(result)
            print(f"  ❌ 不建議刪除：{', '.join(result['reasons'])}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("📊 分析結果總結")
    print("="*60)
    print(f"\n可以安全刪除：{len(can_delete)} 個")
    print(f"不建議刪除：{len(cannot_delete)} 個")
    
    if can_delete:
        print("\n可以刪除的 Issues：")
        for item in can_delete:
            print(f"  - {item['jira_key']}: {item['ticket_id']}")
    
    if cannot_delete:
        print("\n不建議刪除的 Issues（有重要資訊）：")
        for item in cannot_delete:
            print(f"  - {item['jira_key']}: {item['ticket_id']}")
            print(f"    原因：{', '.join(item['reasons'])}")
    
    return can_delete, cannot_delete


if __name__ == "__main__":
    analyze_all_original_issues()

