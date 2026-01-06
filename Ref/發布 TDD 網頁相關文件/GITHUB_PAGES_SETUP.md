# GitHub Pages 設置詳細指南

## 📋 當前狀態檢查

### ✅ 已完成的步驟

1. **gh-pages branch 已創建並推送**
   - Branch 名稱: `gh-pages`
   - 最新 commit: `7c2f79e` (Deployed with MkDocs version: 1.6.1)
   - 狀態: ✅ 已推送到遠端

2. **Repository 資訊**
   - Repository: `HsinChungHan/LiveChatAndCommentOngoingFeature`
   - Remote URL: `git@github.com-personal:HsinChungHan/LiveChatAndCommentOngoingFeature.git`
   - Main branch: `main`
   - Pages branch: `gh-pages`

---

## 🔍 詳細檢查步驟

### 步驟 1: 訪問 GitHub Repository Settings

1. **打開瀏覽器，前往：**
   ```
   https://github.com/HsinChungHan/LiveChatAndCommentOngoingFeature
   ```

2. **點擊右上角的 "Settings" 按鈕**
   - 如果看不到 Settings，確認你有該 repository 的管理權限

### 步驟 2: 檢查 GitHub Pages 設置

1. **在左側選單中，向下滾動找到 "Pages"**
   - 位置：Settings > Pages（在左側選單的最下方）

2. **檢查 "Source" 設置**
   - 應該顯示：`Deploy from a branch`
   - Branch 應該選擇：`gh-pages`
   - Folder 應該選擇：`/ (root)`

3. **檢查部署狀態**
   - 如果設置正確，你會看到：
     - ✅ 綠色勾號或 "Your site is live at..."
     - URL: `https://hsinchunghan.github.io/LiveChatAndCommentOngoingFeature/`

### 步驟 3: 驗證網站內容

1. **檢查 gh-pages branch 內容**
   - 前往：`https://github.com/HsinChungHan/LiveChatAndCommentOngoingFeature/tree/gh-pages`
   - 應該看到 `index.html` 和 `assets/` 等文件夾

2. **訪問網站**
   - URL: `https://hsinchunghan.github.io/LiveChatAndCommentOngoingFeature/`
   - 如果顯示 404，可能需要等待幾分鐘讓 GitHub 完成部署

---

## ⚙️ 如何設置 GitHub Pages（如果尚未設置）

### 方法 1: 通過 GitHub Web UI

1. 前往 `https://github.com/HsinChungHan/LiveChatAndCommentOngoingFeature/settings/pages`

2. 在 "Source" 部分：
   - 選擇 "Deploy from a branch"
   - Branch: 選擇 `gh-pages`
   - Folder: 選擇 `/ (root)`

3. 點擊 "Save" 按鈕

4. 等待 1-2 分鐘，GitHub 會自動部署

### 方法 2: 通過 GitHub CLI（如果已安裝）

```bash
gh api repos/HsinChungHan/LiveChatAndCommentOngoingFeature/pages \
  -X POST \
  -f source[type]=branch \
  -f source[branch]=gh-pages \
  -f source[path]=/
```

---

## 🔧 常見問題排查

### 問題 1: 看不到 "Pages" 選項

**可能原因：**
- Repository 是私有的（GitHub Pages 需要公開 repository 或 GitHub Pro）
- 沒有管理權限

**解決方案：**
- 將 repository 設為公開，或
- 升級到 GitHub Pro/Team 以使用私有 repository 的 Pages

### 問題 2: 設置了但網站顯示 404

**可能原因：**
- GitHub 還在部署中（通常需要 1-5 分鐘）
- gh-pages branch 沒有正確的內容
- URL 路徑錯誤

**解決方案：**
1. 等待 5-10 分鐘後再試
2. 檢查 gh-pages branch 是否有 `index.html`
3. 確認 URL 格式正確：
   ```
   https://[username].github.io/[repository-name]/
   ```
   注意：repository 名稱大小寫敏感

### 問題 3: 網站內容不是最新的

**解決方案：**
```bash
cd /Users/reedhsin/Documents/codebase/fcom-iOS/TDDs/LiveChat\&PrematchComment
python3 -m mkdocs gh-deploy
```

這會重新建置並推送最新內容到 gh-pages branch。

---

## 📊 檢查命令（本地執行）

### 檢查 gh-pages branch 狀態

```bash
cd /Users/reedhsin/Documents/codebase/fcom-iOS/TDDs

# 查看所有 branches
git branch -a

# 查看 gh-pages branch 的內容
git ls-tree -r --name-only origin/gh-pages | head -20

# 查看 gh-pages branch 的最新 commit
git log origin/gh-pages --oneline -1

# 檢查是否有 index.html
git show origin/gh-pages:index.html | head -20
```

### 檢查遠端 branch 狀態

```bash
# 列出所有遠端 branches
git ls-remote --heads origin

# 查看 remote 詳細資訊
git remote show origin
```

---

## 🌐 預期的網站 URL

根據你的 repository 設置，網站應該在以下 URL 可用：

**主要 URL:**
```
https://hsinchunghan.github.io/LiveChatAndCommentOngoingFeature/
```

**備用 URL（如果使用自定義域名）:**
```
https://livechatandcommentongoingfeature.pages.dev/
```

---

## 📝 驗證清單

- [ ] Repository 是公開的（或你有 GitHub Pro）
- [ ] gh-pages branch 已推送到 GitHub
- [ ] Settings > Pages 中 Source 設置為 `gh-pages` branch
- [ ] 等待 5-10 分鐘讓 GitHub 完成部署
- [ ] 訪問網站 URL 確認內容正確顯示
- [ ] 檢查網站是否包含所有 TDD 文檔章節

---

## 🔄 更新文檔流程

每次更新文檔後，執行：

```bash
cd /Users/reedhsin/Documents/codebase/fcom-iOS/TDDs/LiveChat\&PrematchComment
python3 -m mkdocs gh-deploy
```

這會：
1. 建置最新的 MkDocs 文檔
2. 推送到 gh-pages branch
3. 自動觸發 GitHub Pages 重新部署

---

## 📞 需要幫助？

如果遇到問題，可以：
1. 檢查 GitHub Actions（如果有設置）查看部署日誌
2. 查看 repository 的 Settings > Pages 中的錯誤訊息
3. 確認 gh-pages branch 的內容是否正確

