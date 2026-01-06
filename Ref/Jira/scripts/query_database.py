#!/usr/bin/env python3
"""
查詢本地資料庫中的 Ticket 資訊

使用方式：
python scripts/query_database.py [--ticket-id TICKET_ID] [--jira-key JIRA_KEY] [--status STATUS] [--feature FEATURE]
"""

import sqlite3
import sys
from pathlib import Path
from typing import Optional

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"


def query_tickets(ticket_id: Optional[str] = None,
                  jira_key: Optional[str] = None,
                  status: Optional[str] = None,
                  feature: Optional[str] = None,
                  type_filter: Optional[str] = None):
    """查詢 Ticket 資訊"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 建立查詢
    query = """
        SELECT 
            t.ticket_id,
            t.title,
            t.type,
            t.priority,
            t.feature,
            t.story_point,
            t.estimate_standard,
            t.estimate_strict,
            j.jira_key,
            j.status,
            j.assignee_display_name,
            j.priority as jira_priority,
            j.original_estimate,
            j.time_spent,
            j.time_remaining,
            j.url
        FROM tickets t
        LEFT JOIN jira_issues j ON t.ticket_id = j.ticket_id
        WHERE 1=1
    """
    
    params = []
    
    if ticket_id:
        query += " AND t.ticket_id = ?"
        params.append(ticket_id)
    
    if jira_key:
        query += " AND j.jira_key = ?"
        params.append(jira_key)
    
    if status:
        query += " AND j.status = ?"
        params.append(status)
    
    if feature:
        query += " AND t.feature = ?"
        params.append(feature)
    
    if type_filter:
        query += " AND t.type = ?"
        params.append(type_filter)
    
    query += " ORDER BY t.ticket_id"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    if not rows:
        print("❌ 沒有找到符合條件的 Ticket")
        return
    
    print(f"📋 找到 {len(rows)} 個 Ticket：\n")
    
    for row in rows:
        print(f"Ticket ID: {row['ticket_id']}")
        print(f"標題: {row['title']}")
        print(f"類型: {row['type']}")
        print(f"優先級: {row['priority']}")
        print(f"Feature: {row['feature']}")
        print(f"Story Point: {row['story_point']}")
        print(f"估時（標準）: {row['estimate_standard']} 天")
        print(f"估時（最嚴厲）: {row['estimate_strict']} 天")
        
        if row['jira_key']:
            print(f"Jira Key: {row['jira_key']}")
            print(f"Jira Status: {row['status']}")
            print(f"Assignee: {row['assignee_display_name']}")
            print(f"Original Estimate: {row['original_estimate']}")
            print(f"Time Spent: {row['time_spent']}")
            print(f"Time Remaining: {row['time_remaining']}")
            print(f"URL: {row['url']}")
        else:
            print("Jira Key: 未同步")
        
        print("-" * 60)
    
    conn.close()


def list_all_tickets():
    """列出所有 Ticket 的摘要"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            t.ticket_id,
            t.title,
            t.type,
            t.priority,
            j.jira_key,
            j.status
        FROM tickets t
        LEFT JOIN jira_issues j ON t.ticket_id = j.ticket_id
        ORDER BY t.ticket_id
    """)
    
    rows = cursor.fetchall()
    
    if not rows:
        print("❌ 資料庫中沒有 Ticket")
        return
    
    print(f"📋 所有 Ticket（共 {len(rows)} 個）：\n")
    print(f"{'Ticket ID':<12} {'標題':<40} {'類型':<15} {'優先級':<8} {'Jira Key':<15} {'Status':<15}")
    print("-" * 120)
    
    for row in rows:
        jira_key = row['jira_key'] or "未同步"
        status = row['status'] or "-"
        print(f"{row['ticket_id']:<12} {row['title']:<40} {row['type']:<15} {row['priority']:<8} {jira_key:<15} {status:<15}")
    
    conn.close()


def show_statistics():
    """顯示統計資訊"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 總 Ticket 數
    cursor.execute("SELECT COUNT(*) FROM tickets")
    total_tickets = cursor.fetchone()[0]
    
    # 已同步到 Jira 的 Ticket 數
    cursor.execute("SELECT COUNT(*) FROM jira_issues")
    synced_tickets = cursor.fetchone()[0]
    
    # 按類型統計
    cursor.execute("""
        SELECT type, COUNT(*) 
        FROM tickets 
        GROUP BY type 
        ORDER BY COUNT(*) DESC
    """)
    type_stats = cursor.fetchall()
    
    # 按 Feature 統計
    cursor.execute("""
        SELECT feature, COUNT(*) 
        FROM tickets 
        WHERE feature IS NOT NULL
        GROUP BY feature 
        ORDER BY COUNT(*) DESC
    """)
    feature_stats = cursor.fetchall()
    
    # 按狀態統計
    cursor.execute("""
        SELECT status, COUNT(*) 
        FROM jira_issues 
        WHERE status IS NOT NULL
        GROUP BY status 
        ORDER BY COUNT(*) DESC
    """)
    status_stats = cursor.fetchall()
    
    print("📊 統計資訊：\n")
    print(f"總 Ticket 數：{total_tickets}")
    print(f"已同步到 Jira：{synced_tickets}")
    print(f"未同步：{total_tickets - synced_tickets}\n")
    
    print("按類型統計：")
    for type_name, count in type_stats:
        print(f"  {type_name}: {count}")
    
    print("\n按 Feature 統計：")
    for feature, count in feature_stats:
        print(f"  {feature}: {count}")
    
    if status_stats:
        print("\n按 Jira 狀態統計：")
        for status, count in status_stats:
            print(f"  {status}: {count}")
    
    conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="查詢本地資料庫中的 Ticket 資訊")
    parser.add_argument("--ticket-id", help="Ticket ID")
    parser.add_argument("--jira-key", help="Jira Key")
    parser.add_argument("--status", help="Jira Status")
    parser.add_argument("--feature", help="Feature 名稱")
    parser.add_argument("--type", help="Ticket 類型")
    parser.add_argument("--list", action="store_true", help="列出所有 Ticket")
    parser.add_argument("--stats", action="store_true", help="顯示統計資訊")
    
    args = parser.parse_args()
    
    if args.list:
        list_all_tickets()
    elif args.stats:
        show_statistics()
    else:
        query_tickets(
            ticket_id=args.ticket_id,
            jira_key=args.jira_key,
            status=args.status,
            feature=args.feature,
            type_filter=args.type
        )

