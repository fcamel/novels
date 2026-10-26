# 《華山論葉》漫畫製作框架

本目錄只保存目前定稿與可重用的製作規範，不保存每次生成的中間版本。

- `pages/`：目前 12 張已確認的 WebP 80 正式來源圖；依閱讀順序連續命名為 `001.webp`～`012.webp`，並以 `comic.json` 維護發佈順序。
- `characters/`：四人的角色設定圖及固定特徵。
- `consistency-review.md`：整體性校稿 prompt，可用於新增或修改頁面。
- `comic.json`：正式頁面順序，是網站的唯一排序來源。

修改流程：修改定稿 → 校稿確認 → 若有插刪頁，更新發佈清單 → 建置並本機預覽 → 提交部署。角色圖供外貌參照，最新作者指示優先於舊圖。作者已在 ChatGPT Work 手動更新的頁面，以目前 pages 內容為準。

網站頁碼為清單位置 1–12；原製作檔名保留，網站正文與縮圖各自輸出連續編號 `001.webp`、`002.webp`……`012.webp`。PNG 部署統一品質 80、method 6、不縮小正文頁面；WebP 正文直接複製，不再壓縮；縮圖上限 240 × 360，同樣品質 80。

歷次生成圖、分鏡、修改提示與舊目錄已集中移至專案根目錄 `local-production/huashan-lun-ye/`，由 `.gitignore` 排除，只作本機備存。原 `reading-order-v2` 位於該目錄內的 `huashan-storyboard/reading-order-v2/`。這不是雲端備份；正式更新請修改本目錄 pages，避免把本機備存誤當發佈來源。

部署以白名單產生網站：不公開角色設定、製作文件、本機備存或 PNG 母檔。

已採用品質 80：正文 PNG 原稿存於 `local-production/originals/huashan-lun-ye-comic/`，角色設定 PNG 存於 `local-production/originals/huashan-lun-ye-characters/`；正式目錄只保留 WebP，原製作檔名仍用於來源對照。
