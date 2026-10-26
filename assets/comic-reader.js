const COMIC = JSON.parse(document.getElementById('comic-config').textContent);
const TOTAL_PAGES = COMIC.pages.length;
const KEYS = Object.fromEntries(['page', 'mode', 'fit'].map(key => [key, `comic-${COMIC.slug}-${key}`]));
const $ = id => document.getElementById(id);
const image = $('comic-image');
const readingBar = document.querySelector('.reading-bar');
const singlePages = $('page-shell');
const continuousPages = $('continuous-pages');
const dialog = $('pages-dialog');
const grid = $('thumbnail-grid');
const pageSrc = page => COMIC.pages[page - 1].src;
const validPage = page => Number.isInteger(page) && page >= 1 && page <= TOTAL_PAGES;
const hashPage = () => { const match = location.hash.match(/^#p=(\d+)$/); return match ? Number(match[1]) : null; };
const load = key => { try { return localStorage.getItem(key); } catch { return null; } };
const save = (key, value) => { try { localStorage.setItem(key, String(value)); } catch { /* Storage may be unavailable. */ } };

const savedPage = Number(load(KEYS.page));
let currentPage = validPage(hashPage()) ? hashPage() : validPage(savedPage) ? savedPage : 1;
let readingMode = load(KEYS.mode) === 'single' ? 'single' : 'continuous';
let fitMode = ['default', 'width', 'height'].includes(load(KEYS.fit)) ? load(KEYS.fit) : matchMedia('(max-width: 600px)').matches ? 'width' : 'height';
let continuousBuilt = false;
let scrollFrame = 0;

const preloadWindow = new Map();
function preloadNextPages(page) {
  const wanted = new Set([page + 1, page + 2, page + 3].filter(validPage));
  for (const key of preloadWindow.keys()) {
    if (!wanted.has(key)) preloadWindow.delete(key);
  }
  for (const next of wanted) {
    if (preloadWindow.has(next)) continue;
    const upcoming = new Image();
    upcoming.fetchPriority = 'low';
    upcoming.decoding = 'async';
    upcoming.src = pageSrc(next);
    preloadWindow.set(next, upcoming);
  }
}

function updatePageStatus(page, updateHistory = true) {
  if (!validPage(page)) return;
  currentPage = page;
  preloadNextPages(page);
  $('page-number').textContent = String(page).padStart(2, '0');
  $('progress').setAttribute('aria-valuenow', String(page));
  $('progress-fill').style.width = `${page / TOTAL_PAGES * 100}%`;
  grid.querySelectorAll('.thumbnail').forEach(button => {
    if (Number(button.dataset.page) === page) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  });
  save(KEYS.page, page);
  if (updateHistory) history.replaceState(null, '', `#p=${page}`);
}

function renderSingle(page, scroll = true) {
  image.hidden = false;
  $('image-error').hidden = true;
  if (image.getAttribute('src') !== pageSrc(page)) image.src = pageSrc(page);
  image.alt = `《${COMIC.title}》第 ${page} 頁，共 ${TOTAL_PAGES} 頁`;
  if (scroll) window.scrollTo({ top: 0, behavior: 'instant' });
  image.width = COMIC.pages[page - 1].width;
  image.height = COMIC.pages[page - 1].height;
}

function buildContinuousPages() {
  if (continuousBuilt) return;
  const fragment = document.createDocumentFragment();
  for (let page = 1; page <= TOTAL_PAGES; page++) {
    const figure = document.createElement('figure');
    figure.className = 'comic-page continuous-page';
    figure.dataset.page = String(page);
    figure.innerHTML = `<span class="continuous-label">${String(page).padStart(2, '0')} / ${TOTAL_PAGES}</span><img src="${pageSrc(page)}" alt="《${COMIC.title}》第 ${page} 頁" width="${COMIC.pages[page - 1].width}" height="${COMIC.pages[page - 1].height}" loading="lazy" decoding="async"><div class="continuous-error" hidden><p>第 ${page} 頁暫時無法載入。</p><button class="retry-button" type="button">重新載入</button></div>`;
    const pageImage = figure.querySelector('img');
    const pageError = figure.querySelector('.continuous-error');
    pageImage.addEventListener('error', () => { pageImage.hidden = true; pageError.hidden = false; });
    pageImage.addEventListener('load', () => { pageImage.hidden = false; pageError.hidden = true; });
    pageError.querySelector('button').addEventListener('click', () => {
      pageImage.src = `${pageSrc(page)}?retry=${Date.now()}`;
      pageImage.hidden = false;
      pageError.hidden = true;
    });
    fragment.append(figure);
  }
  continuousPages.append(fragment);
  continuousBuilt = true;
}

function scrollToPage(page) {
  const target = continuousPages.children[page - 1];
  if (!target) return;
  const top = window.scrollY + target.getBoundingClientRect().top - readingBar.offsetHeight - 8;
  window.scrollTo({ top: Math.max(0, top), behavior: 'instant' });
}

function navigate(page, updateHistory = true) {
  if (!validPage(page)) return;
  updatePageStatus(page, updateHistory);
  updateReaderSize();
  if (readingMode === 'continuous') scrollToPage(page);
  else renderSingle(page);
}

function setReadingMode(mode, initial = false) {
  if (!['single', 'continuous'].includes(mode)) return;
  readingMode = mode;
  if (mode === 'continuous') buildContinuousPages();
  singlePages.hidden = mode !== 'single';
  continuousPages.hidden = mode !== 'continuous';
  $('reader-hint').textContent = mode === 'continuous' ? '向下捲動閱讀；也可使用 ← → 跳至前後頁' : '圖片左鍵下一頁、右鍵上一頁；亦可用 ← → 或左右滑動';
  document.querySelectorAll('[data-mode]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mode === mode)));
  save(KEYS.mode, mode);
  if (!initial) {
    if (mode === 'continuous') requestAnimationFrame(() => scrollToPage(currentPage));
    else renderSingle(currentPage);
  }
}

function setFitMode(fit, initial = false) {
  if (!['default', 'width', 'height'].includes(fit)) return;
  fitMode = fit;
  document.body.dataset.fit = fit;
  document.querySelectorAll('[data-fit]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.fit === fit)));
  save(KEYS.fit, fit);
  if (!initial && readingMode === 'continuous') requestAnimationFrame(() => scrollToPage(currentPage));
}

function trackContinuousPage() {
  scrollFrame = 0;
  if (readingMode !== 'continuous') return;
  const line = readingBar.getBoundingClientRect().bottom + Math.min((innerHeight - readingBar.offsetHeight) * .25, 180);
  let visiblePage = 1;
  for (const figure of continuousPages.children) {
    const rect = figure.getBoundingClientRect();
    if (rect.top <= line) visiblePage = Number(figure.dataset.page);
    if (rect.bottom > line) break;
  }
  if (visiblePage !== currentPage) updatePageStatus(visiblePage);
}

$('retry').addEventListener('click', () => { image.src = `${pageSrc(currentPage)}?retry=${Date.now()}`; image.hidden = false; $('image-error').hidden = true; });
image.addEventListener('error', () => { image.hidden = true; $('image-error').hidden = false; });
image.addEventListener('load', () => { image.hidden = false; $('image-error').hidden = true; });
let lastTouchTime = 0;
image.addEventListener('click', event => {
  if (readingMode !== 'single' || event.button !== 0 || Date.now() - lastTouchTime < 700) return;
  if ('pointerType' in event && event.pointerType && event.pointerType !== 'mouse') return;
  navigate(currentPage + 1);
});
image.addEventListener('contextmenu', event => {
  if (readingMode !== 'single') return;
  if ('pointerType' in event && event.pointerType && event.pointerType !== 'mouse') return;
  event.preventDefault();
  navigate(currentPage - 1);
});
document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => setReadingMode(button.dataset.mode)));
document.querySelectorAll('[data-fit]').forEach(button => button.addEventListener('click', () => setFitMode(button.dataset.fit)));
$('open-pages').addEventListener('click', () => dialog.showModal());
$('close-pages').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });

