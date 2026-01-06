# 本地資料庫使用指南

本目錄提供本地 SQLite 資料庫來儲存和查詢 Jira Ticket 資訊。

---

## 資料庫結構

### 資料表

1. **tickets**：本地 Ticket 資訊
   - `ticket_id`：Ticket ID（主鍵）
   - `title`：標題
   - `type`：類型（Domain Model, API, Client, Repository, UseCase, Feature, View）
   - `priority`：優先級（P0, P1, P2, P3）
   - `feature`：所屬 Feature
   - `story_point`：Story Point
   - `estimate_standard`：標準估時（天）
   - `estimate_strict`：最嚴厲估時（天）
   - `description`：描述
   - `requirements`：需求
   - `acceptance_criteria`：驗收條件
   - `related_documents`：相關文件

2. **jira_issues**：Jira Issue 資訊
   - `ticket_id`：對應的 Ticket ID（外鍵）
   - `jira_key`：Jira Issue Key（唯一）
   - `jira_id`：Jira Issue ID
   - `summary`：摘要
   - `status`：狀態
   - `assignee_account_id`：受託人 Account ID
   - `assignee_display_name`：受託人顯示名稱
   - `reporter_account_id`：回報者 Account ID
   - `reporter_display_name`：回報者顯示名稱
   - `priority`：優先級
   - `issue_type`：Issue 類型
   - `labels`：標籤
   - `parent_key`：父系 Issue Key
   - `original_estimate`：原始估時
   - `time_spent`：已花費時間
   - `time_remaining`：剩餘時間
   - `created_at`：建立時間
   - `updated_at`：更新時間
   - `resolved_at`：解決時間
   - `url`：Issue URL

3. **dependencies**：Ticket 依賴關係
   - `ticket_id`：Ticket ID（外鍵）
   - `depends_on_ticket_id`：依賴的 Ticket ID（外鍵）
   - `jira_key`：對應的 Jira Key
   - `depends_on_jira_key`：依賴的 Jira Key

4. **issue_links**：Jira Issue 連結關係
   - `source_jira_key`：來源 Issue Key
   - `target_jira_key`：目標 Issue Key
   - `link_type`：連結類型（例如：blocks）

5. **sync_history**：同步歷史記錄
   - `sync_type`：同步類型
   - `sync_time`：同步時間
   - `tickets_synced`：同步的 Ticket 數
   - `issues_created`：建立的 Issue 數
   - `issues_updated`：更新的 Issue 數
   - `links_created`：建立的連結數
   - `errors`：錯誤訊息
   - `status`：狀態（success/failed）

---

## 使用方式

### 1. 初始化資料庫

```bash
cd output/LiveChat&PrematchComment/12_Tickets
python3 scripts/init_database.py
```

這會建立 `jira_tickets.db` 資料庫檔案和所有必要的資料表。

### 2. 載入本地 Ticket 檔案

```bash
python3 scripts/load_tickets_to_db.py
```

這會掃描所有 `TDD-*.md` 檔案，解析內容並載入到 `tickets` 表。

### 3. 從 Jira 同步 Issue 資訊

```bash
python3 scripts/sync_from_jira.py
```

或指定父系 Issue Key：

```bash
python3 scripts/sync_from_jira.py --parent-key FOOTBALL-8686
```

這會：
- 從 Jira API 取得所有子 Issue
- 將 Issue 資訊同步到 `jira_issues` 表
- 同步 Issue 連結關係到 `issue_links` 表
- 記錄同步歷史到 `sync_history` 表

### 4. 查詢資料庫

#### 列出所有 Ticket

```bash
python3 scripts/query_database.py --list
```

#### 顯示統計資訊

```bash
python3 scripts/query_database.py --stats
```

#### 根據條件查詢

```bash
# 根據 Ticket ID 查詢
python3 scripts/query_database.py --ticket-id TDD-001

# 根據 Jira Key 查詢
python3 scripts/query_database.py --jira-key FOOTBALL-8979

# 根據狀態查詢
python3 scripts/query_database.py --status "待處理"

# 根據 Feature 查詢
python3 scripts/query_database.py --feature PrematchComment

# 根據類型查詢
python3 scripts/query_database.py --type Domain-Model
```

---

## 完整工作流程

### 初次設定

```bash
# 1. 初始化資料庫
python3 scripts/init_database.py

# 2. 載入本地 Ticket 檔案
python3 scripts/load_tickets_to_db.py

# 3. 從 Jira 同步 Issue 資訊
python3 scripts/sync_from_jira.py
```

### 定期同步

```bash
# 定期執行同步以更新 Jira Issue 狀態
python3 scripts/sync_from_jira.py
```

---

## 資料庫檔案位置

資料庫檔案位於：
```
output/LiveChat&PrematchComment/12_Tickets/jira_tickets.db
```

此檔案已加入 `.gitignore`，不會被提交到 Git。

---

## 注意事項

1. **環境變數**：`sync_from_jira.py` 需要 `.env` 檔案中的 Jira 設定
2. **Ticket 匹配**：同步時會根據 `title` 匹配本地 Ticket 和 Jira Issue
3. **依賴關係**：依賴關係會從本地 Ticket 檔案解析，Jira 連結關係會從 Jira API 取得
4. **資料庫備份**：建議定期備份 `jira_tickets.db` 檔案

---

## 範例查詢

### 查看所有未同步的 Ticket

```python
import sqlite3
from pathlib import Path

DB_PATH = Path("jira_tickets.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT ticket_id, title 
    FROM tickets 
    WHERE ticket_id NOT IN (SELECT ticket_id FROM jira_issues)
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")
```

### 查看所有已完成的 Ticket

```python
cursor.execute("""
    SELECT t.ticket_id, t.title, j.status, j.resolved_at
    FROM tickets t
    JOIN jira_issues j ON t.ticket_id = j.ticket_id
    WHERE j.status = '完成'
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} - {row[2]} ({row[3]})")
```

---

**最後更新**：2024-11-21

