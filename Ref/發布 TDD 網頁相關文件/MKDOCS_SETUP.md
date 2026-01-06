# MkDocs 設定說明

## 已建立的檔案

1. `output/LiveChat&PrematchComment/mkdocs.yml` - MkDocs 主配置檔案
2. `requirements.txt` - Python 依賴套件
3. `.github/workflows/deploy.yml` - GitHub Actions 自動部署配置
4. `.gitignore` - 已更新，包含 MkDocs 生成的檔案

## 安裝步驟

### 1. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

### 2. 本地預覽

```bash
cd "output/LiveChat&PrematchComment"
mkdocs serve
```

然後在瀏覽器中開啟 `http://127.0.0.1:8000` 即可預覽。

### 3. 建置網站

```bash
cd "output/LiveChat&PrematchComment"
mkdocs build
```

生成的網站會在 `site/` 目錄下。

## 部署到 GitHub Pages

### 方法 1：使用 GitHub Actions（推薦）

1. 將所有檔案推送到 GitHub repository
2. 在 GitHub repository 設定中：
   - 前往 Settings → Pages
   - Source 選擇 "GitHub Actions"
3. 每次 push 到 `main` 分支時會自動部署

### 方法 2：手動部署

```bash
cd "output/LiveChat&PrematchComment"
mkdocs gh-deploy
```

## Mermaid 支援

MkDocs 已配置支援 Mermaid 語法，所有 ````mermaid` 區塊會自動渲染為圖表。

## 功能特色

- ✅ 支援 Mermaid 序列圖和流程圖
- ✅ 自動生成導航側邊欄
- ✅ 支援搜尋功能
- ✅ 深色/淺色主題切換
- ✅ 響應式設計，支援手機瀏覽
- ✅ 程式碼區塊複製功能

## 注意事項

- `mkdocs.yml` 必須放在 `output/LiveChat&PrematchComment/` 目錄下
- 所有 Markdown 檔案的路徑都是相對於 `output/LiveChat&PrematchComment/` 目錄
- 如果新增或刪除檔案，需要更新 `mkdocs.yml` 中的 `nav` 配置

