#!/usr/bin/env python3
"""
檢查 Story (FOOTBALL-8686) 下的所有 Tickets 狀況

生成詳細的報告，包括：
- Main Tasks 列表
- Sub Tasks 列表
- 原始 Issues 列表
- 統計資訊
- 建議
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

STORY_KEY = "FOOTBALL-8686"


def get_jira_issue(jira_key: str) -> Dict:
    """取得 Jira Issue 資訊"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {}


def check_story_status():
    """檢查 Story 下的所有 Tickets 狀況"""
    print("="*70)
    print(f"📋 Story {STORY_KEY} 下的 Tickets 狀況報告")
    print("="*70)
    print()
    
    # 連線資料庫
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 取得 Story 資訊
    story = get_jira_issue(STORY_KEY)
    if story:
        fields = story.get("fields", {})
        print(f"Story 資訊：")
        print(f"  標題: {fields.get('summary', '')}")
        print(f"  類型: {fields.get('issuetype', {}).get('name', '')}")
        print(f"  狀態: {fields.get('status', {}).get('name', '')}")
        print(f"  優先級: {fields.get('priority', {}).get('name', '')}")
        print(f"  受託人: {fields.get('assignee', {}).get('displayName', '未指派')}")
        print()
    
    # 2. Main Tasks（真正的 Main Tasks，ticket_id 以 MAIN- 開頭）
    cursor.execute("""
        SELECT ticket_id, jira_key, summary, status, priority
        FROM jira_issues
        WHERE parent_key = ? AND ticket_id LIKE 'MAIN-%'
        ORDER BY jira_key
    """, (STORY_KEY,))
    
    main_tasks = cursor.fetchall()
    print(f"✅ Main Tasks（{len(main_tasks)} 個）：")
    print()
    for ticket_id, jira_key, summary, status, priority in main_tasks:
        # 取得 Sub Tasks 數量
        cursor.execute("""
            SELECT COUNT(*) FROM jira_issues WHERE parent_key = ?
        """, (jira_key,))
        subtask_count = cursor.fetchone()[0]
        
        print(f"  {jira_key}: {summary}")
        print(f"    狀態: {status} | 優先級: {priority} | Sub Tasks: {subtask_count} 個")
        print(f"    連結: {JIRA_URL}/browse/{jira_key}")
        print()
    
    # 3. Sub Tasks
    cursor.execute("""
        SELECT j.jira_key, j.summary, j.status, j.parent_key, m.summary as main_task_summary
        FROM jira_issues j
        JOIN jira_issues m ON j.parent_key = m.jira_key
        WHERE m.parent_key = ? AND j.ticket_id LIKE '%-SUBTASK'
        ORDER BY j.parent_key, j.jira_key
    """, (STORY_KEY,))
    
    subtasks = cursor.fetchall()
    print(f"✅ Sub Tasks（{len(subtasks)} 個）：")
    print()
    current_parent = None
    for jira_key, summary, status, parent_key, main_task_summary in subtasks:
        if current_parent != parent_key:
            if current_parent is not None:
                print()
            print(f"  📁 {parent_key} ({main_task_summary}):")
            current_parent = parent_key
        print(f"    - {jira_key}: {summary} ({status})")
    print()
    
    # 4. 原始 Issues（可能多餘的）
    cursor.execute("""
        SELECT j.jira_key, j.summary, j.status, t.ticket_id
        FROM jira_issues j
        JOIN tickets t ON j.ticket_id = t.ticket_id
        WHERE j.parent_key = ?
          AND j.ticket_id NOT LIKE 'MAIN-%'
          AND j.ticket_id NOT LIKE '%-SUBTASK'
        ORDER BY j.jira_key
    """, (STORY_KEY,))
    
    original_issues = cursor.fetchall()
    print(f"⚠️  原始 Issues（{len(original_issues)} 個，可能多餘）：")
    print()
    if original_issues:
        for jira_key, summary, status, ticket_id in original_issues:
            # 檢查是否有對應的 Sub Task
            cursor.execute("""
                SELECT COUNT(*) 
                FROM issue_links il
                JOIN jira_issues ji ON il.target_jira_key = ji.jira_key
                WHERE il.source_jira_key = ? 
                  AND ji.ticket_id LIKE '%-SUBTASK'
                  AND il.link_type = 'Relates'
            """, (jira_key,))
            has_subtask = cursor.fetchone()[0] > 0
            
            marker = "✅" if has_subtask else "❌"
            print(f"  {marker} {jira_key}: {summary} ({status})")
            if has_subtask:
                print(f"      → 已有對應的 Sub Task")
    else:
        print("  （無）")
    print()
    
    # 5. 統計
    print("="*70)
    print("📊 統計資訊")
    print("="*70)
    print()
    
    # 按狀態統計
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM jira_issues
        WHERE parent_key = ? 
           OR parent_key IN (
               SELECT jira_key FROM jira_issues WHERE parent_key = ?
           )
        GROUP BY status
        ORDER BY count DESC
    """, (STORY_KEY, STORY_KEY))
    
    print("按狀態統計：")
    for status, count in cursor.fetchall():
        print(f"  {status or '未設定'}: {count} 個")
    print()
    
    # 按 Layer 統計
    print("按 Layer 統計：")
    layer_stats = {
        "Domain Model": 0,
        "API": 0,
        "Client": 0,
        "Repository": 0,
        "UseCase": 0,
        "Feature": 0,
        "View": 0
    }
    
    for layer_name in layer_stats.keys():
        cursor.execute("""
            SELECT COUNT(*) 
            FROM jira_issues 
            WHERE parent_key = ? 
              AND ticket_id LIKE ?
        """, (STORY_KEY, f"MAIN-{layer_name.replace(' ', '-')}%"))
        count = cursor.fetchone()[0]
        if count > 0:
            # 取得 Sub Tasks 數量
            cursor.execute("""
                SELECT COUNT(*) 
                FROM jira_issues ji
                JOIN jira_issues m ON ji.parent_key = m.jira_key
                WHERE m.parent_key = ? 
                  AND m.ticket_id LIKE ?
                  AND ji.ticket_id LIKE '%-SUBTASK'
            """, (STORY_KEY, f"MAIN-{layer_name.replace(' ', '-')}%"))
            subtask_count = cursor.fetchone()[0]
            print(f"  {layer_name}: 1 個 Main Task, {subtask_count} 個 Sub Tasks")
    
    print()
    
    # 6. 建議
    print("="*70)
    print("💡 建議")
    print("="*70)
    print()
    
    active_original = [i for i in original_issues if i[2] != "完成"] if original_issues else []
    closed_original = [i for i in original_issues if i[2] == "完成"] if original_issues else []
    
    if active_original:
        print(f"⚠️  發現 {len(active_original)} 個活躍的原始 Issues 可能是多餘的：")
        print("   - 這些 Issues 已經有對應的 Sub Tasks")
        print("   - Sub Tasks 包含完整的資訊並正確連結到 Main Tasks")
        print("   - 原始 Issues 可以考慮關閉以簡化結構")
        print()
        print("   建議操作：")
        print("   python3 scripts/close_redundant_issues.py --force")
    elif closed_original:
        print(f"✅ 結構已清理：{len(closed_original)} 個原始 Issues 已關閉")
        print("   - 這些 Issues 不會在活躍任務列表中顯示")
        print("   - 仍然保留在 Jira 中，可以查看歷史記錄")
    else:
        print("✅ 結構清晰，沒有發現多餘的 Issues")
    
    print()
    print("="*70)
    
    conn.close()


if __name__ == "__main__":
    check_story_status()

