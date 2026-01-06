#!/usr/bin/env python3
"""
刪除多餘的原始 Issues

這些原始 Issues 已經有對應的 Sub Tasks，可以安全刪除。
"""

import sqlite3
import requests
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"


def delete_jira_issue(jira_key: str, dry_run: bool = False) -> bool:
    """刪除 Jira Issue"""
    if dry_run:
        print(f"   [DRY RUN] 將刪除：{jira_key}")
        return True
    
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    # Jira 刪除 Issue 需要設定 deleteSubtasks 參數
    params = {
        "deleteSubtasks": "false"  # 不刪除子任務
    }
    
    try:
        response = requests.delete(url, headers=headers, auth=auth, params=params, timeout=30)
        response.raise_for_status()
        print(f"   ✅ 已刪除：{jira_key}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 刪除失敗：{jira_key}")
        print(f"      錯誤：{e}")
        if hasattr(e, 'response') and e.response:
            print(f"      回應：{e.response.text[:500]}")
        return False


def delete_redundant_issues(dry_run: bool = False, force: bool = False):
    """刪除多餘的原始 Issues"""
    print("📋 開始刪除多餘的原始 Issues...\n")
    
    if not dry_run and not force:
        try:
            confirm = input("⚠️  確定要刪除原始 Issues 嗎？此操作不可逆！(yes/no): ")
            if confirm.lower() != "yes":
                print("❌ 操作已取消")
                return
        except EOFError:
            print("❌ 無法讀取輸入，請使用 --force 參數跳過確認")
            return
    
    # 連線資料庫
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 取得所有原始 Issues（有對應 Sub Task 的）
    cursor.execute("""
        SELECT DISTINCT j1.jira_key, t.ticket_id, t.title
        FROM tickets t
        JOIN jira_issues j1 ON t.ticket_id = j1.ticket_id
        JOIN issue_links il ON j1.jira_key = il.source_jira_key
        JOIN jira_issues j2 ON il.target_jira_key = j2.jira_key
        WHERE j1.ticket_id NOT LIKE '%-SUBTASK' 
          AND j1.ticket_id NOT LIKE 'MAIN-%'
          AND j2.ticket_id LIKE '%-SUBTASK'
          AND il.link_type = 'Relates'
        ORDER BY t.ticket_id
    """)
    
    issues = cursor.fetchall()
    
    if not issues:
        print("❌ 沒有找到可以刪除的原始 Issues")
        conn.close()
        return
    
    print(f"找到 {len(issues)} 個可以刪除的原始 Issues：\n")
    
    for jira_key, ticket_id, title in issues:
        print(f"{jira_key}: {ticket_id} - {title}")
    
    print()
    
    deleted_count = 0
    failed_count = 0
    
    # 刪除每個 Issue
    for jira_key, ticket_id, title in issues:
        if delete_jira_issue(jira_key, dry_run):
            deleted_count += 1
            
            if not dry_run:
                # 從資料庫中移除記錄
                cursor.execute("""
                    DELETE FROM jira_issues WHERE jira_key = ?
                """, (jira_key,))
                
                cursor.execute("""
                    DELETE FROM issue_links 
                    WHERE source_jira_key = ? OR target_jira_key = ?
                """, (jira_key, jira_key))
        else:
            failed_count += 1
    
    if not dry_run:
        conn.commit()
    
    conn.close()
    
    print(f"\n✅ 完成！")
    print(f"   成功刪除：{deleted_count} 個")
    print(f"   失敗：{failed_count} 個")
    
    if not dry_run:
        print(f"\n📝 注意：已從資料庫中移除這些 Issues 的記錄")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="刪除多餘的原始 Issues")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際刪除）")
    parser.add_argument("--force", action="store_true", help="強制執行，跳過確認")
    args = parser.parse_args()
    
    delete_redundant_issues(dry_run=args.dry_run, force=args.force)

