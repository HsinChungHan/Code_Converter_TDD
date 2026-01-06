#!/usr/bin/env python3
"""
清理重複的翻譯內容

修復因為多次執行翻譯腳本導致的重複翻譯問題。

使用方式：
python scripts/cleanup_duplicate_translations.py
"""

import re
from pathlib import Path

# Ticket 文件目錄（在 output 目錄下）
TICKETS_DIR = Path(__file__).parent.parent.parent / "output" / "LiveChat&PrematchComment" / "12_Tickets"


def cleanup_line(line: str) -> str:
    """清理單行的重複翻譯"""
    # 如果一行中有多個 ' / '，只保留第一個
    if line.count(' / ') > 1:
        # 找到第一個 ' / ' 的位置
        first_slash = line.find(' / ')
        if first_slash > 0:
            # 提取中文部分和第一個英文翻譯
            chinese_part = line[:first_slash]
            after_slash = line[first_slash + len(' / '):]
            # 找到第一個英文翻譯的結尾（下一個 ' / ' 或行尾）
            next_slash = after_slash.find(' / ')
            if next_slash > 0:
                english_part = after_slash[:next_slash]
            else:
                english_part = after_slash
            
            # 重新組合
            return f"{chinese_part} / {english_part}"
    
    return line


def cleanup_file(file_path: Path) -> bool:
    """清理單個文件的重複翻譯"""
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        cleaned_lines = [cleanup_line(line) for line in lines]
        cleaned_content = '\n'.join(cleaned_lines)
        
        if cleaned_content != content:
            file_path.write_text(cleaned_content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"  ❌ 處理失敗 {file_path.name}: {e}")
        return False


def main():
    print("📋 開始清理重複的翻譯內容...\n")
    
    # 找出所有 Ticket 文件
    ticket_files = list(TICKETS_DIR.rglob("TDD-*.md"))
    
    if not ticket_files:
        print("❌ 沒有找到 Ticket 文件")
        return
    
    print(f"找到 {len(ticket_files)} 個 Ticket 文件\n")
    
    cleaned_count = 0
    
    for ticket_path in sorted(ticket_files):
        if cleanup_file(ticket_path):
            print(f"  ✅ 已清理 {ticket_path.relative_to(TICKETS_DIR)}")
            cleaned_count += 1
    
    print()
    print("="*70)
    print("✅ 清理完成！")
    print("="*70)
    print(f"   清理：{cleaned_count} 個文件")
    print(f"   未變更：{len(ticket_files) - cleaned_count} 個文件")
    print("="*70)


if __name__ == "__main__":
    main()

