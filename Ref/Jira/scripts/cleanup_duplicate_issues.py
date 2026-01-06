#!/usr/bin/env python3
"""
清理 Story FOOTBALL-8686 下的重複 Issues

識別並刪除/關閉重複的 Issues，只保留正確的版本。

使用方式：
python scripts/cleanup_duplicate_issues.py [--dry-run] [--force] [--close-only]
"""

import requests
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Set
from collections import defaultdict

# 載入環境變數
load_dotenv()

# Jira 設定
JIRA_URL = os.getenv("JIRA_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

PARENT_KEY = "FOOTBALL-8686"

# 應該保留的 Issue Keys
KEEP_MAIN_TASKS = {
    "FOOTBALL-9052",  # Domain Model Layer
    "FOOTBALL-9053",  # API Layer
    "FOOTBALL-9054",  # Client Layer
    "FOOTBALL-9055",  # Repository Layer
    "FOOTBALL-9056",  # UseCase Layer
    "FOOTBALL-9057",  # Feature Layer
    "FOOTBALL-9058",  # View Layer
}

# 應該保留的 Sub Tasks（FOOTBALL-9059 到 FOOTBALL-9084）
KEEP_SUB_TASKS = {f"FOOTBALL-{i}" for i in range(9059, 9085)}

# 應該保留的已關閉原始 Issues（FOOTBALL-9005 到 FOOTBALL-9030）
KEEP_CLOSED_ORIGINAL = {f"FOOTBALL-{i}" for i in range(9005, 9031)}

# 所有應該保留的 Issues
KEEP_ALL = KEEP_MAIN_TASKS | KEEP_SUB_TASKS | KEEP_CLOSED_ORIGINAL


def get_all_child_issues(parent_key: str) -> List[Dict]:
    """取得所有子 Issues"""
    url = f"{JIRA_URL}/rest/api/3/search/jql"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    jql = f'parent = {parent_key} ORDER BY created ASC'
    payload = {
        "jql": jql,
        "maxResults": 1000
    }
    
    all_issue_ids = []
    next_page_token = None
    
    try:
        # 處理分頁
        while True:
            if next_page_token:
                payload["pageToken"] = next_page_token
            
            response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            issue_ids = [issue["id"] for issue in data.get("issues", [])]
            all_issue_ids.extend(issue_ids)
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token or data.get("isLast", False):
                break
        
        if not all_issue_ids:
            return []
        
        # 取得詳細資訊
        detailed_issues = []
        for issue_id in all_issue_ids:
            detail_url = f"{JIRA_URL}/rest/api/3/issue/{issue_id}"
            detail_response = requests.get(
                detail_url,
                headers={"Accept": "application/json"},
                auth=auth,
                timeout=30
            )
            if detail_response.status_code == 200:
                detailed_issues.append(detail_response.json())
        
        return detailed_issues
    except requests.exceptions.RequestException as e:
        print(f"❌ 查詢失敗：{e}")
        return []


def delete_issue(jira_key: str) -> tuple[bool, str]:
    """刪除 Issue
    
    Returns:
        (success, message): (是否成功, 訊息)
    """
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}?deleteSubtasks=false"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.delete(url, headers=headers, auth=auth, timeout=30)
        if response.status_code == 403:
            return False, "無權限刪除"
        response.raise_for_status()
        return True, "已刪除"
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response:
            if e.response.status_code == 403:
                return False, "無權限刪除"
        return False, str(e)


