#!/usr/bin/env python3
"""
修正所有英文版本的 Ticket 文件

1. 將 Requirements 改為編號列表格式（1. xxx）
2. 將 Acceptance Criteria 改為任務列表格式（- [ ] xxx）
3. 翻譯所有中文內容為英文
"""

import re
from pathlib import Path
from typing import Dict, List

# Ticket 文件目錄（在 output 目錄下）
TICKETS_DIR = Path(__file__).parent.parent.parent / "output" / "LiveChat&PrematchComment" / "12_Tickets"


def translate_text(text: str) -> str:
    """翻譯常見的中文詞彙為英文"""
    if not text:
        return ""
    
    # 完整匹配的翻譯字典
    translations = {
        "和": "and",
        "定義": "Define",
        "實作": "Implement",
        "所有": "all",
        "必要": "required",
        "欄位": "fields",
        "類型": "types",
        "正確": "correct",
        "完成": "Complete",
        "透過": "via",
        "比較": "compare",
        "覆蓋率": "Coverage",
        "商業": "Business",
        "邏輯": "Logic",
        "整合": "Integrate",
        "呼叫": "Call",
        "驗證": "Validation",
        "錯誤": "Error",
        "處理": "Handling",
        "支援": "Support",
        "分頁": "Pagination",
        "最新": "newest",
        "重新載入": "refresh",
        "分支": "Branch",
        "測試": "Test",
        "通過": "Passed",
        "定義：": "Definition:",
        "模型：": "Model:",
        "場景：": "Scenarios:",
    }
    
    result = text
    
    # 先處理完整短語
    phrase_translations = [
        (r"定義所有RequiredFields\((.+?)\)", r"Define all required fields (\1)"),
        (r"所有FieldsCorrect Types", "All fields have correct types"),
        (r"Equatable 實作正確\(透過 id 比較\)", "Equatable implementation is correct (compare via id)"),
        (r"實作正確\(透過 id 比較\)", "implementation is correct (compare via id)"),
        (r"UseCase 商業Logic", "UseCase Business Logic"),
        (r"商業Logic", "Business Logic"),
        (r"Repository Call", "Repository Call"),
        (r"Input/Output Model Validation", "Input/Output Model Validation"),
        (r"Error Handling", "Error Handling"),
        (r"支援Pagination\(cursor\)", "Support Pagination (cursor)"),
        (r"UseCase Business LogicImplementation Complete", "UseCase Business Logic Implementation Complete"),
        (r"Business LogicImplementation Complete", "Business Logic Implementation Complete"),
        (r"refresh", "Refresh comment list"),
        (r"newest）", "newest)"),
        (r"Branch", "All branches tested"),
        (r"Unit Test Coverage", "Unit Test Coverage"),
        (r"Integration Test Passed", "Integration Test Passed"),
        (r"Domain Model 定義：", "Domain Model Definition:"),
        (r"UseCase 定義：", "UseCase Definition:"),
        (r"Input/Output Model：", "Input/Output Model:"),
        (r"Test Scenarios：", "Test Scenarios:"),
    ]
    
    for pattern, replacement in phrase_translations:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # 處理單詞翻譯
    for zh, en in translations.items():
        result = result.replace(zh, en)
    
    # 清理多餘空格
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


