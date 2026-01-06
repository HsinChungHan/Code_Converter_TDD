#!/usr/bin/env python3
"""
收斂 Tickets 並建立 Main Tasks 和 Sub Tasks

策略：
1. 按照 Layer 分組 tickets
2. 為每個 Layer 創建一個 Main Task
3. 將現有的 tickets 轉換為 Sub Tasks
4. 更新 Jira
5. 更新資料庫
"""

import sqlite3
import requests
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple

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

# Layer 分組定義
LAYER_GROUPS = {
    "Domain Model": {
        "name": "Domain Model Layer",
        "description": "實作所有 Domain Model（Entity、Value Object）",
        "ticket_ids": ["TDD-001", "TDD-002", "TDD-003", "TDD-004", "TDD-005", "TDD-006"]
    },
    "API": {
        "name": "API Layer",
        "description": "定義所有 API 規格（PrematchComment API、Chat API）",
        "ticket_ids": ["TDD-010", "TDD-011"]
    },
    "Client": {
        "name": "Client Layer",
        "description": "實作所有 Client（HTTP Client、WebSocket Client）",
        "ticket_ids": ["TDD-020", "TDD-021", "TDD-022"]
    },
    "Repository": {
        "name": "Repository Layer",
        "description": "實作所有 Repository（PrematchComment Repository、LiveChat Repository）",
        "ticket_ids": ["TDD-030", "TDD-031"]
    },
    "UseCase": {
        "name": "UseCase Layer",
        "description": "實作所有 UseCase（Comment、Chat 相關業務邏輯）",
        "ticket_ids": ["TDD-040", "TDD-041", "TDD-042", "TDD-043", "TDD-044", "TDD-045", "TDD-046", "TDD-047", "TDD-048"]
    },
    "Feature": {
        "name": "Feature Layer",
        "description": "實作所有 Feature（TCA Reducer）",
        "ticket_ids": ["TDD-050", "TDD-051"]
    },
    "View": {
        "name": "View Layer",
        "description": "實作所有 View（UI 元件）",
        "ticket_ids": ["TDD-060", "TDD-061"]
    }
}

# 優先級對應
PRIORITY_MAP = {
    "P0": "Highest",
    "P1": "High",
    "P2": "Medium",
    "P3": "Low"
}


