# 飛駝作品集

原創小說與漫畫閱讀網站，以 GitHub Pages 發佈。

- 網址：https://fcamel.github.io/novels/
- 純靜態 HTML、CSS、JavaScript；建置需要 Python 3.10 以上與 Pillow（見 requirements.txt）。
- 網頁全文在建置時產生；即使關閉 JavaScript 也可以閱讀。
- 閱讀頁提供字體調整、日／夜間模式與進度條；字體與主題偏好儲存在讀者的瀏覽器。

## 本機預覽

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

開啟 http://localhost:8000/ 。請勿直接編輯 `dist/`，它是建置產物，不加入版本控制。

## 新增小說

1. 將 UTF-8 純文字正文放入 `content/novels/`，例如 `content/novels/second-story.txt`。
   單一換行保留為文章中的換行；空白行分隔段落。
2. 將封面放入 `covers/`，例如 `covers/second-story.webp`。
3. 在 `content/books.json` 陣列加入一筆：

```json
{
  "slug": "second-story",
  "title": "第二本小說",
  "subtitle": "一句題辭。",
  "description": "書架顯示的簡介。",
  "genre": "奇幻",
  "cover": "second-story.webp",
  "text": "second-story.txt"
}
```

`slug` 必須唯一，且只包含小寫英文字、數字和連字號；它是作品的固定網址。陣列順序就是書架順序。閱讀時間由正文長度估算。若要將指定段落加粗，可加入選填的 `bold_paragraphs` 陣列，每個字串須與正文該段完全相同（換行使用 `\n`）。

4. 執行 `python3 scripts/build.py` 並預覽。
5. 提交並推送至 `main`，GitHub Actions 將自動建置及發佈。

```sh
git add content covers comics assets scripts templates docs
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

## 漫畫與製作資料

網站整合小說及漫畫，作品資料在 `content/books.json`，選填 `comic` 使用專案根目錄相對路徑，指向 `comics/<slug>/comic.json` 漫畫清單。清單的 `source_directory` 指定正式圖稿目錄，`pages` 陣列明確指定頁序（支援 PNG、WebP 混用）。讀者頁碼從 1 起算，不依製作檔名判斷。

- `comics/huashan-lun-ye/`：正式圖稿、角色設定、可重用校稿規範。
- `local-production/`：歷次產物、比較圖與 PNG 備存；已 gitignore，不提交、不部署。
- `tools/image-compare/`：可重用的本機圖片比較介面。
- `scripts/build_comics.py`：PNG 以 WebP quality 80、method 6 轉檔；**WebP 正文原樣複製，不再次壓縮**。縮圖另行產生。
- `assets/comic-reader.*`：單頁／連續閱讀、頁面一覽、進度記憶及後續 3 頁低優先序預載。手機首次預設適合寬度。

建置只複製白名單上的網站資產，角色圖、校稿文件、PNG 正文母檔不會發佈。舊 `comics` 專案不受影響。

### 比較原圖與壓縮圖

```sh
python3 -m pip install -r requirements.txt
python3 scripts/compare_images.py comics/huashan-lun-ye/comic.json
python3 -m http.server 8001 --bind 127.0.0.1 --directory local-production/image-compare
```

開啟 http://127.0.0.1:8001/huashan-lun-ye/ 。可選頁、切換品質 70／80、並排同步捲動、同位置切換、100%／200% 或適合視窗。頁面顯示每頁及全篇大小。此步驟**不改動正式原稿**。

肉眼確認後才執行（選擇 80 或 70）：

```sh
python3 scripts/compare_images.py comics/huashan-lun-ye/comic.json --adopt 80
python3 scripts/build.py
```

採用工具核對比較時的頁序和來源／候選圖雜湊，先將 PNG 備份到 `local-production/originals/`，驗證備份，再以已比較的 WebP 替換正式來源並更新清單。已是 WebP 的來源略過，不再次壓縮。若原稿或清單已變動，必須重新產生比較。工具不自動 commit 或 push。

原圖一旦提交進 Git，之後刪除仍留在歷史中；因此本次先比較，再決定哪些格式加入 Git。本機備存不等於遠端備份，重要原稿請自行另備份。

《華山論葉》已採用比較後的 WebP 80，正文與角色圖的 PNG 原稿僅在 `local-production/originals/` 本機備存。正式來源依閱讀順序統一命名為 `001.webp`、`002.webp`……；網站正文輸出為 `pages/001.webp`、`002.webp`……，縮圖為 `thumbnails/001.webp`、`002.webp`……，順序依發佈清單。


## 目錄結構與新增漫畫

```text
content/books.json                 作品書架資料
content/novels/<slug>.txt           小說正文
covers/<slug>.webp                 作品封面
comics/<slug>/comic.json           漫畫頁序與來源設定
comics/<slug>/pages/               最終採用圖檔
comics/<slug>/characters/          角色設定
comics/<slug>/consistency-review.md 校稿規範
assets/                           共用網站程式、樣式及圖示
local-production/                 本機備存（不提交）
```

`books.json` 的 `text` 相對於 `content/novels/`，`cover` 相對於 `covers/`；`comic` 相對於專案根目錄。只有小說的作品省略 `comic` 即可。

新增漫畫時，在作品資料填入 `"comic": "comics/second-story/comic.json"`，再建立清單：

```json
{
  "source_directory": "comics/second-story/pages",
  "pages": ["opening.webp", "encounter.webp"]
}
```

`source_directory` 也是專案根目錄相對路徑，`pages` 各項相對於該目錄。每部作品獨立存放比較結果，避免同名 `comic.json` 互相覆寫。

建置後小說網址仍為 `books/<slug>/`、漫畫網址仍為 `comics/<slug>/`；封面集中輸出至 `covers/`。內部移動不更改作品閱讀網址。舊本機比較資料維持原位置，新比較請使用新清單重新產生。
