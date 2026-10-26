"""Exercise multiple works through the complete publishing pipeline."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from compare_images import comparison_name

class CollectionLayout(unittest.TestCase):
    def test_multi_work_build_and_private_asset_exclusion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for folder in ('scripts', 'templates', 'assets'):
                shutil.copytree(ROOT / folder, root / folder)
            (root / 'content/novels').mkdir(parents=True)
            (root / 'covers').mkdir()
            books = []
            for slug, comic in [('first', True), ('second', True), ('prose-only', False)]:
                (root / f'content/novels/{slug}.txt').write_text('測試正文。')
                Image.new('RGB', (64, 96), 'white').save(root / f'covers/{slug}.webp')
                book = dict(slug=slug,title=slug,description='測試',subtitle='測試',genre='小說',text=f'{slug}.txt',cover=f'{slug}.webp')
                if comic:
                    folder = root / 'comics' / slug
                    (folder / 'pages').mkdir(parents=True)
                    Image.new('RGB',(64,96),'gray').save(folder/'pages/final.webp')
                    (folder/'private-notes.md').write_text('Do not publish')
                    (folder/'comic.json').write_text(json.dumps({'source_directory':f'comics/{slug}/pages','pages':['final.webp']}))
                    book['comic']=f'comics/{slug}/comic.json'
                books.append(book)
            (root/'content/books.json').write_text(json.dumps(books))
            subprocess.run([sys.executable,str(root/'scripts/build.py')],check=True,capture_output=True)
            out=root/'dist'
            index=(out/'index.html').read_text()
            for book in books:
                slug=book['slug']
                self.assertIn(f'./covers/{slug}.webp',index)
                self.assertTrue((out/f'books/{slug}/index.html').is_file())
                self.assertTrue((out/f'covers/{slug}.webp').is_file())
                if 'comic' in book:
                    self.assertTrue((out/f'comics/{slug}/index.html').is_file())
                    self.assertEqual((out/f'comics/{slug}/pages/001.webp').read_bytes(),(root/f'comics/{slug}/pages/final.webp').read_bytes())
                    self.assertFalse((out/f'comics/{slug}/private-notes.md').exists())
                else:
                    self.assertNotIn(f'./comics/{slug}/',index)
            self.assertFalse((out/'content').exists())
            self.assertFalse(list(out.rglob('comic.json')))

    def test_comparison_directories_distinguish_same_manifest_names(self):
        self.assertEqual(comparison_name(Path('comics/first/comic.json')),'first')
        self.assertEqual(comparison_name(Path('comics/second/comic.json')),'second')

if __name__ == '__main__': unittest.main()
