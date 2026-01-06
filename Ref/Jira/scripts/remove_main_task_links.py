#!/usr/bin/env python3
"""
移除 Main Tasks 與原始 Issues 之間的連結

移除所有 Main Tasks 連結到原始 Issues 的連結關係。
"""

import sqlite3
import requests
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional, Dict

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"


def get_issue_links(jira_key: str) -> List[Dict]:
    """取得 Issue 的所有連結"""
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


def delete_issue_link(link_id: str) -> bool:
    """刪除 Issue 連結"""
    url = f"{JIRA_URL}/rest/api/3/issueLink/{link_id}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.delete(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"⚠️  刪除連結失敗 (ID: {link_id})：{e}")
        return False


def remove_main_task_links(dry_run: bool = False, force: bool = False):
    """移除 Main Tasks 與原始 Issues 之間的連結"""
    print("📋 開始移除 Main Tasks 的連結關係...\n")
    
    if not dry_run and not force:
        try:
            confirm = input("⚠️  確定要移除 Main Tasks 的連結關係嗎？(yes/no): ")
            if confirm.lower() != "yes":
                print("❌ 操作已取消")
                return
        except EOFError:
            print("❌ 無法讀取輸入，請使用 --force 參數跳過確認")
            return
    
    # 連線資料庫
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 取得所有 Main Tasks
    cursor.execute("""
        SELECT jira_key, summary, ticket_id
        FROM jira_issues
        WHERE ticket_id LIKE 'MAIN-%'
        ORDER BY jira_key
    """)
    
    main_tasks = cursor.fetchall()
    
    if not main_tasks:
        print("❌ 沒有找到 Main Tasks")
        conn.close()
        return
    
    print(f"找到 {len(main_tasks)} 個 Main Tasks\n")
    
    total_removed = 0
    total_failed = 0
    
    # 處理每個 Main Task
    for main_task_key, main_task_summary, main_ticket_id in main_tasks:
        print(f"處理 {main_task_key}: {main_task_summary}")
        
        # 取得 Main Task 的所有連結
        links = get_issue_links(main_task_key)
        
        if not links:
            print(f"  ℹ️  沒有連結")
            continue
        
        # 找出連結到原始 Issues 的連結（不是 Sub Tasks）
        links_to_remove = []
        for link in links:
            link_id = link.get("id")
            inward_issue = link.get("inwardIssue")
            outward_issue = link.get("outwardIssue")
            
            # 取得連結的另一端（不是 Main Task 的那一端）
            target_key = None
            if inward_issue:
                inward_key = inward_issue.get("key")
                if inward_key == main_task_key:
                    # Main Task 是 inward，目標是 outward
                    target_key = outward_issue.get("key") if outward_issue else None
                else:
                    # Main Task 不是 inward，目標可能是 inward
                    target_key = inward_key
            
            if not target_key and outward_issue:
                outward_key = outward_issue.get("key")
                if outward_key == main_task_key:
                    # Main Task 是 outward，目標是 inward
                    target_key = inward_issue.get("key") if inward_issue else None
                else:
                    # Main Task 不是 outward，目標可能是 outward
                    target_key = outward_key
            
            if not target_key:
                continue
            
            # 檢查目標 Issue 是否是原始 Issue（不是 Sub Task，不是 Main Task）
            cursor.execute("""
                SELECT ticket_id, status
                FROM jira_issues
                WHERE jira_key = ?
            """, (target_key,))
            target_row = cursor.fetchone()
            
            if target_row:
                target_ticket_id, target_status = target_row
                # 如果是原始 Issue（ticket_id 格式是 TDD-XXX，不是 MAIN-XXX 或 XXX-SUBTASK）
                is_original_issue = (
                    target_ticket_id and 
                    target_ticket_id.startswith("TDD-") and
                    not target_ticket_id.startswith("MAIN-") and 
                    not target_ticket_id.endswith("-SUBTASK")
                )
                
                if is_original_issue:
                    links_to_remove.append({
                        "link_id": link_id,
                        "target_key": target_key,
                        "link_type": link.get("type", {}).get("name", "")
                    })
                    print(f"   找到連結：{main_task_key} -> {target_key} (ticket_id: {target_ticket_id})")
        
        if not links_to_remove:
            print(f"  ℹ️  沒有需要移除的連結")
            continue
        
        print(f"  找到 {len(links_to_remove)} 個需要移除的連結")
        
        # 移除連結
        for link_info in links_to_remove:
            if dry_run:
                print(f"  [DRY RUN] 將移除連結：{main_task_key} -> {link_info['target_key']} ({link_info['link_type']})")
                total_removed += 1
            else:
                if delete_issue_link(link_info["link_id"]):
                    print(f"  ✅ 已移除連結：{main_task_key} -> {link_info['target_key']}")
                    total_removed += 1
                    
                    # 從資料庫中移除連結記錄
                    cursor.execute("""
                        DELETE FROM issue_links
                        WHERE (source_jira_key = ? AND target_jira_key = ?)
                           OR (source_jira_key = ? AND target_jira_key = ?)
                    """, (main_task_key, link_info['target_key'], link_info['target_key'], main_task_key))
                else:
                    total_failed += 1
        
        print()
    
    if not dry_run:
        conn.commit()
    
    conn.close()
    
    print("="*70)
    print(f"✅ 完成！")
    print(f"   成功移除：{total_removed} 個連結")
    print(f"   失敗：{total_failed} 個")
    print("="*70)


if __name__ == "__main__":
    import argparse
    from typing import Dict
    
    parser = argparse.ArgumentParser(description="移除 Main Tasks 與原始 Issues 之間的連結")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際移除）")
    parser.add_argument("--force", action="store_true", help="強制執行，跳過確認")
    args = parser.parse_args()
    
    remove_main_task_links(dry_run=args.dry_run, force=args.force)

