#!/usr/bin/env python3
"""
關閉多餘的原始 Issues（替代刪除）

由於 Jira API 刪除需要特殊權限，我們可以將這些 Issues 關閉（標記為「已取消」或「已完成」）。
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


def get_available_transitions(jira_key: str) -> List[Dict]:
    """取得 Issue 可用的狀態轉換"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}/transitions"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("transitions", [])
    except requests.exceptions.RequestException:
        return []


def close_issue(jira_key: str, transition_name: str = "Done", dry_run: bool = False) -> bool:
    """關閉 Issue（使用狀態轉換）"""
    if dry_run:
        print(f"   [DRY RUN] 將關閉：{jira_key} (轉換為: {transition_name})")
        return True
    
    # 取得可用的 transitions
    transitions = get_available_transitions(jira_key)
    
    # 尋找匹配的 transition
    transition_id = None
    for transition in transitions:
        if transition.get("name") == transition_name or transition.get("to", {}).get("name") == transition_name:
            transition_id = transition.get("id")
            break
    
    # 如果找不到，嘗試使用 "Cancel" 或 "Close"
    if not transition_id:
        for name in ["Cancel", "Close", "Done", "完成", "取消"]:
            for transition in transitions:
                if transition.get("name") == name or transition.get("to", {}).get("name") == name:
                    transition_id = transition.get("id")
                    transition_name = transition.get("to", {}).get("name", name)
                    break
            if transition_id:
                break
    
    if not transition_id:
        print(f"   ⚠️  無法找到合適的狀態轉換：{jira_key}")
        return False
    
    # 執行狀態轉換
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}/transitions"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    payload = {
        "transition": {"id": transition_id}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        print(f"   ✅ 已關閉：{jira_key} (狀態: {transition_name})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 關閉失敗：{jira_key}")
        print(f"      錯誤：{e}")
        if hasattr(e, 'response') and e.response:
            print(f"      回應：{e.response.text[:500]}")
        return False


def close_redundant_issues(dry_run: bool = False, force: bool = False):
    """關閉多餘的原始 Issues"""
    print("📋 開始關閉多餘的原始 Issues...\n")
    
    if not dry_run and not force:
        try:
            confirm = input("⚠️  確定要關閉原始 Issues 嗎？(yes/no): ")
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
        print("❌ 沒有找到可以關閉的原始 Issues")
        conn.close()
        return
    
    print(f"找到 {len(issues)} 個可以關閉的原始 Issues：\n")
    
    for jira_key, ticket_id, title in issues:
        print(f"{jira_key}: {ticket_id} - {title}")
    
    print()
    
    closed_count = 0
    failed_count = 0
    
    # 關閉每個 Issue
    for jira_key, ticket_id, title in issues:
        if close_issue(jira_key, dry_run=dry_run):
            closed_count += 1
        else:
            failed_count += 1
    
    conn.close()
    
    print(f"\n✅ 完成！")
    print(f"   成功關閉：{closed_count} 個")
    print(f"   失敗：{failed_count} 個")
    
    if not dry_run:
        print(f"\n💡 建議：執行 sync_from_jira.py 同步最新狀態到資料庫")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="關閉多餘的原始 Issues")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際關閉）")
    parser.add_argument("--force", action="store_true", help="強制執行，跳過確認")
    args = parser.parse_args()
    
    close_redundant_issues(dry_run=args.dry_run, force=args.force)

