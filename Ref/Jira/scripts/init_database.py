#!/usr/bin/env python3
"""
初始化本地資料庫

建立 SQLite 資料庫並建立必要的資料表結構。
"""

import sqlite3
import os
from pathlib import Path

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"


def init_database():
    """初始化資料庫和資料表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 建立 tickets 表（本地 Ticket 資訊）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            priority TEXT NOT NULL,
            feature TEXT,
            story_point INTEGER,
            estimate_standard REAL,
            estimate_strict REAL,
            description TEXT,
            requirements TEXT,
            acceptance_criteria TEXT,
            related_documents TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 建立 jira_issues 表（Jira Issue 資訊）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jira_issues (
            ticket_id TEXT PRIMARY KEY,
            jira_key TEXT UNIQUE NOT NULL,
            jira_id TEXT,
            summary TEXT,
            status TEXT,
            assignee_account_id TEXT,
            assignee_display_name TEXT,
            reporter_account_id TEXT,
            reporter_display_name TEXT,
            priority TEXT,
            issue_type TEXT,
            labels TEXT,
            parent_key TEXT,
            original_estimate TEXT,
            time_spent TEXT,
            time_remaining TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            resolved_at TIMESTAMP,
            url TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
        )
    """)
    
    # 建立 dependencies 表（Ticket 依賴關係）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            depends_on_ticket_id TEXT NOT NULL,
            jira_key TEXT,
            depends_on_jira_key TEXT,
            FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id),
            FOREIGN KEY (depends_on_ticket_id) REFERENCES tickets(ticket_id)
        )
    """)
    
    # 建立 issue_links 表（Jira Issue 連結關係）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issue_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_jira_key TEXT NOT NULL,
            target_jira_key TEXT NOT NULL,
            link_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_jira_key, target_jira_key, link_type)
        )
    """)
    
    # 建立 sync_history 表（同步歷史記錄）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sync_type TEXT NOT NULL,
            sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tickets_synced INTEGER DEFAULT 0,
            issues_created INTEGER DEFAULT 0,
            issues_updated INTEGER DEFAULT 0,
            links_created INTEGER DEFAULT 0,
            errors TEXT,
            status TEXT DEFAULT 'success'
        )
    """)
    
    # 建立索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jira_key ON jira_issues(jira_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_type ON tickets(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_feature ON tickets(feature)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_priority ON tickets(priority)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_ticket ON dependencies(ticket_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_depends_on ON dependencies(depends_on_ticket_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_issue_links_source ON issue_links(source_jira_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_issue_links_target ON issue_links(target_jira_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sync_history_time ON sync_history(sync_time)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ 資料庫初始化完成：{DB_PATH}")
    print("   已建立以下資料表：")
    print("   - tickets（本地 Ticket 資訊）")
    print("   - jira_issues（Jira Issue 資訊）")
    print("   - dependencies（Ticket 依賴關係）")
    print("   - issue_links（Jira Issue 連結關係）")
    print("   - sync_history（同步歷史記錄）")


if __name__ == "__main__":
    init_database()

