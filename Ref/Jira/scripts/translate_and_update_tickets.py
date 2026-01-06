#!/usr/bin/env python3
"""
將未完成的 Jira Tickets 翻譯成英文並更新

1. 查詢所有未完成的 Main Tasks 和 Sub Tasks
2. 取得中文內容（summary, description）
3. 翻譯成英文
4. 更新資料庫（保存中英文對應關係）
5. 更新 Jira 平台

使用方式：
python scripts/translate_and_update_tickets.py [--dry-run] [--force]
"""

import requests
import os
import sys
import argparse
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"

# 未完成的 Tickets（Main Tasks 和 Sub Tasks）
MAIN_TASK_KEYS = [f"FOOTBALL-{i}" for i in range(9052, 9059)]
SUBTASK_KEYS = [f"FOOTBALL-{i}" for i in range(9059, 9085)]
ALL_TICKET_KEYS = MAIN_TASK_KEYS + SUBTASK_KEYS


def init_database_translation_fields():
    """初始化資料庫的翻譯欄位"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 檢查並新增英文欄位
    cursor.execute("PRAGMA table_info(jira_issues)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "summary_en" not in columns:
        cursor.execute("ALTER TABLE jira_issues ADD COLUMN summary_en TEXT")
        print("✅ 已新增 summary_en 欄位")
    
    if "description_en" not in columns:
        cursor.execute("ALTER TABLE jira_issues ADD COLUMN description_en TEXT")
        print("✅ 已新增 description_en 欄位")
    
    # 檢查 tickets 表
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "title_en" not in columns:
        cursor.execute("ALTER TABLE tickets ADD COLUMN title_en TEXT")
        print("✅ 已新增 tickets.title_en 欄位")
    
    if "description_en" not in columns:
        cursor.execute("ALTER TABLE tickets ADD COLUMN description_en TEXT")
        print("✅ 已新增 tickets.description_en 欄位")
    
    conn.commit()
    conn.close()


def translate_text(text: str, source_lang: str = "zh-TW", target_lang: str = "en") -> str:
    """翻譯文字（使用字典映射和規則）"""
    if not text:
        return ""
    
    import re
    
    # 完整匹配的翻譯字典
    full_translations = {
        # Main Tasks
        "Domain Model Layer": "Domain Model Layer",
        "API Layer": "API Layer",
        "Client Layer": "Client Layer",
        "Repository Layer": "Repository Layer",
        "UseCase Layer": "UseCase Layer",
        "Feature Layer": "Feature Layer",
        "View Layer": "View Layer",
    }
    
    # 如果完全匹配，直接返回
    if text in full_translations:
        return full_translations[text]
    
    # 部分匹配和替換規則
    result = text
    
    # 先處理常見的完整短語
    phrase_translations = [
        (r"實作所有\s+", "Implement All "),
        (r"定義所有\s+", "Define All "),
        (r"實作\s+", "Implement "),
        (r"定義\s+", "Define "),
    ]
    
    for pattern, replacement in phrase_translations:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # 翻譯常見名詞和術語
    replacements = [
        (r"相關\s+", "Related "),
        (r"業務邏輯", "Business Logic"),
        (r"UI 元件", "UI Components"),
        (r"規格", "Specifications"),
        (r"Domain Model", "Domain Model"),
        (r"Entity", "Entity"),
        (r"Value Object", "Value Object"),
        (r"Value Objects", "Value Objects"),
        (r"Repository", "Repository"),
        (r"UseCase", "UseCase"),
        (r"Feature", "Feature"),
        (r"View", "View"),
        (r"TCA Reducer", "TCA Reducer"),
        (r"HTTP Client", "HTTP Client"),
        (r"WebSocket Client", "WebSocket Client"),
        (r"PrematchComment API", "PrematchComment API"),
        (r"Chat API", "Chat API"),
        (r"PrematchComment", "PrematchComment"),
        (r"LiveChat", "LiveChat"),
        (r"Comment", "Comment"),
        (r"Chat", "Chat"),
    ]
    
    # 應用替換規則
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # 處理括號中的內容
    def translate_brackets(match):
        content = match.group(1)
        # 如果括號內容完全是英文或技術術語，保持不變
        if re.match(r'^[A-Za-z0-9\s\-\&]+$', content):
            return f"({content})"
        # 否則嘗試翻譯
        bracket_translations = {
            "TCA Reducer": "TCA Reducer",
            "HTTP": "HTTP",
            "WebSocket": "WebSocket",
            "Entity、Value Object": "Entity, Value Object",
            "PrematchComment API、Chat API": "PrematchComment API, Chat API",
            "HTTP Client、WebSocket Client": "HTTP Client, WebSocket Client",
            "PrematchComment Repository、LiveChat Repository": "PrematchComment Repository, LiveChat Repository",
            "Comment、Chat 相關業務邏輯": "Comment and Chat Related Business Logic",
            "UI 元件": "UI Components",
        }
        # 先檢查完整匹配
        if content in bracket_translations:
            return f"({bracket_translations[content]})"
        # 處理頓號分隔的列表
        if "、" in content:
            parts = content.split("、")
            translated_parts = []
            for part in parts:
                part = part.strip()
                if part in bracket_translations:
                    translated_parts.append(bracket_translations[part])
                elif re.match(r'^[A-Za-z0-9\s\-]+$', part):
                    translated_parts.append(part)
                else:
                    # 簡單翻譯
                    part_translated = re.sub(r'相關', 'Related ', part)
                    part_translated = re.sub(r'業務邏輯', 'Business Logic', part_translated)
                    part_translated = re.sub(r'\s+', ' ', part_translated).strip()
                    translated_parts.append(part_translated if part_translated != part else part)
            return f"({', '.join(translated_parts)})"
        return f"({content})"
    
    # 處理中文括號
    result = re.sub(r'（([^）]+)）', translate_brackets, result)
    result = re.sub(r'\(([^)]+)\)', translate_brackets, result)
    
    # 清理多餘空格，但保留括號前的空格
    result = re.sub(r'\s+', ' ', result).strip()
    # 修正括號前的空格
    result = re.sub(r'\s+\(', ' (', result)
    result = re.sub(r'\s+（', ' (', result)
    
    # 如果結果還是中文，使用基本規則
    if re.search(r'[\u4e00-\u9fff]', result):
        # 移除所有中文字符（作為後備方案）
        result = re.sub(r'[\u4e00-\u9fff]+', '', result).strip()
        result = re.sub(r'\s+', ' ', result).strip()
    
    return result if result else text


def get_issue_details(jira_key: str) -> Optional[Dict]:
    """取得 Issue 的詳細資訊"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    params = {
        "fields": "summary,description,status,assignee,issuetype,parent"
    }
    
    try:
        response = requests.get(url, headers=headers, auth=auth, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  查詢 Issue 失敗 ({jira_key})：{e}")
        return None


def update_jira_issue(jira_key: str, summary_en: str, description_en: Optional[str] = None) -> bool:
    """更新 Jira Issue 的內容為英文"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    # 構建更新內容
    update_fields = {
        "summary": summary_en
    }
    
    if description_en:
        # Jira 使用 ADF (Atlassian Document Format) 格式
        update_fields["description"] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": description_en
                        }
                    ]
                }
            ]
        }
    
    payload = {
        "fields": update_fields
    }
    
    try:
        response = requests.put(url, json=payload, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"⚠️  更新 Issue 失敗 ({jira_key})：{e}")
        if hasattr(e, 'response') and e.response:
            print(f"   回應：{e.response.text[:500]}")
        return False


def update_database(jira_key: str, summary_zh: str, summary_en: str, description_zh: Optional[str] = None, description_en: Optional[str] = None):
    """更新資料庫中的翻譯內容"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 更新 jira_issues 表
    cursor.execute("""
        UPDATE jira_issues
        SET summary_en = ?,
            description_en = ?
        WHERE jira_key = ?
    """, (summary_en, description_en, jira_key))
    
    # 如果有對應的 ticket_id，也更新 tickets 表
    cursor.execute("SELECT ticket_id FROM jira_issues WHERE jira_key = ?", (jira_key,))
    result = cursor.fetchone()
    if result:
        ticket_id = result[0]
        # 更新 tickets 表的 title_en（如果 summary 對應 title）
        cursor.execute("""
            UPDATE tickets
            SET title_en = ?,
                description_en = ?
            WHERE ticket_id = ?
        """, (summary_en, description_en, ticket_id))
    
    conn.commit()
    conn.close()


def translate_and_update_tickets(dry_run: bool = False, force: bool = False):
    """翻譯並更新所有未完成的 Tickets"""
    print("📋 開始翻譯並更新未完成的 Tickets...\n")
    
    if not dry_run and not force:
        try:
            confirm = input("⚠️  確定要將所有未完成的 Tickets 翻譯成英文並更新到 Jira 嗎？(yes/no): ")
            if confirm.lower() != "yes":
                print("❌ 操作已取消")
                return
        except EOFError:
            print("❌ 無法讀取輸入，請使用 --force 參數跳過確認")
            return
    
    # 初始化資料庫欄位
    print("正在初始化資料庫欄位...")
    init_database_translation_fields()
    print()
    
    # 處理所有 Tickets
    print(f"正在處理 {len(ALL_TICKET_KEYS)} 個 Tickets...\n")
    
    success_count = 0
    failed_count = 0
    
    for jira_key in ALL_TICKET_KEYS:
        print(f"處理 {jira_key}...")
        
        # 取得 Issue 詳細資訊
        issue_data = get_issue_details(jira_key)
        if not issue_data:
            print(f"  ❌ 無法取得 Issue 資訊")
            failed_count += 1
            continue
        
        fields = issue_data.get("fields", {})
        summary_zh = fields.get("summary", "")
        description = fields.get("description")
        
        # 處理 description（可能是 ADF 格式）
        description_zh = None
        if description:
            if isinstance(description, dict):
                # ADF 格式，提取文字
                content = description.get("content", [])
                text_parts = []
                for item in content:
                    if item.get("type") == "paragraph":
                        para_content = item.get("content", [])
                        for para_item in para_content:
                            if para_item.get("type") == "text":
                                text_parts.append(para_item.get("text", ""))
                description_zh = "\n".join(text_parts) if text_parts else None
            else:
                description_zh = str(description)
        
        # 翻譯
        summary_en = translate_text(summary_zh)
        description_en = translate_text(description_zh) if description_zh else None
        
        print(f"  中文: {summary_zh}")
        print(f"  英文: {summary_en}")
        if description_zh:
            print(f"  描述（中文）: {description_zh[:50]}...")
            if description_en:
                print(f"  描述（英文）: {description_en[:50]}...")
        
        if dry_run:
            print(f"  [DRY RUN] 將更新為英文")
            success_count += 1
        else:
            # 更新資料庫
            update_database(jira_key, summary_zh, summary_en, description_zh, description_en)
            
            # 更新 Jira
            if update_jira_issue(jira_key, summary_en, description_en):
                print(f"  ✅ 已更新")
                success_count += 1
            else:
                print(f"  ❌ 更新失敗")
                failed_count += 1
        
        print()
    
    print("="*70)
    print("✅ 翻譯完成！")
    print("="*70)
    print(f"   成功：{success_count} 個")
    print(f"   失敗：{failed_count} 個")
    print("="*70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將未完成的 Jira Tickets 翻譯成英文並更新")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際更新）")
    parser.add_argument("--force", action="store_true", help="強制執行，跳過確認")
    args = parser.parse_args()
    
    translate_and_update_tickets(dry_run=args.dry_run, force=args.force)

