"""Build a portable, novel and comic collection for GitHub Pages."""
import html
import json
import math
import re
import shutil
from pathlib import Path
from build_comics import build_comic

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dist'
books = json.loads((ROOT / 'content/books.json').read_text())
assert books, 'Add at least one book'
slugs = set()
for book in books:
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', book['slug']), 'Invalid slug'
    assert book['slug'] not in slugs, 'Duplicate slug'
    slugs.add(book['slug'])
    for key, folder in [('text', 'content/novels'), ('cover', 'covers')]:
        path = ROOT / folder / book[key]
        assert path.is_file() and path.resolve().is_relative_to((ROOT / folder).resolve()), f'Missing or invalid {key}'
    book['body'] = (ROOT / 'content/novels' / book['text']).read_text().strip()
    book['minutes'] = max(1, math.ceil(len(re.sub(r'\s', '', book['body'])) / 400))
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
(OUT / 'assets').mkdir()
public_assets = {'style.css', 'reader.js', 'leaf.svg', 'comic-reader.css', 'comic-reader.js'}
for name in public_assets:
    destination = OUT / 'assets' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'assets' / name, destination)
for book in books:
    destination = OUT / 'covers' / book['cover']
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'covers' / book['cover'], destination)
(OUT / '.nojekyll').touch()
e = html.escape


def page(title, description, content, prefix='./', reader=False):
    return f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description, quote=True)}">
<meta name="theme-color" content="#f4f1e9"><link rel="icon" href="{prefix}assets/leaf.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/reader.js" defer></script></head>
<body{' class="reading"' if reader else ''}><a class="skip" href="#main">跳至內容</a>
<header class="site-header"><a class="brand" href="{prefix}"><img src="{prefix}assets/leaf.svg" width="26" height="26" alt="">飛駝<span>作品集</span></a><a class="header-link" href="{prefix}#collection">{'← 回到書架' if reader else '作品書架 ↗'}</a></header>
{content}<footer class="site-footer"><span>飛駝・作品集</span></footer></body></html>'''

cards = ''
for i, b in enumerate(books, 1):
    comic_link = f'<a href="./comics/{b["slug"]}/">閱讀漫畫 <span aria-hidden="true">↗</span></a>' if b.get('comic') else ''
    cards += f'''<article class="book-card"><a class="cover-link" href="./books/{b['slug']}/" aria-label="閱讀《{e(b['title'])}》"><img class="cover" src="./covers/{e(b['cover'])}" alt="《{e(b['title'])}》封面" width="941" height="1672"><span class="cover-action">翻開故事 ↗</span></a><div class="book-info"><span class="eyebrow">卷 {i:02d} <span class="dot">·</span> {e(b['genre'])}</span><h3><a href="./books/{b['slug']}/">{e(b['title'])}</a></h3><p>{e(b['description'])}</p><div class="book-bottom"><span>短篇小說 <span class="dot">·</span> 約 {b['minutes']} 分鐘</span><a href="./books/{b['slug']}/">閱讀小說 <span aria-hidden="true">↗</span></a>{comic_link}</div></div></article>'''
home = f'''<main id="main"><section class="collection home-collection" id="collection"><div class="section-heading"><h1>作品集<span class="count">{len(books):02d}</span></h1></div><div class="books">{cards}</div></section></main>'''
(OUT / 'index.html').write_text(page('飛駝｜作品集', '飛駝的原創作品集。', home))
for b in books:
    comic_link = f'<a class="top-link" href="../../comics/{b["slug"]}/">閱讀漫畫版 →</a>' if b.get('comic') else ''
    paragraphs = ''
    for block in b['body'].split('\n\n'):
        rendered = '<br>'.join(e(line) for line in block.splitlines())
        if block in b.get('bold_paragraphs', []):
            rendered = '<strong>' + rendered + '</strong>'
        paragraphs += '<p>' + rendered + '</p>'
    content = f'''<div class="reading-progress" aria-hidden="true"><div id="progress"></div></div><main id="main"><section class="reader-heading"><p class="eyebrow">{e(b['genre'])} <span class="dot">·</span> 短篇小說</p><h1>{e(b['title'])}</h1><p class="reader-subtitle">{e(b['subtitle'])}</p>{comic_link}<p class="reader-meta">文／飛駝 <span class="dot">·</span> 約 {b['minutes']} 分鐘</p></section><div class="reading-tools" role="group" aria-label="閱讀設定"><span>閱讀設定</span><button id="smaller" type="button" aria-label="縮小字體">A−</button><button id="larger" type="button" aria-label="放大字體">A＋</button><span class="tool-divider"></span><button id="theme" type="button" aria-pressed="false">夜間閱讀</button></div><article class="prose" aria-label="{e(b['title'])}全文">{paragraphs}<div class="story-end">— 完 —</div></article><nav class="reader-end" aria-label="閱讀完成"><a class="primary" href="../../#collection">← 回到書架</a>{comic_link}<a class="top-link" href="#main">回到篇首 ↑</a></nav></main>'''
    target = OUT / 'books' / b['slug']
    target.mkdir(parents=True)
    (target / 'index.html').write_text(page(b['title'] + '｜飛駝', b['description'], content, '../../', True))
    if b.get('comic'):
        build_comic(ROOT, OUT, b)
print(f'Built {len(books)} book(s) → {OUT}')