for (let page = 1; page <= TOTAL_PAGES; page++) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'thumbnail';
  button.dataset.page = String(page);
  button.setAttribute('aria-label', `跳到第 ${page} 頁`);
  button.innerHTML = `<img src="${COMIC.pages[page - 1].thumbnail}" alt="" loading="lazy" width="187" height="280"><span>第 ${String(page).padStart(2, '0')} 頁</span>`;
  button.addEventListener('click', () => { dialog.close(); navigate(page); });
  grid.append(button);
}

document.addEventListener('keydown', event => {
  if (dialog.open || event.altKey || event.ctrlKey || event.metaKey || ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
  if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
    event.preventDefault();
    navigate(currentPage + (event.key === 'ArrowRight' ? 1 : -1));
  }
});

let touchStart = null;
singlePages.addEventListener('touchstart', event => {
  touchStart = event.touches.length === 1 ? {
    x: event.touches[0].clientX,
    y: event.touches[0].clientY,
    time: Date.now(),
    onImage: event.target === image
  } : null;
}, { passive: true });
singlePages.addEventListener('touchend', event => {
  lastTouchTime = Date.now();
  if (!touchStart || event.changedTouches.length !== 1) { touchStart = null; return; }
  const dx = event.changedTouches[0].clientX - touchStart.x;
  const dy = event.changedTouches[0].clientY - touchStart.y;
  if (Math.abs(dx) > 65 && Math.abs(dx) > Math.abs(dy) * 1.5) navigate(currentPage + (dx < 0 ? 1 : -1));
  else if (touchStart.onImage && Math.abs(dx) < 12 && Math.abs(dy) < 12 && Date.now() - touchStart.time < 500) navigate(currentPage + 1);
  touchStart = null;
}, { passive: true });
singlePages.addEventListener('touchcancel', () => { touchStart = null; }, { passive: true });

window.addEventListener('scroll', () => {
  if (readingMode === 'continuous' && !scrollFrame) scrollFrame = requestAnimationFrame(trackContinuousPage);
}, { passive: true });
window.addEventListener('hashchange', () => {
  const page = hashPage();
  if (validPage(page) && page !== currentPage) navigate(page, false);
});

function updateReaderSize() {
  const barHeight = readingBar.offsetHeight;
  document.documentElement.style.setProperty('--reader-bar-height', `${barHeight}px`);
  const availableHeight = Math.max(240, innerHeight - barHeight - 24);
  document.documentElement.style.setProperty('--fit-height-width', `${Math.floor(availableHeight * COMIC.pages[currentPage - 1].width / COMIC.pages[currentPage - 1].height)}px`);
}
new ResizeObserver(updateReaderSize).observe(readingBar);
window.addEventListener('resize', updateReaderSize);
updateReaderSize();
setFitMode(fitMode, true);
setReadingMode(readingMode, true);
if (currentPage !== 1) $('first-page-preload').remove();
if (readingMode === 'single') renderSingle(currentPage, false);
updatePageStatus(currentPage, !validPage(hashPage()));
if (readingMode === 'continuous') requestAnimationFrame(() => scrollToPage(currentPage));
