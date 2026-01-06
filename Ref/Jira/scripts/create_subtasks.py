#!/usr/bin/env python3
"""
為 Main Tasks 建立真正的 Sub Tasks

策略：
1. 為每個 Main Task 建立新的 Sub Tasks
2. 將原 Ticket 的資訊複製到 Sub Task
3. 連結原 Ticket 到 Sub Task（使用 "duplicates" 或 "relates"）
4. 更新資料庫
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

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"

# Layer 分組定義（與 consolidate_tickets.py 相同）
LAYER_GROUPS = {
    "Domain Model": {
        "name": "Domain Model Layer",
        "ticket_ids": ["TDD-001", "TDD-002", "TDD-003", "TDD-004", "TDD-005", "TDD-006"]
    },
    "API": {
        "name": "API Layer",
        "ticket_ids": ["TDD-010", "TDD-011"]
    },
    "Client": {
        "name": "Client Layer",
        "ticket_ids": ["TDD-020", "TDD-021", "TDD-022"]
    },
    "Repository": {
        "name": "Repository Layer",
        "ticket_ids": ["TDD-030", "TDD-031"]
    },
    "UseCase": {
        "name": "UseCase Layer",
        "ticket_ids": ["TDD-040", "TDD-041", "TDD-042", "TDD-043", "TDD-044", "TDD-045", "TDD-046", "TDD-047", "TDD-048"]
    },
    "Feature": {
        "name": "Feature Layer",
        "ticket_ids": ["TDD-050", "TDD-051"]
    },
    "View": {
        "name": "View Layer",
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


def get_subtask_type_id() -> Optional[str]:
    """取得子任務的 Issue Type ID"""
    project_url = f"{JIRA_URL}/rest/api/3/project/{JIRA_PROJECT_KEY}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(project_url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        project_info = response.json()
        
        for issue_type in project_info.get("issueTypes", []):
            if issue_type.get("name") == "子任務":
                return issue_type.get("id")
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️  取得 Issue Types 失敗：{e}")
        return None


def create_jira_description(ticket: Dict) -> Dict:
    """建立 Jira Description（ADF 格式）"""
    content = []
    
    # 描述
    if ticket.get("description"):
        content.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": ticket["description"]}]
        })
    
    # 需求
    if ticket.get("requirements"):
        content.append({
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "需求"}]
        })
        # 將需求文字轉換為列表
        req_items = []
        for line in ticket["requirements"].split("\n"):
            line = line.strip()
            if line and (line.startswith("1.") or line.startswith("-") or line.startswith("*")):
                text = line.lstrip("1234567890.-* ").strip()
                if text:
                    req_items.append({
                        "type": "listItem",
                        "content": [{
                            "type": "paragraph",
                            "content": [{"type": "text", "text": text}]
                        }]
                    })
        if req_items:
            content.append({
                "type": "bulletList",
                "content": req_items
            })
    
    # 驗收條件
    if ticket.get("acceptance_criteria"):
        content.append({
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "驗收條件"}]
        })
        # 將驗收條件轉換為列表
        ac_items = []
        for line in ticket["acceptance_criteria"].split("\n"):
            line = line.strip()
            if line and (line.startswith("-") or line.startswith("*") or line.startswith("[ ]")):
                text = line.lstrip("-*[ ]").strip()
                if text:
                    ac_items.append({
                        "type": "listItem",
                        "content": [{
                            "type": "paragraph",
                            "content": [{"type": "text", "text": text}]
                        }]
                    })
        if ac_items:
            content.append({
                "type": "bulletList",
                "content": ac_items
            })
    
    return {
        "type": "doc",
        "version": 1,
        "content": content
    }


def create_subtask(ticket: Dict, main_task_key: str, subtask_type_id: str) -> Optional[str]:
    """為 Main Task 建立 Sub Task"""
    url = f"{JIRA_URL}/rest/api/3/issue"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    issue_data = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": ticket["title"],
            "description": create_jira_description(ticket),
            "issuetype": {"id": subtask_type_id},
            "priority": {"name": PRIORITY_MAP.get(ticket.get("priority", "P0"), "Medium")},
            "labels": [ticket.get("feature", "").replace(" ", "-") if ticket.get("feature") else ""],
            "parent": {"key": main_task_key}
        }
    }
    
    # 移除空的 labels
    issue_data["fields"]["labels"] = [l for l in issue_data["fields"]["labels"] if l]
    
    # 如果有估時，加入時間追蹤
    if ticket.get("estimate_standard"):
        issue_data["fields"]["timetracking"] = {
            "originalEstimate": f"{ticket['estimate_standard']:.1f}d"
        }
    
    try:
        response = requests.post(url, json=issue_data, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        result = response.json()
        subtask_key = result.get("key")
        print(f"   ✅ 建立 Sub Task：{subtask_key} - {ticket['title']}")
        return subtask_key
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 建立 Sub Task 失敗：{ticket['title']}")
        print(f"      錯誤：{e}")
        if hasattr(e, 'response') and e.response:
            print(f"      回應：{e.response.text[:500]}")
        return None


def link_original_to_subtask(original_key: str, subtask_key: str):
    """連結原 Issue 到 Sub Task（使用 "relates" 連結）"""
    url = f"{JIRA_URL}/rest/api/3/issueLink"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    link_data = {
        "type": {"name": "Relates"},
        "inwardIssue": {"key": subtask_key},
        "outwardIssue": {"key": original_key}
    }
    
    try:
        response = requests.post(url, json=link_data, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        print(f"      ✅ 連結原 Issue：{original_key} -> {subtask_key}")
        return True
    except requests.exceptions.RequestException as e:
        # 如果連結已存在，忽略錯誤
        if hasattr(e, 'response') and e.response:
            if e.response.status_code == 400:
                try:
                    error_json = e.response.json()
                    if "already exists" in str(error_json).lower() or "已存在" in str(error_json):
                        return True
                except:
                    pass
        print(f"      ⚠️  連結失敗：{original_key} -> {subtask_key}")
        return False


def update_database_with_subtask(ticket_id: str, original_jira_key: str, subtask_key: str, main_task_key: str, conn: sqlite3.Connection):
    """更新資料庫，記錄 Sub Task 資訊"""
    cursor = conn.cursor()
    
    # 取得 Sub Task 資訊
    issue = get_jira_issue_by_key(subtask_key)
    if issue:
        fields = issue.get("fields", {})
        # 使用特殊的 ticket_id 格式來標記這是 Sub Task
        subtask_ticket_id = f"{ticket_id}-SUBTASK"
        
        cursor.execute("""
            INSERT OR REPLACE INTO jira_issues (
                ticket_id, jira_key, jira_id, summary, status,
                priority, issue_type, labels, parent_key, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subtask_ticket_id,
            subtask_key,
            issue.get("id"),
            fields.get("summary"),
            fields.get("status", {}).get("name"),
            fields.get("priority", {}).get("name"),
            fields.get("issuetype", {}).get("name"),
            ",".join(fields.get("labels", [])),
            fields.get("parent", {}).get("key"),
            f"{JIRA_URL}/browse/{subtask_key}"
        ))
        
        # 記錄原 Issue 和 Sub Task 的連結
        cursor.execute("""
            INSERT OR IGNORE INTO issue_links (
                source_jira_key, target_jira_key, link_type
            ) VALUES (?, ?, ?)
        """, (original_jira_key, subtask_key, "Relates"))
    
    conn.commit()


