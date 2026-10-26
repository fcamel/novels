import json
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_comics
import compare_images

class AssetFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for directory in ['content', 'comics/test/pages', 'templates', 'tools/image-compare', 'dist']:
            (self.root / directory).mkdir(parents=True)
        self.manifest = self.root / 'comics/test/comic.json'
        self.manifest.write_text(json.dumps({'source_directory': 'comics/test/pages', 'pages':['a.png','b.webp']}))
        Image.new('RGB', (64, 96), 'gray').save(self.root / 'comics/test/pages/a.png')
        Image.new('RGB', (64, 96), 'red').save(self.root / 'comics/test/pages/b.webp', quality=70)
        (self.root / 'templates/comic.html').write_text('@@CONFIG@@')
        self.previous_root = compare_images.ROOT
        compare_images.ROOT = self.root
        self.addCleanup(setattr, compare_images, 'ROOT', self.previous_root)
        self.output = self.root / 'local-production/comparison'

    def test_png_encoding_webp_exact_copy_and_private_exclusion(self):
        build_comics.build_comic(self.root, self.root/'dist', {'slug':'test','title':'測試','comic':'comics/test/comic.json'})
        target = self.root/'dist/comics/test'
        data = json.loads((target/'index.html').read_text())
        self.assertEqual([p['src'] for p in data['pages']], ['pages/001.webp', 'pages/002.webp'])
        self.assertEqual([p['thumbnail'] for p in data['pages']], ['thumbnails/001.webp', 'thumbnails/002.webp'])
        self.assertEqual((target/data['pages'][1]['src']).read_bytes(), (self.root/'comics/test/pages/b.webp').read_bytes())
        with Image.open(target/data['pages'][0]['src']) as image:
            self.assertEqual(image.format, 'WEBP')
        self.assertFalse(list((self.root/'dist').rglob('*.png')))

    def test_adopt_preserves_original_and_uses_reviewed_bytes(self):
        original = (self.root/'comics/test/pages/a.png').read_bytes()
        webp = (self.root/'comics/test/pages/b.webp').read_bytes()
        compare_images.prepare(self.manifest, self.output)
        candidate = (self.output/'001-q80.webp').read_bytes()
        compare_images.adopt(self.manifest,self.output,80)
        self.assertEqual(json.loads(self.manifest.read_text())['pages'], ['a.webp','b.webp'])
        self.assertEqual((self.root/'comics/test/pages/a.webp').read_bytes(), candidate)
        self.assertEqual((self.root/'comics/test/pages/b.webp').read_bytes(), webp)
        self.assertFalse((self.root/'comics/test/pages/a.png').exists())
        backups = list((self.root/'local-production/originals').rglob('*.png'))
        self.assertEqual(backups[0].read_bytes(),original)

    def test_changed_source_refuses_before_mutation(self):
        compare_images.prepare(self.manifest,self.output)
        Image.new('RGB',(64,96),'blue').save(self.root/'comics/test/pages/a.png')
        with self.assertRaisesRegex(ValueError,'Source changed'):
            compare_images.adopt(self.manifest,self.output,80)
        self.assertTrue((self.root/'comics/test/pages/a.png').exists())
        self.assertFalse((self.root/'comics/test/pages/a.webp').exists())

if __name__ == '__main__': unittest.main()
