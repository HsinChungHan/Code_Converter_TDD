#!/usr/bin/env python3
"""
將本地 Ticket Markdown 檔案載入到資料庫

使用方式：
python scripts/load_tickets_to_db.py
"""

import sqlite3
import re
from pathlib import Path
from typing import Dict, Optional

# 資料庫路徑（在 jira_integration 目錄下）
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"
# Ticket 文件目錄（在 output 目錄下）
TICKETS_DIR = Path(__file__).parent.parent.parent / "output" / "LiveChat&PrematchComment" / "12_Tickets"


def parse_ticket_file(file_path: Path) -> Optional[Dict]:
    """解析 Ticket Markdown 檔案"""
    content = file_path.read_text(encoding="utf-8")
    
    ticket = {}
    
    # 解析 Ticket ID
    ticket_id_match = re.search(r'\| \*\*Ticket ID\*\* \| (.+?) \|', content)
    if ticket_id_match:
        ticket["ticket_id"] = ticket_id_match.group(1).strip()
    else:
        return None
    
    # 解析標題
    title_match = re.search(r'\| \*\*標題\*\* \| (.+?) \|', content)
    if title_match:
        ticket["title"] = title_match.group(1).strip()
    
    # 解析類型
    type_match = re.search(r'\| \*\*類型\*\* \| (.+?) \|', content)
    if type_match:
        ticket["type"] = type_match.group(1).strip()
    
    # 解析優先級
    priority_match = re.search(r'\| \*\*優先級\*\* \| (.+?) \|', content)
    if priority_match:
        ticket["priority"] = priority_match.group(1).strip()
    
    # 解析所屬 Feature
    feature_match = re.search(r'\| \*\*所屬 Feature\*\* \| (.+?) \|', content)
    if feature_match:
        ticket["feature"] = feature_match.group(1).strip()
    
    # 解析 Story Point
    sp_match = re.search(r'\| \*\*Story Point\*\* \| (\d+) \|', content)
    if sp_match:
        ticket["story_point"] = int(sp_match.group(1))
    
    # 解析估時（標準）
    estimate_match = re.search(r'\| \*\*估時.*?\*\* \| 標準：(\d+(?:\.\d+)?) 天', content)
    if estimate_match:
        ticket["estimate_standard"] = float(estimate_match.group(1))
    
    # 解析估時（最嚴厲）
    estimate_strict_match = re.search(r'最嚴厲：(\d+(?:\.\d+)?) 天', content)
    if estimate_strict_match:
        ticket["estimate_strict"] = float(estimate_strict_match.group(1))
    
    # 解析描述
    desc_match = re.search(r'## 描述\s*\n\s*\n(.+?)(?=\n## |$)', content, re.DOTALL)
    if desc_match:
        ticket["description"] = desc_match.group(1).strip()
    
    # 解析需求
    req_match = re.search(r'## 需求\s*\n\s*\n(.+?)(?=\n## |$)', content, re.DOTALL)
    if req_match:
        ticket["requirements"] = req_match.group(1).strip()
    
    # 解析驗收條件
    ac_match = re.search(r'## 驗收條件\s*\n\s*\n(.+?)(?=\n## |$)', content, re.DOTALL)
    if ac_match:
        ticket["acceptance_criteria"] = ac_match.group(1).strip()
    
    # 解析相關文件
    doc_match = re.search(r'## 相關文件\s*\n\s*\n(.+?)(?=\n## |$)', content, re.DOTALL)
    if doc_match:
        ticket["related_documents"] = doc_match.group(1).strip()
    
    return ticket


def load_tickets_to_database():
    """將所有 Ticket 檔案載入到資料庫"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 找出所有 Ticket 檔案
    ticket_files = list(TICKETS_DIR.rglob("TDD-*.md"))
    
    print(f"📋 找到 {len(ticket_files)} 個 Ticket 檔案")
    
    loaded_count = 0
    error_count = 0
    
    for file_path in ticket_files:
        ticket = parse_ticket_file(file_path)
        
        if not ticket:
            print(f"⚠️  無法解析：{file_path.name}")
            error_count += 1
            continue
        
        # 插入或更新 tickets 表
        cursor.execute("""
            INSERT OR REPLACE INTO tickets (
                ticket_id, title, type, priority, feature,
                story_point, estimate_standard, estimate_strict,
                description, requirements, acceptance_criteria,
                related_documents, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            ticket.get("ticket_id"),
            ticket.get("title"),
            ticket.get("type"),
            ticket.get("priority"),
            ticket.get("feature"),
            ticket.get("story_point"),
            ticket.get("estimate_standard"),
            ticket.get("estimate_strict"),
            ticket.get("description"),
            ticket.get("requirements"),
            ticket.get("acceptance_criteria"),
            ticket.get("related_documents")
        ))
        
        loaded_count += 1
        print(f"   ✅ 載入：{ticket.get('ticket_id')} - {ticket.get('title')}")
    
    # 載入依賴關係
    print("\n📋 載入依賴關係...")
    
    for file_path in ticket_files:
        content = file_path.read_text(encoding="utf-8")
        
        # 解析 Ticket ID
        ticket_id_match = re.search(r'\| \*\*Ticket ID\*\* \| (.+?) \|', content)
        if not ticket_id_match:
            continue
        
        ticket_id = ticket_id_match.group(1).strip()
        
        # 解析依賴 Ticket
        deps_match = re.search(r'\| \*\*依賴 Ticket\*\* \| (.+?) \|', content)
        if deps_match:
            deps_str = deps_match.group(1).strip()
            if deps_str and deps_str != "-":
                dependencies = [d.strip() for d in deps_str.split(",")]
                
                for dep_ticket_id in dependencies:
                    cursor.execute("""
                        INSERT OR IGNORE INTO dependencies (
                            ticket_id, depends_on_ticket_id
                        ) VALUES (?, ?)
                    """, (ticket_id, dep_ticket_id))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 載入完成！")
    print(f"   成功載入：{loaded_count} 個 Ticket")
    print(f"   錯誤：{error_count} 個")


if __name__ == "__main__":
    load_tickets_to_database()