def fix_requirements_section(content: str) -> str:
    """修正 Requirements 部分"""
    # 找到 Requirements 區塊
    req_match = re.search(r'## Requirements\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not req_match:
        return content
    
    req_text = req_match.group(1).strip()
    lines = [line.strip() for line in req_text.split('\n') if line.strip()]
    
    # 如果已經是編號列表格式，檢查是否需要翻譯
    if lines and re.match(r'^\d+\.', lines[0]):
        # 已經是編號列表，只需要翻譯中文
        fixed_lines = []
        for line in lines:
            # 移除編號前綴
            match = re.match(r'^(\d+\.\s*)(.+)', line)
            if match:
                prefix = match.group(1)
                text = match.group(2)
                translated = translate_text(text)
                fixed_lines.append(f"{prefix}{translated}")
            else:
                fixed_lines.append(translate_text(line))
    else:
        # 不是編號列表，轉換為編號列表並翻譯
        fixed_lines = []
        for i, line in enumerate(lines, 1):
            translated = translate_text(line)
            fixed_lines.append(f"{i}. {translated}")
    
    # 替換原內容
    new_req_text = '\n'.join(fixed_lines)
    # 確保標題後只有一個空行
    new_content = content[:req_match.start(1)] + '\n\n' + new_req_text + '\n' + content[req_match.end(1):]
    # 移除多餘的空行
    new_content = re.sub(r'\n\n\n+', '\n\n', new_content)
    
    return new_content


def fix_acceptance_criteria_section(content: str) -> str:
    """修正 Acceptance Criteria 部分"""
    # 找到 Acceptance Criteria 區塊
    ac_match = re.search(r'## Acceptance Criteria\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not ac_match:
        return content
    
    ac_text = ac_match.group(1).strip()
    lines = [line.strip() for line in ac_text.split('\n') if line.strip()]
    
    # 如果已經是任務列表格式，檢查是否需要翻譯
    if lines and re.match(r'^- \[[ x]\]', lines[0]):
        # 已經是任務列表，只需要翻譯中文
        fixed_lines = []
        for line in lines:
            match = re.match(r'^(- \[[ x]\]\s*)(.+)', line)
            if match:
                prefix = match.group(1)
                text = match.group(2)
                translated = translate_text(text)
                fixed_lines.append(f"{prefix}{translated}")
            else:
                fixed_lines.append(translate_text(line))
    else:
        # 不是任務列表，轉換為任務列表並翻譯
        fixed_lines = []
        for line in lines:
            translated = translate_text(line)
            fixed_lines.append(f"- [ ] {translated}")
    
    # 替換原內容
    new_ac_text = '\n'.join(fixed_lines)
    # 確保標題後只有一個空行
    new_content = content[:ac_match.start(1)] + '\n\n' + new_ac_text + '\n' + content[ac_match.end(1):]
    # 移除多餘的空行
    new_content = re.sub(r'\n\n\n+', '\n\n', new_content)
    
    return new_content


def fix_related_documents_section(content: str) -> str:
    """修正 Related Documents 部分"""
    # 找到 Related Documents 區塊
    doc_match = re.search(r'## Related Documents\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not doc_match:
        return content
    
    doc_text = doc_match.group(1).strip()
    lines = doc_text.split('\n')
    
    fixed_lines = []
    for line in lines:
        if line.strip():
            translated = translate_text(line)
            # 修正冒號後的空格（例如：Definition:`path` -> Definition: `path`）
            translated = re.sub(r'([a-zA-Z]):`', r'\1: `', translated)
            fixed_lines.append(translated)
        else:
            fixed_lines.append(line)
    
    # 替換原內容
    new_doc_text = '\n'.join(fixed_lines)
    # 確保標題後只有一個空行
    new_content = content[:doc_match.start(1)] + '\n\n' + new_doc_text + '\n' + content[doc_match.end(1):]
    # 移除多餘的空行
    new_content = re.sub(r'\n\n\n+', '\n\n', new_content)
    
    return new_content


def fix_english_ticket(file_path: Path) -> bool:
    """修正單個英文版本的 Ticket 文件"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # 修正各個區塊
        content = fix_requirements_section(content)
        content = fix_acceptance_criteria_section(content)
        content = fix_related_documents_section(content)
        
        # 如果內容有變更，寫回文件
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"  ❌ 處理失敗 {file_path.name}: {e}")
        return False


def main():
    print("📋 開始修正所有英文版本的 Ticket 文件...\n")
    
    # 找出所有英文版本的 Ticket 文件
    english_ticket_files = list(TICKETS_DIR.rglob("*_en.md"))
    
    if not english_ticket_files:
        print("❌ 沒有找到英文版本的 Ticket 文件")
        return
    
    print(f"找到 {len(english_ticket_files)} 個英文版本的 Ticket 文件\n")
    
    fixed_count = 0
    unchanged_count = 0
    failed_count = 0
    
    for ticket_path in sorted(english_ticket_files):
        print(f"處理 {ticket_path.relative_to(TICKETS_DIR)}...")
        
        if fix_english_ticket(ticket_path):
            print(f"  ✅ 已修正")
            fixed_count += 1
        else:
            print(f"  ℹ️  無需修正")
            unchanged_count += 1
    
    print()
    print("="*70)
    print("✅ 修正完成！")
    print("="*70)
    print(f"   已修正：{fixed_count} 個")
    print(f"   無需修正：{unchanged_count} 個")
    print(f"   失敗：{failed_count} 個")
    print("="*70)


if __name__ == "__main__":
    main()

