#!/usr/bin/env python3
"""
將英文版本的 Ticket 文件更新到資料庫

從英文版本的 Ticket 文件（*_en.md）讀取內容，更新資料庫中對應的記錄。

使用方式：
python scripts/update_db_with_english_tickets.py [--dry-run]
"""

import re
import argparse
import sqlite3
from pathlib import Path
from typing import Dict, Optional

# Ticket 文件目錄（在 output 目錄下）
TICKETS_DIR = Path(__file__).parent.parent.parent / "output" / "LiveChat&PrematchComment" / "12_Tickets"
# 資料庫路徑（在 jira_integration 目錄下）
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"


def parse_english_ticket_markdown(file_path: Path) -> Dict:
    """解析英文版本的 Ticket Markdown 文件"""
    content = file_path.read_text(encoding='utf-8')
    
    ticket = {
        "ticket_id": None,
        "description": "",
        "requirements": [],
        "acceptance_criteria": [],
        "related_documents": []
    }
    
    # 解析 Ticket ID
    ticket_id_match = re.search(r'# (TDD-\d+):', content)
    if ticket_id_match:
        ticket["ticket_id"] = ticket_id_match.group(1)
    
    # 解析 Description
    desc_match = re.search(r'## Description\s*\n\s*(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if desc_match:
        ticket["description"] = desc_match.group(1).strip()
    
    # 解析 Requirements
    req_match = re.search(r'## Requirements\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if req_match:
        req_text = req_match.group(1)
        # 提取編號列表項
        req_items = re.findall(r'^\d+\.\s*(.+)$', req_text, re.MULTILINE)
        ticket["requirements"] = [item.strip() for item in req_items if item.strip()]
    
    # 解析 Acceptance Criteria
    ac_match = re.search(r'## Acceptance Criteria\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if ac_match:
        ac_text = ac_match.group(1)
        # 提取任務列表項
        ac_items = re.findall(r'^- \[[ x]\]\s*(.+)$', ac_text, re.MULTILINE)
        ticket["acceptance_criteria"] = [item.strip() for item in ac_items if item.strip()]
    
    # 解析 Related Documents
    doc_match = re.search(r'## Related Documents\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if doc_match:
        doc_text = doc_match.group(1)
        # 提取列表項
        doc_items = re.findall(r'^-\s*(.+)$', doc_text, re.MULTILINE)
        ticket["related_documents"] = [item.strip() for item in doc_items if item.strip()]
    
    return ticket


def build_description_text(ticket: Dict) -> str:
    """將 Ticket 資料組合成描述文字"""
    lines = []
    
    # Description
    if ticket["description"]:
        lines.append(ticket["description"])
        lines.append("")
    
    # Requirements
    if ticket["requirements"]:
        lines.append("Requirements:")
        for req in ticket["requirements"]:
            lines.append(f"- {req}")
        lines.append("")
    
    # Acceptance Criteria
    if ticket["acceptance_criteria"]:
        lines.append("Acceptance Criteria:")
        for ac in ticket["acceptance_criteria"]:
            lines.append(f"- [ ] {ac}")
        lines.append("")
    
    # Related Documents
    if ticket["related_documents"]:
        lines.append("Related Documents:")
        for doc in ticket["related_documents"]:
            lines.append(f"- {doc}")
    
    return "\n".join(lines)


def update_database_with_english_ticket(ticket_id: str, description_en: str, jira_key: str = None) -> bool:
    """更新資料庫中的英文描述"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 優先更新 SUBTASK 格式（如果 jira_key 提供，直接使用）
        if jira_key:
            cursor.execute("""
                UPDATE jira_issues
                SET description_en = ?
                WHERE jira_key = ?
            """, (description_en, jira_key))
        else:
            # 先嘗試 SUBTASK 格式
            subtask_id = f"{ticket_id}-SUBTASK"
            cursor.execute("""
                UPDATE jira_issues
                SET description_en = ?
                WHERE ticket_id = ?
            """, (description_en, subtask_id))
            
            rows_updated = cursor.rowcount
            
            # 如果沒更新到，嘗試直接匹配
            if rows_updated == 0:
                cursor.execute("""
                    UPDATE jira_issues
                    SET description_en = ?
                    WHERE ticket_id = ?
                """, (description_en, ticket_id))
        
        rows_updated = cursor.rowcount
        
        # 更新 tickets 表的 description_en（如果存在）
        cursor.execute("""
            UPDATE tickets
            SET description_en = ?
            WHERE ticket_id = ?
        """, (description_en, ticket_id))
        
        conn.commit()
        conn.close()
        return rows_updated > 0
    except Exception as e:
        print(f"  ⚠️  更新資料庫失敗 ({ticket_id}): {e}")
        return False


def get_ticket_status_from_db(ticket_id: str) -> Optional[tuple]:
    """從資料庫獲取 Ticket 的狀態資訊（優先查詢 SUBTASK 格式）"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 優先查詢 SUBTASK 格式（這些是未完成的）
        subtask_id = f"{ticket_id}-SUBTASK"
        cursor.execute("""
            SELECT jira_key, status
            FROM jira_issues
            WHERE ticket_id = ?
        """, (subtask_id,))
        
        result = cursor.fetchone()
        
        # 如果沒找到 SUBTASK，再嘗試直接匹配
        if not result:
            cursor.execute("""
                SELECT jira_key, status
                FROM jira_issues
                WHERE ticket_id = ?
            """, (ticket_id,))
            result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return result  # (jira_key, status)
    except Exception as e:
        print(f"  ⚠️  查詢資料庫失敗 ({ticket_id}): {e}")
    
    return None


def update_all_english_tickets_to_db(dry_run: bool = False):
    """將所有英文版本的 Tickets 更新到資料庫"""
    print("📋 開始將英文版本的 Tickets 更新到資料庫...\n")
    
    # 找出所有英文版本的 Ticket 文件
    english_ticket_files = list(TICKETS_DIR.rglob("*_en.md"))
    
    if not english_ticket_files:
        print("❌ 沒有找到英文版本的 Ticket 文件")
        return
    
    print(f"找到 {len(english_ticket_files)} 個英文版本的 Ticket 文件\n")
    
    success_count = 0
    skipped_count = 0
    failed_count = 0
    
    for ticket_file in sorted(english_ticket_files):
        print(f"處理 {ticket_file.relative_to(TICKETS_DIR)}...")
        
        # 解析 Ticket 文件
        ticket = parse_english_ticket_markdown(ticket_file)
        
        if not ticket["ticket_id"]:
            print(f"  ⚠️  無法解析 Ticket ID，跳過")
            skipped_count += 1
            continue
        
        # 從資料庫獲取狀態資訊
        db_info = get_ticket_status_from_db(ticket["ticket_id"])
        
        if not db_info:
            print(f"  ⚠️  找不到對應的資料庫記錄，跳過")
            skipped_count += 1
            continue
        
        jira_key, status = db_info
        
        # 只處理未完成的 tickets（狀態不是「完成」）
        # 允許的狀態：Backlog, To Do, In Progress, 或 NULL
        if status and status == "完成":
            print(f"  ⚠️  Ticket 已完成 ({status})，跳過")
            skipped_count += 1
            continue
        
        print(f"  Jira Key: {jira_key}, Status: {status}")
        
        # 建立描述文字
        description_en = build_description_text(ticket)
        
        if dry_run:
            print(f"  [DRY RUN] 將更新資料庫")
            print(f"    Description 長度：{len(description_en)} 字元")
            print(f"    Description 預覽：{description_en[:100]}...")
            success_count += 1
        else:
            # 更新資料庫（傳入 jira_key 以確保更新正確的記錄）
            if update_database_with_english_ticket(ticket["ticket_id"], description_en, jira_key):
                print(f"  ✅ 已更新資料庫")
                success_count += 1
            else:
                print(f"  ❌ 更新失敗")
                failed_count += 1
        
        print()
    
    print("="*70)
    print("✅ 更新完成！")
    print("="*70)
    print(f"   成功：{success_count} 個")
    print(f"   跳過：{skipped_count} 個")
    print(f"   失敗：{failed_count} 個")
    print("="*70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將英文版本的 Ticket 文件更新到資料庫")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際更新）")
    args = parser.parse_args()
    
    update_all_english_tickets_to_db(dry_run=args.dry_run)

