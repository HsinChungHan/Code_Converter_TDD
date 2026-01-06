#!/usr/bin/env python3
"""
為所有 Ticket 文件創建獨立的英文版本

從現有的中英雙語版本中提取英文內容，並從資料庫獲取表格值的英文翻譯，
創建獨立的英文版本文件。

使用方式：
python scripts/create_english_versions.py [--dry-run]
"""

import re
import argparse
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# Ticket 文件目錄（在 output 目錄下）
TICKETS_DIR = Path(__file__).parent.parent.parent / "output" / "LiveChat&PrematchComment" / "12_Tickets"
# 資料庫路徑（在 jira_integration 目錄下）
DB_PATH = Path(__file__).parent.parent / "jira_tickets.db"


def get_translation_from_db(ticket_id: str) -> Optional[Dict]:
    """從資料庫獲取 ticket 的英文翻譯"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查詢 ticket 的英文翻譯
        cursor.execute('''
            SELECT summary, summary_en, description_en
            FROM jira_issues
            WHERE ticket_id = ?
        ''', (ticket_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'summary_zh': result[0],
                'summary_en': result[1],
                'description_en': result[2]
            }
    except Exception as e:
        print(f"  ⚠️  無法從資料庫獲取翻譯 ({ticket_id}): {e}")
    
    return None


def translate_text(text: str) -> str:
    """翻譯文字為英文（使用簡單的字典映射）"""
    if not text:
        return ""
    
    # 翻譯映射
    translations = {
        "實作": "Implement",
        "定義": "Define",
        "所有": "All",
        "必要": "Required",
        "欄位": "Fields",
        "類型": "Type",
        "正確": "Correct",
        "完成": "Complete",
        "透過": "via",
        "比較": "Comparison",
        "標準": "Standard",
        "最嚴厲": "Most Stringent",
        "天": "days",
    }
    
    result = text
    for zh, en in translations.items():
        result = result.replace(zh, en)
    
    return result


def extract_english_content(content: str, ticket_id: Optional[str] = None) -> str:
    """從中英雙語內容中提取英文部分"""
    lines = content.split('\n')
    english_lines = []
    in_table = False
    table_header_processed = False
    
    for i, line in enumerate(lines):
        # 處理標題（格式：## 中文 / English）
        if line.startswith('#'):
            match = re.match(r'(#+)\s*(.+?)\s*/\s*(.+)', line)
            if match:
                level = match.group(1)
                english_title = match.group(3).strip()
                english_lines.append(f"{level} {english_title}")
            else:
                # 如果沒有 / 分隔符，可能是純英文標題
                english_lines.append(line)
        
        # 處理表格行
        elif line.startswith('|'):
            if '---' in line:
                english_lines.append(line)
                in_table = True
            elif in_table:
                # 處理表格內容行
                parts = line.split('|')
                english_parts = []
                
                for part in parts:
                    part = part.strip()
                    
                    # 處理表格標題行（欄位 | 值）
                    if not table_header_processed:
                        if '欄位' in part and '值' not in part:
                            english_parts.append('Field')
                            continue
                        elif '值' in part:
                            english_parts.append('Value')
                            table_header_processed = True
                            continue
                    
                    # 如果有 / 分隔符，提取英文部分
                    if ' / ' in part:
                        # 處理 **欄位名 / Field Name** 格式
                        if '**' in part:
                            match = re.search(r'\*\*(.+?)\s*/\s*(.+?)\*\*', part)
                            if match:
                                english_part = f"**{match.group(2).strip()}**"
                            else:
                                # 提取最後一個 / 後面的內容
                                english_part = part.split(' / ')[-1].strip()
                        else:
                            # 提取最後一個 / 後面的內容
                            english_part = part.split(' / ')[-1].strip()
                        
                        # 處理估時欄位的特殊格式
                        if '標準' in part or '最嚴厲' in part:
                            # 提取英文部分並替換中文
                            english_part = part
                            english_part = english_part.replace('標準：', 'Standard: ')
                            english_part = english_part.replace('最嚴厲：', 'Most Stringent: ')
                            english_part = english_part.replace(' 天', ' days')
                            english_part = english_part.replace('天', 'days')
                            # 移除中文部分
                            if ' / ' in english_part:
                                english_part = english_part.split(' / ')[-1].strip()
                        
                        english_parts.append(english_part)
                    else:
                        # 沒有 / 分隔符
                        # 如果包含中文，嘗試翻譯
                        if re.search(r'[\u4e00-\u9fff]', part):
                            # 嘗試從資料庫獲取翻譯
                            if ticket_id and '標題' in part or '實作' in part or '定義' in part:
                                # 這可能是標題欄位，嘗試翻譯
                                translated = translate_text(part)
                                if translated != part:
                                    english_parts.append(translated)
                                else:
                                    # 無法翻譯，跳過
                                    continue
                            else:
                                # 其他中文內容，嘗試簡單翻譯
                                translated = translate_text(part)
                                if translated != part:
                                    english_parts.append(translated)
                                else:
                                    # 無法翻譯，跳過
                                    continue
                        else:
                            # 純英文或數字，保留
                            english_parts.append(part)
                
                if english_parts and len(english_parts) > 1:
                    english_lines.append('| ' + ' | '.join(english_parts) + ' |')
        
        # 處理列表項和段落（格式：中文 / English）
        elif ' / ' in line:
            # 提取英文部分
            english_part = line.split(' / ')[-1].strip()
            # 如果英文部分不為空，使用英文部分
            if english_part:
                english_lines.append(english_part)
            else:
                english_lines.append(line)
        
        # 處理純英文行或空行
        else:
            # 如果是空行，保留
            if not line.strip():
                english_lines.append(line)
            # 如果是純英文行，保留
            elif not re.search(r'[\u4e00-\u9fff]', line):
                english_lines.append(line)
            # 如果包含中文但沒有 / 分隔符，可能是文件路徑等，保持不變
            elif '`' in line or 'http' in line.lower() or 'output/' in line:
                english_lines.append(line)
    
    return '\n'.join(english_lines)


def create_english_version(ticket_path: Path, dry_run: bool = False) -> bool:
    """為單個 Ticket 創建英文版本"""
    try:
        content = ticket_path.read_text(encoding='utf-8')
        
        # 從文件名提取 ticket_id（例如：TDD-001_Comment_Entity.md -> TDD-001）
        ticket_id_match = re.search(r'(TDD-\d+)', ticket_path.stem)
        ticket_id = ticket_id_match.group(1) if ticket_id_match else None
        
        # 提取英文內容
        english_content = extract_english_content(content, ticket_id)
        
        # 創建英文版本文件路徑（在相同目錄下，文件名加 _en 後綴）
        english_path = ticket_path.parent / f"{ticket_path.stem}_en.md"
        
        if dry_run:
            print(f"  [DRY RUN] 將創建 {english_path.name}")
            return True
        
        # 寫入英文版本文件
        english_path.write_text(english_content, encoding='utf-8')
        print(f"  ✅ 已創建 {english_path.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ 處理失敗 {ticket_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="為所有 Ticket 文件創建獨立的英文版本")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際創建文件）")
    args = parser.parse_args()
    
    print("📋 開始為所有 Ticket 文件創建英文版本...\n")
    
    # 找出所有 Ticket 文件（排除已存在的 _en 版本）
    ticket_files = [
        f for f in TICKETS_DIR.rglob("TDD-*.md")
        if not f.name.endswith("_en.md")
    ]
    
    if not ticket_files:
        print("❌ 沒有找到 Ticket 文件")
        return
    
    print(f"找到 {len(ticket_files)} 個 Ticket 文件\n")
    
    success_count = 0
    failed_count = 0
    
    for ticket_path in sorted(ticket_files):
        print(f"處理 {ticket_path.relative_to(TICKETS_DIR)}...")
        
        if create_english_version(ticket_path, dry_run=args.dry_run):
            success_count += 1
        else:
            failed_count += 1
    
    print()
    print("="*70)
    print("✅ 完成！")
    print("="*70)
    print(f"   成功：{success_count} 個")
    print(f"   失敗：{failed_count} 個")
    print("="*70)


if __name__ == "__main__":
    main()

