"""Publish selected comic pages, never production references or drafts."""
import html
import json
import shutil
from pathlib import Path

from PIL import Image

WEBP_QUALITY = 80
WEBP_METHOD = 6


def local_file(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f'Missing or invalid source: {relative}')
    return path


def build_comic(root, out, book):
    manifest_path = local_file(root, book['comic'])
    manifest = json.loads(manifest_path.read_text())
    names = manifest['pages']
    if not names or len(names) != len(set(names)):
        raise ValueError('Comic needs a nonempty list of unique pages')
    source_dir = root / manifest['source_directory']
    target = out / 'comics' / book['slug']
    target.mkdir(parents=True)
    (target / 'pages').mkdir()
    (target / 'thumbnails').mkdir()
    pages = []
    original_bytes = web_bytes = 0
    for index, name in enumerate(names, 1):
        source = local_file(root, source_dir / name)
        if source.suffix.lower() not in {'.png', '.webp'}:
            raise ValueError(f'Only PNG and WebP sources are supported: {name}')
        filename = f'{index:03d}.webp'
        with Image.open(source) as image:
            image = image.convert('RGB')
            width, height = image.size
            if source.suffix.lower() == '.webp':
                shutil.copyfile(source, target / 'pages' / filename)
            else:
                image.save(target / 'pages' / filename, 'WEBP', quality=WEBP_QUALITY, method=WEBP_METHOD)
            image.thumbnail((240, 360), Image.Resampling.LANCZOS)
            image.save(target / 'thumbnails' / filename, 'WEBP', quality=WEBP_QUALITY, method=WEBP_METHOD)
        original_bytes += source.stat().st_size
        web_bytes += (target / 'pages' / filename).stat().st_size
        pages.append(dict(src=f'pages/{filename}', thumbnail=f'thumbnails/{filename}', width=width, height=height))
    config = dict(slug=book['slug'], title=book['title'], pages=pages)
    template = (root / 'templates/comic.html').read_text()
    values = dict(TITLE=html.escape(book['title']), SLUG=book['slug'], TOTAL=str(len(pages)),
                  FIRST=pages[0]['src'], WIDTH=str(pages[0]['width']), HEIGHT=str(pages[0]['height']),
                  CONFIG=json.dumps(config, ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026'))
    for key, value in values.items():
        template = template.replace(f'@@{key}@@', value)
    (target / 'index.html').write_text(template)
    print(f"Comic {book['slug']}: {len(pages)} pages, source {original_bytes:,} → WebP {web_bytes:,} bytes (PNG Q{WEBP_QUALITY}; WebP copied)")
