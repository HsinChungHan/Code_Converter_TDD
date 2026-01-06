#!/usr/bin/env python3
"""
將資料庫中的英文版本同步到 Jira 平台

從資料庫讀取未完成 tickets 的英文內容（summary_en, description_en），
更新到 Jira 平台，只保留英文內容。

使用方式：
python scripts/sync_english_to_jira.py [--dry-run] [--force]
"""

import os
import argparse
import sqlite3
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

# 資料庫路徑（在 jira_integration 目錄下）
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"
# Ticket 文件目錄（在 output 目錄下，此腳本不需要讀取 Ticket 文件，但保留變數以備用）
TICKETS_DIR = Path(__file__).parent.parent.parent / "output" / "LiveChat&PrematchComment" / "12_Tickets"


def text_to_adf(text: str) -> Dict:
    """將純文字轉換為 Jira ADF 格式"""
    if not text:
        return {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": ""}]
            }]
        }
    
    lines = text.split('\n')
    adf_content = []
    current_section = None
    current_items = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # 空行，結束當前區塊
            if current_items:
                adf_content.append({
                    "type": "bulletList",
                    "content": current_items
                })
                current_items = []
            continue
        
        # 檢查是否是區塊標題
        if line == "Requirements:":
            if current_items:
                adf_content.append({
                    "type": "bulletList",
                    "content": current_items
                })
                current_items = []
            adf_content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Requirements"}]
            })
            current_section = "requirements"
        elif line == "Acceptance Criteria:":
            if current_items:
                adf_content.append({
                    "type": "bulletList",
                    "content": current_items
                })
                current_items = []
            adf_content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Acceptance Criteria"}]
            })
            current_section = "acceptance"
        elif line == "Related Documents:":
            if current_items:
                adf_content.append({
                    "type": "bulletList",
                    "content": current_items
                })
                current_items = []
            adf_content.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Related Documents"}]
            })
            current_section = "documents"
        elif line.startswith('- '):
            # 列表項
            item_text = line[2:].strip()
            current_items.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": item_text}]
                }]
            })
        elif line.startswith('- [ ]') or line.startswith('- [x]'):
            # 任務列表項
            item_text = line[5:].strip() if line.startswith('- [ ]') else line[6:].strip()
            current_items.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": item_text}]
                }]
            })
        else:
            # 普通文字段落
            if current_items:
                adf_content.append({
                    "type": "bulletList",
                    "content": current_items
                })
                current_items = []
            adf_content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}]
            })
    
    # 處理最後的列表項
    if current_items:
        adf_content.append({
            "type": "bulletList",
            "content": current_items
        })
    
    return {
        "type": "doc",
        "version": 1,
        "content": adf_content if adf_content else [{
            "type": "paragraph",
            "content": [{"type": "text", "text": text}]
        }]
    }


def get_uncompleted_tickets_from_db() -> List[Dict]:
    """從資料庫獲取所有未完成的 tickets 及其英文內容"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查詢未完成的 tickets（狀態不是「完成」）
        cursor.execute("""
            SELECT ticket_id, jira_key, summary_en, description_en, status
            FROM jira_issues
            WHERE (status != '完成' OR status IS NULL)
              AND ticket_id LIKE 'TDD-%'
            ORDER BY ticket_id
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        tickets = []
        for row in results:
            ticket_id, jira_key, summary_en, description_en, status = row
            tickets.append({
                "ticket_id": ticket_id,
                "jira_key": jira_key,
                "summary_en": summary_en,
                "description_en": description_en,
                "status": status
            })
        
        return tickets
    except Exception as e:
        print(f"❌ 查詢資料庫失敗：{e}")
        return []


def update_jira_issue_english_only(jira_key: str, summary_en: str, description_en: Optional[str] = None) -> bool:
    """更新 Jira Issue，只使用英文內容"""
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    # 構建更新內容（只使用英文）
    update_fields = {
        "summary": summary_en
    }
    
    if description_en:
        # 將描述文字轉換為 ADF 格式
        description_adf = text_to_adf(description_en)
        update_fields["description"] = description_adf
    
    payload = {
        "fields": update_fields
    }
    
    try:
        response = requests.put(url, json=payload, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  更新 Issue 失敗 ({jira_key}): {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   回應：{e.response.text[:500]}")
        return False


def sync_english_to_jira(dry_run: bool = False, force: bool = False):
    """將資料庫中的英文版本同步到 Jira"""
    print("📋 開始將英文版本同步到 Jira 平台...\n")
    
    if not dry_run and not force:
        try:
            confirm = input("⚠️  確定要將所有未完成 tickets 的英文內容更新到 Jira 嗎？(yes/no): ")
            if confirm.lower() != "yes":
                print("❌ 操作已取消")
                return
        except EOFError:
            print("❌ 無法讀取輸入，請使用 --force 參數跳過確認")
            return
    
    # 從資料庫獲取未完成的 tickets
    tickets = get_uncompleted_tickets_from_db()
    
    if not tickets:
        print("❌ 沒有找到未完成的 tickets")
        return
    
    print(f"找到 {len(tickets)} 個未完成的 tickets\n")
    
    success_count = 0
    skipped_count = 0
    failed_count = 0
    
    for ticket in tickets:
        jira_key = ticket["jira_key"]
        summary_en = ticket["summary_en"]
        description_en = ticket["description_en"]
        
        print(f"處理 {jira_key} ({ticket['ticket_id']})...")
        
        # 檢查是否有英文內容
        if not summary_en:
            print(f"  ⚠️  沒有英文標題，跳過")
            skipped_count += 1
            continue
        
        if dry_run:
            print(f"  [DRY RUN] 將更新")
            print(f"    Summary: {summary_en}")
            if description_en:
                print(f"    Description 長度：{len(description_en)} 字元")
                print(f"    Description 預覽：{description_en[:100]}...")
            success_count += 1
        else:
            # 更新 Jira Issue
            if update_jira_issue_english_only(jira_key, summary_en, description_en):
                print(f"  ✅ 已更新 {jira_key}")
                success_count += 1
            else:
                print(f"  ❌ 更新失敗 {jira_key}")
                failed_count += 1
        
        print()
    
    print("="*70)
    print("✅ 同步完成！")
    print("="*70)
    print(f"   成功：{success_count} 個")
    print(f"   跳過：{skipped_count} 個")
    print(f"   失敗：{failed_count} 個")
    print("="*70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="將資料庫中的英文版本同步到 Jira 平台")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際更新）")
    parser.add_argument("--force", action="store_true", help="強制執行，跳過確認")
    args = parser.parse_args()
    
    sync_english_to_jira(dry_run=args.dry_run, force=args.force)

