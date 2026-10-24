"""Build a portable, dependency-free novel collection for GitHub Pages."""
import html
import json
import math
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dist'
books = json.loads((ROOT / 'content/books.json').read_text())
assert books, 'Add at least one book'
slugs = set()
for book in books:
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', book['slug']), 'Invalid slug'
    assert book['slug'] not in slugs, 'Duplicate slug'
    slugs.add(book['slug'])
    for key, folder in [('text', 'content'), ('cover', 'assets')]:
        path = ROOT / folder / book[key]
        assert path.is_file() and path.resolve().is_relative_to((ROOT / folder).resolve()), f'Missing or invalid {key}'
    book['body'] = (ROOT / 'content' / book['text']).read_text().strip()
    book['minutes'] = max(1, math.ceil(len(re.sub(r'\s', '', book['body'])) / 400))
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT / 'assets', OUT / 'assets')
(OUT / '.nojekyll').touch()
e = html.escape


def page(title, description, content, prefix='./', reader=False):
    return f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description, quote=True)}">
<meta name="theme-color" content="#f4f1e9"><link rel="icon" href="{prefix}assets/leaf.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/reader.js" defer></script></head>
<body{' class="reading"' if reader else ''}><a class="skip" href="#main">跳至內容</a>
<header class="site-header"><a class="brand" href="{prefix}"><img src="{prefix}assets/leaf.svg" width="26" height="26" alt="">fcamel<span>小說集</span></a><a class="header-link" href="{prefix}#collection">{'← 回到書架' if reader else '作品書架 ↗'}</a></header>
{content}<footer class="site-footer"><span>fcamel 的小說集</span><span>故事未完，來日續頁。</span></footer></body></html>'''

cards = ''
for i, b in enumerate(books, 1):
    cards += f'''<article class="book-card"><a class="cover-link" href="./books/{b['slug']}/" aria-label="閱讀《{e(b['title'])}》"><img class="cover" src="./assets/{e(b['cover'])}" alt="《{e(b['title'])}》封面" width="941" height="1672"><span class="cover-action">翻開故事 ↗</span></a><div class="book-info"><span class="eyebrow">卷 {i:02d} <span class="dot">·</span> {e(b['genre'])}</span><h3><a href="./books/{b['slug']}/">{e(b['title'])}</a></h3><p>{e(b['description'])}</p><div class="book-bottom"><span>短篇小說 <span class="dot">·</span> 約 {b['minutes']} 分鐘</span><a href="./books/{b['slug']}/">開始閱讀 <span aria-hidden="true">↗</span></a></div></div></article>'''
first = books[0]
home = f'''<main id="main"><section class="hero"><div class="hero-text"><p class="eyebrow">字裡行間，自有天地</p><h1>一頁，<br>入<span>江湖。</span></h1><p class="hero-description">把想像寫成故事，把故事留在這裡。<br>歡迎走進我的小說集。</p><a class="primary" href="#collection">翻閱作品 <span aria-hidden="true">↓</span></a><div class="hero-note"><span class="seal" aria-hidden="true">小說</span><span>山水有相逢，故事慢慢讀。</span></div></div><a class="hero-art" href="./books/{first['slug']}/" aria-label="閱讀《{e(first['title'])}》"><img src="./assets/{e(first['cover'])}" alt="水墨華山雲海，峭壁上一株綠葉，題字華山論葉" width="941" height="1672"><span class="art-caption">首卷・{e(first['title'])}</span></a><span class="vertical-note" aria-hidden="true">一葉一世界，一書一江湖</span></section>
<section class="collection" id="collection"><div class="section-heading"><div><p class="eyebrow">落筆成卷</p><h2>作品書架<span class="count">{len(books):02d}</span></h2></div><p>每一本，都是另一個世界。</p></div><div class="books">{cards}</div><div class="colophon"><span aria-hidden="true">✳</span><p>還有一些故事，正在路上。<br><span>新作將陸續收錄於此。</span></p></div></section></main>'''
(OUT / 'index.html').write_text(page('fcamel 小說集｜一頁，入江湖。', 'fcamel 的原創小說集。翻開《華山論葉》，走進字裡行間的江湖。', home))
for b in books:
    paragraphs = ''.join('<p>' + '<br>'.join(e(line) for line in block.splitlines()) + '</p>' for block in b['body'].split('\n\n'))
    content = f'''<div class="reading-progress" aria-hidden="true"><div id="progress"></div></div><main id="main"><section class="reader-heading"><p class="eyebrow">{e(b['genre'])} <span class="dot">·</span> 短篇小說</p><h1>{e(b['title'])}</h1><p class="reader-subtitle">{e(b['subtitle'])}</p><p class="reader-meta">文／fcamel <span class="dot">·</span> 約 {b['minutes']} 分鐘</p></section><div class="reading-tools" role="group" aria-label="閱讀設定"><span>閱讀設定</span><button id="smaller" type="button" aria-label="縮小字體">A−</button><button id="larger" type="button" aria-label="放大字體">A＋</button><span class="tool-divider"></span><button id="theme" type="button" aria-pressed="false">夜間閱讀</button></div><article class="prose" aria-label="{e(b['title'])}全文">{paragraphs}<div class="story-end">— 完 —</div></article><nav class="reader-end" aria-label="閱讀完成"><p>一卷讀罷，江湖還在。</p><a class="primary" href="../../#collection">← 回到書架</a><a class="top-link" href="#main">回到篇首 ↑</a></nav></main>'''
    target = OUT / 'books' / b['slug']
    target.mkdir(parents=True)
    (target / 'index.html').write_text(page(b['title'] + '｜fcamel 小說集', b['description'], content, '../../', True))
print(f'Built {len(books)} book(s) → {OUT}')