def close_issue(jira_key: str) -> bool:
    """關閉 Issue（使用狀態轉換）"""
    # 取得可用的 transitions
    url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}/transitions"
    headers = {"Accept": "application/json"}
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        data = response.json()
        transitions = data.get("transitions", [])
        
        # 尋找「完成」或「取消」的 transition
        transition_id = None
        for transition in transitions:
            to_status = transition.get("to", {}).get("name", "")
            if to_status in ["完成", "Done", "取消", "Cancel"]:
                transition_id = transition.get("id")
                break
        
        if not transition_id:
            return False
        
        # 執行狀態轉換
        url = f"{JIRA_URL}/rest/api/3/issue/{jira_key}/transitions"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {"transition": {"id": transition_id}}
        
        response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def cleanup_duplicates(dry_run: bool = False, force: bool = False, close_only: bool = False):
    """清理重複的 Issues"""
    print("📋 開始清理重複的 Issues...\n")
    
    if not dry_run and not force:
        try:
            confirm = input("⚠️  確定要清理重複的 Issues 嗎？此操作不可逆！(yes/no): ")
            if confirm.lower() != "yes":
                print("❌ 操作已取消")
                return
        except EOFError:
            print("❌ 無法讀取輸入，請使用 --force 參數跳過確認")
            return
    
    # 取得所有子 Issues
    print(f"正在查詢 Story {PARENT_KEY} 下的所有 Issues...")
    issues = get_all_child_issues(PARENT_KEY)
    
    if not issues:
        print("❌ 沒有找到任何 Issues")
        return
    
    print(f"✅ 找到 {len(issues)} 個 Issues\n")
    
    # 識別需要刪除的 Issues
    to_delete = []
    to_keep = []
    
    for issue in issues:
        key = issue.get("key")
        summary = issue.get("fields", {}).get("summary", "")
        status = issue.get("fields", {}).get("status", {}).get("name", "")
        
        if key in KEEP_ALL:
            to_keep.append((key, summary, status))
        else:
            # 如果是已關閉的，也保留
            if status == "完成":
                to_keep.append((key, summary, status))
            else:
                to_delete.append((key, summary, status))
    
    print("="*70)
    print("📊 分析結果")
    print("="*70)
    print(f"\n✅ 保留的 Issues：{len(to_keep)} 個")
    print(f"🗑️  需要清理的 Issues：{len(to_delete)} 個\n")
    
    if to_delete:
        print("需要清理的 Issues（前 20 個）：")
        for i, (key, summary, status) in enumerate(to_delete[:20], 1):
            print(f"  {i:3d}. {key} - {summary[:50]}... ({status})")
        if len(to_delete) > 20:
            print(f"  ... 還有 {len(to_delete) - 20} 個")
        print()
    
    if dry_run:
        print("="*70)
        print("🔍 DRY RUN 模式 - 不會實際執行操作")
        print("="*70)
        return
    
    # 執行清理
    print("="*70)
    print("🗑️  開始清理...")
    print("="*70)
    print()
    
    deleted_count = 0
    closed_count = 0
    failed_count = 0
    
    for key, summary, status in to_delete:
        if close_only:
            # 只關閉，不刪除
            if dry_run:
                print(f"  [DRY RUN] 將關閉：{key} - {summary[:50]}...")
                closed_count += 1
            else:
                if close_issue(key):
                    print(f"  ✅ 已關閉：{key} - {summary[:50]}...")
                    closed_count += 1
                else:
                    print(f"  ❌ 關閉失敗：{key}")
                    failed_count += 1
        else:
            # 嘗試刪除
            success, message = delete_issue(key)
            if success:
                print(f"  ✅ 已刪除：{key} - {summary[:50]}...")
                deleted_count += 1
            else:
                # 刪除失敗（無權限），嘗試關閉
                if "無權限" in message:
                    print(f"  ⚠️  無法刪除 {key}（無權限），嘗試關閉...")
                    if close_issue(key):
                        print(f"  ✅ 已關閉：{key} - {summary[:50]}...")
                        closed_count += 1
                    else:
                        print(f"  ❌ 關閉失敗：{key}")
                        failed_count += 1
                else:
                    print(f"  ❌ 刪除失敗：{key} - {message}")
                    failed_count += 1
    
    print()
    print("="*70)
    print("✅ 清理完成！")
    print("="*70)
    print(f"   成功刪除：{deleted_count} 個")
    print(f"   成功關閉：{closed_count} 個")
    print(f"   失敗：{failed_count} 個")
    print(f"   保留：{len(to_keep)} 個")
    print("="*70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="清理 Story FOOTBALL-8686 下的重複 Issues")
    parser.add_argument("--dry-run", action="store_true", help="Dry run 模式（不會實際執行）")
    parser.add_argument("--force", action="store_true", help="強制執行，跳過確認")
    parser.add_argument("--close-only", action="store_true", help="只關閉，不刪除（用於無刪除權限的情況）")
    args = parser.parse_args()
    
    cleanup_duplicates(dry_run=args.dry_run, force=args.force, close_only=args.close_only)

