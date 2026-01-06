#!/usr/bin/env python3
"""
為所有 Ticket 文件創建中英版本

將現有的中文 Ticket 文件擴展為中英雙語版本，在同一個文件中提供中英文對照。

使用方式：
python scripts/create_bilingual_tickets.py [--dry-run]
"""

import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# Ticket 文件目錄（在 output 目錄下）
TICKETS_DIR = Path(__file__).parent.parent.parent / "output" / "LiveChat&PrematchComment" / "12_Tickets"


def translate_text(text: str) -> str:
    """翻譯文字為英文"""
    if not text:
        return ""
    
    # 完整匹配的翻譯字典
    full_translations = {
        "Ticket 資訊": "Ticket Information",
        "標題": "Title",
        "類型": "Type",
        "優先級": "Priority",
        "所屬 Feature": "Feature",
        "依賴 Ticket": "Dependencies",
        "Story Point": "Story Point",
        "估時（Senior iOS Engineer + AI 輔助）": "Estimation (Senior iOS Engineer + AI Assisted)",
        "標準": "Standard",
        "最嚴厲": "Most Stringent",
        "天": "days",
        "描述": "Description",
        "需求": "Requirements",
        "驗收條件": "Acceptance Criteria",
        "相關文件": "Related Documents",
        "Domain Model": "Domain Model",
        "Client": "Client",
        "API": "API",
        "Repository": "Repository",
        "UseCase": "UseCase",
        "Feature": "Feature",
        "View": "View",
        "P0": "P0",
        "P1": "P1",
        "P2": "P2",
        "P3": "P3",
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
        (r"支援\s+", "Support "),
        (r"整合\s+", "Integrate "),
        (r"處理\s+", "Handle "),
    ]
    
    for pattern, replacement in phrase_translations:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # 翻譯常見名詞和術語（按長度排序，先匹配長的）
    replacements = [
        (r"UseCase 商業邏輯", "UseCase Business Logic"),
        (r"所有欄位類型", "All Fields Types"),
        (r"所有欄位", "All Fields"),
        (r"必要欄位", "Required Fields"),
        (r"實作正確", "Implementation Correct"),
        (r"定義完成", "Definition Complete"),
        (r"實作完成", "Implementation Complete"),
        (r"類型正確", "Correct Types"),
        (r"業務邏輯", "Business Logic"),
        (r"錯誤處理", "Error Handling"),
        (r"UI 元件", "UI Components"),
        (r"相關\s+", "Related "),
        (r"規格", "Specifications"),
        (r"結構", "Structure"),
        (r"欄位", "Fields"),
        (r"必要", "Required"),
        (r"透過", "via"),
        (r"比較", "Comparison"),
        (r"覆蓋率", "Coverage"),
        (r"驗證", "Validation"),
        (r"呼叫", "Call"),
        (r"方法", "Methods"),
        (r"邏輯", "Logic"),
        (r"分頁", "Pagination"),
        (r"排序", "Sorting"),
        (r"過濾", "Filtering"),
        (r"狀態", "State"),
        (r"動作", "Action"),
        (r"更新", "Update"),
        (r"綁定", "Binding"),
        (r"互動", "Interaction"),
        (r"顯示", "Display"),
        (r"載入", "Loading"),
        (r"錯誤", "Error"),
        (r"成功", "Success"),
        (r"通過", "Passed"),
        (r"Entity", "Entity"),
        (r"Value Object", "Value Object"),
        (r"Value Objects", "Value Objects"),
        (r"TCA Reducer", "TCA Reducer"),
        (r"HTTP", "HTTP"),
        (r"WebSocket", "WebSocket"),
        (r"Domain Model", "Domain Model"),
        (r"Repository", "Repository"),
        (r"UseCase", "UseCase"),
        (r"Feature", "Feature"),
        (r"View", "View"),
        (r"Client", "Client"),
        (r"API", "API"),
        (r"PrematchComment", "PrematchComment"),
        (r"LiveChat", "LiveChat"),
        (r"Comment", "Comment"),
        (r"Chat", "Chat"),
        (r"Unit Test", "Unit Test"),
        (r"Integration Test", "Integration Test"),
        (r"UI Test", "UI Test"),
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
        # 處理頓號分隔的列表
        if "、" in content:
            parts = content.split("、")
            translated_parts = []
            for part in parts:
                part = part.strip()
                if re.match(r'^[A-Za-z0-9\s\-]+$', part):
                    translated_parts.append(part)
                else:
                    part_translated = re.sub(r'相關', 'Related ', part)
                    part_translated = re.sub(r'業務邏輯', 'Business Logic', part_translated)
                    part_translated = re.sub(r'\s+', ' ', part_translated).strip()
                    translated_parts.append(part_translated if part_translated != part else part)
            return f"({', '.join(translated_parts)})"
        return f"({content})"
    
    # 處理中文括號
    result = re.sub(r'（([^）]+)）', translate_brackets, result)
    result = re.sub(r'\(([^)]+)\)', translate_brackets, result)
    
    # 清理多餘空格
    result = re.sub(r'\s+', ' ', result).strip()
    result = re.sub(r'\s+\(', ' (', result)
    result = re.sub(r'\s+（', ' (', result)
    
    return result if result else text


def translate_table_row(row: str) -> str:
    """翻譯表格行"""
    # 提取欄位名和值
    match = re.match(r'\|\s*\*\*([^*]+)\*\*\s*\|\s*(.+?)\s*\|', row)
    if match:
        field_name = match.group(1).strip()
        field_value = match.group(2).strip()
        
        # 翻譯欄位名
        field_name_en = translate_text(field_name)
        
        # 翻譯欄位值（如果是中文）
        if re.search(r'[\u4e00-\u9fff]', field_value):
            # 如果值包含估時資訊，需要特殊處理
            if "標準" in field_value or "最嚴厲" in field_value:
                # 保持原有格式，只翻譯文字
                field_value_en = field_value
                field_value_en = field_value_en.replace("標準：", "Standard: ")
                field_value_en = field_value_en.replace("最嚴厲：", "Most Stringent: ")
                field_value_en = field_value_en.replace(" 天", " days")
                field_value_en = field_value_en.replace("天", "days")
                # 處理 <br/> 標籤（保持不變）
            else:
                field_value_en = translate_text(field_value)
            return f"| **{field_name}** / **{field_name_en}** | {field_value} / {field_value_en} |"
        else:
            # 值沒有中文，只翻譯欄位名
            return f"| **{field_name}** / **{field_name_en}** | {field_value} |"
    
    # 處理表格標題行（欄位 | 值）
    if '欄位' in row or '值' in row:
        row_en = row.replace('欄位', 'Field').replace('值', 'Value')
        return f"{row}\n{row_en}"
    
    return row


def translate_markdown_content(content: str) -> str:
    """翻譯 Markdown 內容，創建中英對照版本"""
    lines = content.split('\n')
    translated_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        # 處理標題
        if line.startswith('#'):
            # 提取標題文字
            match = re.match(r'(#+)\s*(.+)', line)
            if match:
                level = match.group(1)
                title = match.group(2)
                if re.search(r'[\u4e00-\u9fff]', title):
                    title_en = translate_text(title)
                    translated_lines.append(f"{level} {title} / {title_en}")
                else:
                    translated_lines.append(line)
            else:
                translated_lines.append(line)
        
        # 處理表格
        elif line.startswith('|'):
            if '---' in line:
                translated_lines.append(line)
                in_table = True
            elif in_table and not line.strip().startswith('| **'):
                # 翻譯表格行（非標題行）
                translated_row = translate_table_row(line)
                translated_lines.append(translated_row)
            else:
                translated_lines.append(line)
        
        # 處理列表項（任務列表）
        elif line.strip().startswith('- [ ]') or line.strip().startswith('- [x]'):
            # 提取列表項內容
            match = re.match(r'(\s*)(- \[[ x]\]) (.+)', line)
            if match:
                indent = match.group(1)
                checkbox = match.group(2)
                item_text = match.group(3)
                if re.search(r'[\u4e00-\u9fff]', item_text):
                    item_text_en = translate_text(item_text)
                    translated_lines.append(f"{indent}{checkbox} {item_text} / {item_text_en}")
                else:
                    translated_lines.append(line)
            else:
                translated_lines.append(line)
        
        # 處理編號列表
        elif re.match(r'^\s*\d+\.\s+', line):
            match = re.match(r'(\s*\d+\.\s+)(.+)', line)
            if match:
                prefix = match.group(1)
                item_text = match.group(2)
                if re.search(r'[\u4e00-\u9fff]', item_text):
                    item_text_en = translate_text(item_text)
                    translated_lines.append(f"{prefix}{item_text} / {item_text_en}")
                else:
                    translated_lines.append(line)
            else:
                translated_lines.append(line)
        
        # 處理普通文字段落
        else:
            # 空行保持不變
            if not line.strip():
                translated_lines.append(line)
            elif re.search(r'[\u4e00-\u9fff]', line):
                # 如果有中文，創建中英對照
                line_en = translate_text(line)
                if line_en != line and line_en:
                    translated_lines.append(f"{line} / {line_en}")
                else:
                    translated_lines.append(line)
            else:
                translated_lines.append(line)
    
    return '\n'.join(translated_lines)


def create_bilingual_ticket(ticket_path: Path, dry_run: bool = False, force: bool = False) -> bool:
    """為單個 Ticket 創建中英版本"""
    try:
        content = ticket_path.read_text(encoding='utf-8')
        
        # 檢查是否已經是雙語版本（但允許重新生成以改進翻譯）
        # 如果使用 --force 參數，會強制重新生成
        
        # 翻譯內容
        translated_content = translate_markdown_content(content)
        
        if dry_run:
            print(f"  [DRY RUN] 將更新 {ticket_path.name}")
            return True
        
        # 寫回文件
        ticket_path.write_text(translated_content, encoding='utf-8')
        print(f"  ✅ 已更新 {ticket_path.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ 處理失敗 {ticket_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="為所有 Ticket 文件創建中英版本")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際更新）")
    parser.add_argument("--force", action="store_true", help="強制重新生成（即使已經是雙語版本）")
    args = parser.parse_args()
    
    print("📋 開始為所有 Ticket 文件創建中英版本...\n")
    
    # 找出所有 Ticket 文件
    ticket_files = list(TICKETS_DIR.rglob("TDD-*.md"))
    
    if not ticket_files:
        print("❌ 沒有找到 Ticket 文件")
        return
    
    print(f"找到 {len(ticket_files)} 個 Ticket 文件\n")
    
    success_count = 0
    skipped_count = 0
    failed_count = 0
    
    for ticket_path in sorted(ticket_files):
        print(f"處理 {ticket_path.relative_to(TICKETS_DIR)}...")
        
        if create_bilingual_ticket(ticket_path, dry_run=args.dry_run, force=args.force):
            success_count += 1
        else:
            skipped_count += 1
    
    print()
    print("="*70)
    print("✅ 完成！")
    print("="*70)
    print(f"   成功：{success_count} 個")
    print(f"   跳過：{skipped_count} 個")
    print(f"   失敗：{failed_count} 個")
    print("="*70)


if __name__ == "__main__":
    main()

