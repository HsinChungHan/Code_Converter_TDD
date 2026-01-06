# Jira Integration

本目錄包含所有與 Jira 整合相關的腳本、資料庫和文檔。

## 目錄結構

```
jira_integration/
├── scripts/              # Jira 整合腳本
├── jira_tickets.db       # 本地 SQLite 資料庫
├── .env                  # 環境變數配置（需自行創建）
├── .gitignore            # Git 忽略規則
├── JIRA_INTEGRATION.md   # Jira 整合完整指南
├── JIRA_SETUP_GUIDE.md   # Jira 設定快速指南
├── TROUBLESHOOTING.md    # 疑難排解指南
└── README.md             # 本文件
```

## 快速開始

### 1. 設定環境變數

創建 `.env` 文件並填入以下資訊：

```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=YOUR-PROJECT-KEY
PARENT_ISSUE_KEY=YOUR-PARENT-ISSUE-KEY
ASSIGNEE_EMAIL=assignee@example.com
REPORTER_EMAIL=reporter@example.com
```

### 2. 初始化資料庫

```bash
cd jira_integration
python3 scripts/init_database.py
```

### 3. 載入本地 Ticket 文件

```bash
python3 scripts/load_tickets_to_db.py
```

### 4. 同步到 Jira

```bash
python3 scripts/sync_tickets_to_jira.py
```

## 主要功能

### 資料庫管理
- `init_database.py` - 初始化資料庫結構
- `load_tickets_to_db.py` - 載入本地 Ticket 文件到資料庫
- `query_database.py` - 查詢資料庫中的 Ticket 資訊

### Jira 同步
- `sync_tickets_to_jira.py` - 將本地 Tickets 同步到 Jira
- `sync_from_jira.py` - 從 Jira 同步 Issue 資訊到本地資料庫
- `sync_english_to_jira.py` - 將英文版本同步到 Jira

### Ticket 管理
- `consolidate_tickets.py` - 收斂 Tickets 並建立 Main Tasks
- `create_subtasks.py` - 為 Main Tasks 建立 Sub Tasks
- `assign_unassigned_tickets.py` - 指派未指派的 Tickets
- `assign_subtasks.py` - 指派未指派的 Sub Tasks

### 翻譯與更新
- `translate_and_update_tickets.py` - 翻譯並更新 Jira Tickets
- `create_bilingual_tickets.py` - 創建中英雙語版本的 Tickets
- `create_english_versions.py` - 創建獨立的英文版本
- `update_db_with_english_tickets.py` - 更新資料庫中的英文內容
- `fix_english_tickets.py` - 修正英文版本 Tickets 的格式

### 清理與維護
- `cleanup_duplicate_issues.py` - 清理重複的 Issues
- `close_redundant_issues.py` - 關閉多餘的原始 Issues
- `remove_main_task_links.py` - 移除 Main Tasks 的連結關係

### 查詢與檢查
- `list_all_story_issues.py` - 列出 Story 下的所有 Issues
- `list_uncompleted_tickets.py` - 列出未完成的 Tickets
- `check_story_status.py` - 檢查 Story 狀態
- `test_jira_connection.py` - 測試 Jira 連線

## 詳細文檔

- [JIRA_INTEGRATION.md](./JIRA_INTEGRATION.md) - 完整的整合指南
- [JIRA_SETUP_GUIDE.md](./JIRA_SETUP_GUIDE.md) - 快速設定指南
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 疑難排解
- [scripts/README_DATABASE.md](./scripts/README_DATABASE.md) - 資料庫使用指南

## 注意事項

1. **環境變數**：請確保 `.env` 文件已正確設定，且不要提交到 Git
2. **資料庫備份**：建議定期備份 `jira_tickets.db` 文件
3. **API 權限**：確保 Jira API Token 有足夠的權限（建立、更新、查詢 Issues）
4. **測試連線**：首次使用前，建議執行 `test_jira_connection.py` 測試連線

## 依賴套件

```bash
pip install requests python-dotenv
```

---

**最後更新**：2024-11-21


