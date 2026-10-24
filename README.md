# fcamel 小說集

原創小說書架與全文閱讀網站，以 GitHub Pages 發佈。

- 網址：https://fcamel.github.io/novels/
- 純靜態 HTML、CSS、JavaScript；建置只需要 Python 3.9 以上，無第三方相依套件。
- 網頁全文在建置時產生；即使關閉 JavaScript 也可以閱讀。
- 閱讀頁提供字體調整、日／夜間模式與進度條；字體與主題偏好儲存在讀者的瀏覽器。

## 本機預覽

```sh
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

開啟 http://localhost:8000/ 。請勿直接編輯 `dist/`，它是建置產物，不加入版本控制。

## 新增小說

1. 將 UTF-8 純文字正文放入 `content/`，例如 `content/second-story.txt`。
   單一換行保留為文章中的換行；空白行分隔段落。
2. 將封面放入 `assets/`，例如 `assets/second-cover.png`。
3. 在 `content/books.json` 陣列加入一筆：

```json
{
  "slug": "second-story",
  "title": "第二本小說",
  "subtitle": "一句題辭。",
  "description": "書架顯示的簡介。",
  "genre": "奇幻",
  "cover": "second-cover.png",
  "text": "second-story.txt"
}
```

`slug` 必須唯一，且只包含小寫英文字、數字和連字號；它是作品的固定網址。陣列順序就是書架順序，第一本會成為首頁主打。閱讀時間由正文長度估算。

4. 執行 `python3 scripts/build.py` 並預覽。
5. 提交並推送至 `main`，GitHub Actions 將自動建置及發佈。

```sh
git add content assets
git commit -m "Add a new story"
git push
```

## 發佈設定

GitHub 儲存庫的 **Settings → Pages → Source** 設為 **GitHub Actions**。
工作流程位於 `.github/workflows/pages.yml`；不需要 npm、Jekyll、網站後端或額外密鑰。
所有網站連結使用相對路徑，適用於 GitHub Pages 專案子目錄。

## 作品

- 《華山論葉》：封面及正文由作者提供，網站保留原有分段與措辭。

小說文字與封面之權利保留予原作者。未另行授權轉載。
