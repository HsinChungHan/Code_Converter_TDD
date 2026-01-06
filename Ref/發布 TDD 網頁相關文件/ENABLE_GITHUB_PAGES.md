# 啟用 GitHub Pages 步驟指南

## 📋 當前狀況

根據你的 GitHub Pages 設置頁面，repository 目前是**私有的**，需要先設為公開才能啟用 GitHub Pages。

## 🎯 解決方案

### 方案 1：將 Repository 設為公開（推薦，免費）

1. **前往 General Settings**
   - 在左側選單中，點擊 **"General"**（在 "Code and automation" 上方）
   - 或直接訪問：
     ```
     https://github.com/HsinChungHan/LiveChatAndCommentOngoingFeature/settings
     ```

2. **找到 "Danger Zone" 區塊**
   - 向下滾動到頁面最底部
   - 找到 **"Danger Zone"** 區塊（通常是紅色邊框）

3. **更改 Visibility**
   - 在 "Danger Zone" 中，找到 **"Change repository visibility"**
   - 點擊 **"Change visibility"** 按鈕
   - 選擇 **"Make public"**
   - 確認操作（需要輸入 repository 名稱確認）

4. **返回 Pages 設置**
   - 回到 Settings > Pages
   - 現在應該可以看到 "Source" 選項了
   - 選擇 `gh-pages` branch 和 `/ (root)` folder
   - 點擊 **"Save"**

### 方案 2：升級到 GitHub Enterprise（付費）

如果你需要保持 repository 私有，可以：
- 點擊 **"Upgrade"** 按鈕
- 或點擊 **"Start free for 30 days"** 試用 GitHub Enterprise

## 📝 詳細步驟（方案 1）

### 步驟 1: 前往 General Settings

在當前頁面（Settings > Pages）：
- 點擊左側選單最上方的 **"General"**

### 步驟 2: 找到 Danger Zone

- 向下滾動到頁面最底部
- 找到 **"Danger Zone"** 區塊（紅色邊框）

### 步驟 3: 更改為公開

在 "Danger Zone" 中：
- 找到 **"Change repository visibility"**
- 點擊右側的 **"Change visibility"** 按鈕
- 在彈出視窗中：
  - 選擇 **"Make public"**
  - 輸入 repository 名稱 `HsinChungHan/LiveChatAndCommentOngoingFeature` 確認
  - 點擊 **"I understand, change repository visibility"**

### 步驟 4: 返回設置 GitHub Pages

1. 點擊左側選單的 **"Pages"**
2. 在 "Source" 部分：
   - 選擇 **"Deploy from a branch"**
   - Branch: 選擇 **`gh-pages`**
   - Folder: 選擇 **`/ (root)`**
3. 點擊 **"Save"** 按鈕

### 步驟 5: 等待部署

- 等待 1-5 分鐘
- 頁面會顯示：**"Your site is live at https://hsinchunghan.github.io/LiveChatAndCommentOngoingFeature/"**

## ⚠️ 注意事項

### 將 Repository 設為公開的影響

1. **任何人都可以看到你的代碼**
   - 包括所有 commits、branches、issues 等
   - 如果包含敏感資訊，請先檢查

2. **TDD 文檔通常是公開的**
   - 技術設計文檔通常適合公開分享
   - 這有助於團隊協作和知識分享

3. **如果擔心敏感資訊**
   - 檢查是否有 API keys、密碼等
   - 檢查是否有內部業務邏輯細節
   - 考慮使用 `.gitignore` 排除敏感文件

## 🔄 快速操作流程

```
Settings > Pages (當前頁面)
  ↓
點擊左側 "General"
  ↓
滾動到底部 "Danger Zone"
  ↓
點擊 "Change visibility" → "Make public"
  ↓
返回 "Pages" 設置
  ↓
選擇 gh-pages branch → Save
  ↓
完成！
```

## ✅ 完成後的驗證

設置完成後，訪問：
```
https://hsinchunghan.github.io/LiveChatAndCommentOngoingFeature/
```

應該可以看到你的 TDD 文檔網站了！

