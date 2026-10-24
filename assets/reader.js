(() => {
  if (!document.body.classList.contains('reading')) return;
  const root = document.documentElement;
  const theme = document.querySelector('#theme');
  let fontSize = 20;
  // Reading remains available when browser storage is blocked.
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch {} };
  let night = false;
  try {
    const stored = Number(localStorage.getItem('novels-font'));
    if (stored >= 18 && stored <= 28) fontSize = stored;
    night = localStorage.getItem('novels-night') === 'true';
  } catch {}
  function render() {
    root.style.setProperty('--reading-size', `${fontSize}px`);
    document.body.classList.toggle('night', night);
    theme.textContent = night ? '日間閱讀' : '夜間閱讀';
    theme.setAttribute('aria-pressed', String(night));
    document.querySelector('#smaller').disabled = fontSize <= 18;
    document.querySelector('#larger').disabled = fontSize >= 28;
  }
  document.querySelector('#smaller').addEventListener('click', () => { fontSize = Math.max(18, fontSize - 2); save('novels-font', fontSize); render(); update(); });
  document.querySelector('#larger').addEventListener('click', () => { fontSize = Math.min(28, fontSize + 2); save('novels-font', fontSize); render(); update(); });
  theme.addEventListener('click', () => { night = !night; save('novels-night', night); render(); });
  function update() {
    const distance = root.scrollHeight - innerHeight;
    document.querySelector('#progress').style.width = `${distance > 0 ? Math.min(100, Math.max(0, scrollY / distance * 100)) : 100}%`;
  }
  render(); update();
  addEventListener('scroll', update, { passive: true });
  addEventListener('resize', update);
})();
