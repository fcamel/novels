const $ = id => document.getElementById(id);
let report, showingOriginal = true, syncing = false;
const bytes = n => n >= 1e6 ? `${(n / 1e6).toFixed(2)} MB` : `${(n / 1e3).toFixed(0)} KB`;
function render() {
  const row = report.pages[Number($('page').value)];
  const quality = $('quality').value;
  const variant = row.variants[quality];
  const toggleMode = $('mode').value === 'toggle';
  $('views').classList.toggle('single', toggleMode);
  $('compressed-panel').hidden = toggleMode;
  $('toggle').hidden = !toggleMode;
  $('original').src = toggleMode && !showingOriginal ? variant.src : row.original;
  $('compressed').src = variant.src;
  $('original-panel').querySelector('h2').textContent = toggleMode && !showingOriginal ? `WebP ${quality}` : '原圖';
  $('compressed-title').textContent = `WebP ${quality}`;
  $('toggle').textContent = `目前：${showingOriginal ? '原圖' : `WebP ${quality}`}（點擊切換）`;
  for (const id of ['original', 'compressed']) {
    $(id).style.width = $('zoom').value === 'fit' ? '100%' : `${row.width * Number($('zoom').value)}px`;
    $(id).width = row.width; $(id).height = row.height; $(id).style.height = 'auto';
  }
  const originalTotal = report.pages.reduce((sum, r) => sum + r.bytes, 0);
  const compressedTotal = report.pages.reduce((sum, r) => sum + r.variants[quality].bytes, 0);
  $('stats').textContent = `本頁 ${row.width} × ${row.height}：${bytes(row.bytes)} → ${bytes(variant.bytes)}（減少 ${(100 * (1 - variant.bytes / row.bytes)).toFixed(1)}%）｜全篇：${bytes(originalTotal)} → ${bytes(compressedTotal)}`;
}
for (const [from, to] of [['left','right'], ['right','left']]) $(from).addEventListener('scroll', () => {
  if (syncing) return;
  syncing = true; $(to).scrollTop = $(from).scrollTop; $(to).scrollLeft = $(from).scrollLeft;
  requestAnimationFrame(() => { syncing = false; });
}, { passive: true });
for (const id of ['page','quality','zoom','mode']) $(id).addEventListener('change', render);
$('toggle').addEventListener('click', () => { showingOriginal = !showingOriginal; render(); });
fetch('report.json').then(r => { if (!r.ok) throw Error('無法讀取比較資料'); return r.json(); }).then(data => {
  report = data;
  data.pages.forEach((row, i) => { const option = document.createElement('option'); option.value = i; option.textContent = `${i + 1}. ${row.name}`; $('page').append(option); });
  render();
}).catch(e => { $('stats').textContent = `${e.message}。請用本機 HTTP 伺服器開啟比較頁。`; });