def create_subtasks_for_layer(layer_name: str, layer_info: Dict, main_task_key: str, conn: sqlite3.Connection):
    """為 Layer 的 Main Task 建立所有 Sub Tasks"""
    cursor = conn.cursor()
    
    # 取得子任務的 Issue Type ID
    subtask_type_id = get_subtask_type_id()
    if not subtask_type_id:
        print(f"❌ 無法取得子任務 Issue Type ID")
        return
    
    print(f"處理 Layer：{layer_name}")
    print(f"  Main Task: {main_task_key}")
    
    # 取得該 Layer 的所有 tickets 資訊
    ticket_ids = layer_info["ticket_ids"]
    placeholders = ",".join(["?"] * len(ticket_ids))
    cursor.execute(f"""
        SELECT t.ticket_id, t.title, t.priority, t.story_point, t.estimate_standard,
               t.description, t.requirements, t.acceptance_criteria, j.jira_key
        FROM tickets t
        LEFT JOIN jira_issues j ON t.ticket_id = j.ticket_id
        WHERE t.ticket_id IN ({placeholders})
    """, ticket_ids)
    
    tickets = cursor.fetchall()
    
    if not tickets:
        print(f"  ⚠️  沒有找到任何 tickets")
        return
    
    print(f"  建立 {len(tickets)} 個 Sub Tasks...")
    
    for ticket_row in tickets:
        ticket = {
            "ticket_id": ticket_row[0],
            "title": ticket_row[1],
            "priority": ticket_row[2],
            "story_point": ticket_row[3],
            "estimate_standard": ticket_row[4],
            "description": ticket_row[5],
            "requirements": ticket_row[6],
            "acceptance_criteria": ticket_row[7]
        }
        original_jira_key = ticket_row[8]
        
        # 建立 Sub Task
        subtask_key = create_subtask(ticket, main_task_key, subtask_type_id)
        
        if subtask_key and original_jira_key:
            # 連結原 Issue 到 Sub Task
            link_original_to_subtask(original_jira_key, subtask_key)
            
            # 更新資料庫
            update_database_with_subtask(
                ticket["ticket_id"],
                original_jira_key,
                subtask_key,
                main_task_key,
                conn
            )


def create_all_subtasks():
    """為所有 Main Tasks 建立 Sub Tasks"""
    print("📋 開始為 Main Tasks 建立 Sub Tasks...\n")
    
    # 連線資料庫
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 取得所有 Main Tasks
    cursor.execute("""
        SELECT ticket_id, jira_key, summary
        FROM jira_issues
        WHERE ticket_id LIKE 'MAIN-%'
        ORDER BY ticket_id
    """)
    
    main_tasks = cursor.fetchall()
    
    if not main_tasks:
        print("❌ 沒有找到任何 Main Tasks")
        print("   請先執行 consolidate_tickets.py 建立 Main Tasks")
        conn.close()
        return
    
    # 建立 Main Task Key 到 Layer 名稱的映射
    main_task_map = {}
    for main_task_row in main_tasks:
        main_ticket_id = main_task_row[0]
        main_task_key = main_task_row[1]
        # 從 ticket_id 提取 layer 名稱（例如：MAIN-Domain-Model -> Domain Model）
        layer_name = main_ticket_id.replace("MAIN-", "").replace("-", " ")
        main_task_map[layer_name] = main_task_key
    
    # 為每個 Layer 建立 Sub Tasks
    for layer_name, layer_info in LAYER_GROUPS.items():
        main_task_key = main_task_map.get(layer_name)
        if not main_task_key:
            print(f"⚠️  找不到 {layer_name} 的 Main Task")
            continue
        
        create_subtasks_for_layer(layer_name, layer_info, main_task_key, conn)
        print()
    
    conn.close()
    print("✅ 完成！")


if __name__ == "__main__":
    create_all_subtasks()