def get_jira_issue_by_key(jira_key: str) -> Optional[Dict]:
    """取得 Jira Issue 資訊"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  取得 Issue 失敗 ({jira_key})：{e}")
        return None


def create_main_task(layer_name: str, layer_info: Dict, conn: sqlite3.Connection) -> Optional[str]:
    """為 Layer 創建 Main Task"""
    cursor = conn.cursor()
    
    # 取得該 Layer 的所有 tickets 資訊
    ticket_ids = layer_info["ticket_ids"]
    placeholders = ",".join(["?"] * len(ticket_ids))
    cursor.execute(f"""
        SELECT t.ticket_id, t.title, t.priority, t.story_point, t.estimate_standard, j.jira_key
        FROM tickets t
        LEFT JOIN jira_issues j ON t.ticket_id = j.ticket_id
        WHERE t.ticket_id IN ({placeholders})
    """, ticket_ids)
    
    tickets = cursor.fetchall()
    
    if not tickets:
        print(f"⚠️  Layer {layer_name} 沒有找到任何 tickets")
        return None
    
    # 計算總 Story Point 和估時
    total_story_point = sum(t[3] or 0 for t in tickets)
    total_estimate = sum(t[4] or 0 for t in tickets)
    
    # 取得最高優先級
    priorities = [t[2] for t in tickets if t[2]]
    highest_priority = min(priorities, key=lambda p: int(p[1]) if len(p) > 1 else 3) if priorities else "P0"
    
    # 建立 Main Task
    summary = layer_info["name"]
    description_content = [
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": layer_info["description"]}]
        },
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "包含的 Sub Tasks"}]
        },
        {
            "type": "bulletList",
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"{t[0]}: {t[1]}"
                                }
                            ]
                        }
                    ]
                }
                for t in tickets
            ]
        },
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "統計資訊"}]
        },
        {
            "type": "bulletList",
            "content": [
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"總 Sub Tasks 數：{len(tickets)}"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"總 Story Point：{total_story_point}"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "listItem",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"總估時：{total_estimate:.1f} 天"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
    
    issue_data = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": description_content
            },
            "issuetype": {"name": "任務"},
            "priority": {"name": PRIORITY_MAP.get(highest_priority, "Medium")},
            "labels": [layer_name.replace(" ", "-")],
            "parent": {"key": PARENT_ISSUE_KEY}
        }
    }
    
    # 如果有估時，加入時間追蹤
    if total_estimate > 0:
        issue_data["fields"]["timetracking"] = {
            "originalEstimate": f"{total_estimate:.1f}d"
        }
    
    # 建立 Issue
    url = f"{JIRA_URL}/rest/api/3/issue"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.post(url, json=issue_data, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        result = response.json()
        main_task_key = result.get("key")
        print(f"✅ 建立 Main Task：{main_task_key} - {summary}")
        return main_task_key
    except requests.exceptions.RequestException as e:
        print(f"❌ 建立 Main Task 失敗：{summary}")
        print(f"   錯誤：{e}")
        if hasattr(e, 'response') and e.response:
            print(f"   回應：{e.response.text[:500]}")
        return None


def link_to_parent(jira_key: str, parent_key: str) -> bool:
    """將 Issue 連結到 Main Task（使用 Issue Links）"""
    # 由於 Jira 不允許直接將現有 Issue 轉換為 Sub Task，
    # 我們使用 Issue Links 來建立關係
    url = f"{JIRA_URL}/rest/api/3/issueLink"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    # 建立 "relates to" 連結（表示這個 Issue 與 Main Task 相關）
    link_data = {
        "type": {"name": "Relates"},
        "inwardIssue": {"key": parent_key},
        "outwardIssue": {"key": jira_key}
    }
    
    try:
        response = requests.post(url, json=link_data, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        print(f"   ✅ 連結到 Main Task：{jira_key} -> {parent_key}")
        return True
    except requests.exceptions.RequestException as e:
        # 如果連結已存在，忽略錯誤
        if hasattr(e, 'response') and e.response:
            if e.response.status_code == 400:
                try:
                    error_json = e.response.json()
                    if "already exists" in str(error_json).lower() or "已存在" in str(error_json):
                        print(f"   ℹ️  連結已存在：{jira_key} -> {parent_key}")
                        return True
                except:
                    pass
        print(f"   ⚠️  連結失敗：{jira_key} -> {parent_key} ({e})")
        return False


def update_database(main_task_key: str, layer_name: str, ticket_ids: List[str], conn: sqlite3.Connection):
    """更新資料庫，記錄 Main Task 和 Ticket 關係"""
    cursor = conn.cursor()
    
    # 在資料庫中記錄 Main Task（使用特殊的 ticket_id）
    main_ticket_id = f"MAIN-{layer_name.replace(' ', '-')}"
    
    # 取得 Main Task 資訊
    issue = get_jira_issue_by_key(main_task_key)
    if issue:
        fields = issue.get("fields", {})
        cursor.execute("""
            INSERT OR REPLACE INTO jira_issues (
                ticket_id, jira_key, jira_id, summary, status,
                priority, issue_type, labels, parent_key, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            main_ticket_id,
            main_task_key,
            issue.get("id"),
            fields.get("summary"),
            fields.get("status", {}).get("name"),
            fields.get("priority", {}).get("name"),
            fields.get("issuetype", {}).get("name"),
            ",".join(fields.get("labels", [])),
            fields.get("parent", {}).get("key"),
            f"{JIRA_URL}/browse/{main_task_key}"
        ))
    
    # 記錄 Main Task 和 Ticket 的連結關係到 issue_links 表
    for ticket_id in ticket_ids:
        # 取得 ticket 的 jira_key
        cursor.execute("""
            SELECT jira_key FROM jira_issues WHERE ticket_id = ?
        """, (ticket_id,))
        row = cursor.fetchone()
        
        if row and row[0]:
            ticket_jira_key = row[0]
            # 記錄連結關係（Main Task -> Ticket）
            cursor.execute("""
                INSERT OR IGNORE INTO issue_links (
                    source_jira_key, target_jira_key, link_type
                ) VALUES (?, ?, ?)
            """, (main_task_key, ticket_jira_key, "Relates"))
    
    conn.commit()


def consolidate_tickets(dry_run: bool = False):
    """收斂 Tickets"""
    print("📋 開始收斂 Tickets...\n")
    
    if not PARENT_ISSUE_KEY:
        print("❌ 錯誤：請設定 PARENT_ISSUE_KEY")
        sys.exit(1)
    
    # 連線資料庫
    conn = sqlite3.connect(DB_PATH)
    
    main_tasks = {}
    
    # 為每個 Layer 創建 Main Task
    for layer_name, layer_info in LAYER_GROUPS.items():
        print(f"處理 Layer：{layer_name}")
        
        if dry_run:
            print(f"   [DRY RUN] 將為 {layer_name} 創建 Main Task")
            print(f"   包含 {len(layer_info['ticket_ids'])} 個 Sub Tasks")
            main_tasks[layer_name] = f"DRY-RUN-{layer_name}"
        else:
            main_task_key = create_main_task(layer_name, layer_info, conn)
            if main_task_key:
                main_tasks[layer_name] = main_task_key
                
                # 將該 Layer 的所有 tickets 連結到 Main Task
                print(f"   連結 Tickets 到 Main Task...")
                for ticket_id in layer_info["ticket_ids"]:
                    # 取得 ticket 的 jira_key
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT jira_key FROM jira_issues WHERE ticket_id = ?
                    """, (ticket_id,))
                    row = cursor.fetchone()
                    
                    if row and row[0]:
                        jira_key = row[0]
                        link_to_parent(jira_key, main_task_key)
                
                # 更新資料庫
                update_database(main_task_key, layer_name, layer_info["ticket_ids"], conn)
        
        print()
    
    conn.close()
    
    print("✅ 收斂完成！")
    print(f"\n建立的 Main Tasks：")
    for layer_name, main_task_key in main_tasks.items():
        print(f"  {layer_name}: {main_task_key}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="收斂 Tickets 並建立 Main Tasks 和 Sub Tasks")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式")
    args = parser.parse_args()
    
    consolidate_tickets(dry_run=args.dry_run)

