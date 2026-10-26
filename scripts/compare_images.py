"""Build a local PNG/WebP comparison; adopt only after human visual review."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image
from build_comics import local_file

ROOT = Path(__file__).resolve().parent.parent


def comparison_name(manifest):
    # Every work may use comic.json; retain a separate output directory per work.
    return manifest.parent.name if manifest.name == 'comic.json' else manifest.stem


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(manifest_path, output):
    manifest = json.loads(manifest_path.read_text())
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, name in enumerate(manifest['pages'], 1):
        source = local_file(ROOT, Path(manifest['source_directory']) / name)
        if source.suffix.lower() not in {'.png', '.webp'}:
            raise ValueError(f'Unsupported source: {name}')
        original = f'{index:03d}-original{source.suffix.lower()}'
        shutil.copyfile(source, output / original)
        row = dict(name=name, original=original, sha256=digest(source), bytes=source.stat().st_size, variants={})
        with Image.open(source) as image:
            image = image.convert('RGB')
            row.update(width=image.width, height=image.height)
            for quality in (70, 80):
                filename = f'{index:03d}-q{quality}.webp'
                image.save(output / filename, 'WEBP', quality=quality, method=6)
                row['variants'][str(quality)] = dict(src=filename, bytes=(output / filename).stat().st_size, sha256=digest(output / filename))
        rows.append(row)
    report = dict(manifest=str(manifest_path.relative_to(ROOT)), source_directory=manifest['source_directory'], pages=rows)
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    for file in (ROOT / 'tools/image-compare').iterdir():
        if file.is_file():
            shutil.copyfile(file, output / file.name)
    print(f'Comparison: {output / "index.html"}')
    print(f'Original total: {sum(r["bytes"] for r in rows):,} bytes')
    for quality in ('70', '80'):
        print(f'Q{quality}: {sum(r["variants"][quality]["bytes"] for r in rows):,} bytes')


def adopt(manifest_path, output, quality):
    manifest = json.loads(manifest_path.read_text())
    report = json.loads((output / 'report.json').read_text())
    if (report['manifest'] != str(manifest_path.relative_to(ROOT)) or
            report['source_directory'] != manifest['source_directory'] or
            [r['name'] for r in report['pages']] != manifest['pages']):
        raise ValueError('Page list changed; regenerate the comparison before adoption.')
    changes = []
    for row in report['pages']:
        source = local_file(ROOT, Path(manifest['source_directory']) / row['name'])
        if digest(source) != row['sha256']:
            raise ValueError(f'Source changed after comparison: {source.name}')
        # Avoid repeated lossy encoding of sources already adopted as WebP.
        if source.suffix.lower() == '.webp':
            continue
        variant = row['variants'][str(quality)]
        candidate = local_file(output, variant['src'])
        if digest(candidate) != variant['sha256']:
            raise ValueError(f'Comparison candidate changed: {candidate.name}')
        destination = source.with_suffix('.webp')
        if destination.exists():
            raise ValueError(f'Will not overwrite existing source: {destination}')
        changes.append((source, candidate, destination, row['sha256']))
    # Preserve originals first. All source/candidate validation finishes before mutations.
    archive = ROOT / 'local-production' / 'originals' / comparison_name(manifest_path)
    archive.mkdir(parents=True, exist_ok=True)
    for source, candidate, destination, sha in changes:
        backup = archive / f'{source.stem}-{sha[:12]}{source.suffix}'
        shutil.copy2(source, backup)
        if digest(backup) != sha:
            raise ValueError('Backup verification failed')
        shutil.copyfile(candidate, destination)
    replacements = {str(s.relative_to((ROOT / manifest['source_directory']).resolve())): str(d.relative_to((ROOT / manifest['source_directory']).resolve())) for s, _, d, _ in changes}
    manifest['pages'] = [replacements.get(name, name) for name in manifest['pages']]
    temporary = manifest_path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(manifest_path)
    for source, _, _, _ in changes:
        source.unlink()
    print(f'Adopted {len(changes)} Q{quality} WebP pages. Original PNGs: {archive}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', help='Project-relative comic manifest, e.g. comics/huashan-lun-ye/comic.json')
    parser.add_argument('--adopt', type=int, choices=(70, 80), help='After visual approval, adopt reviewed WebP and move PNG to ignored local backup')
    args = parser.parse_args()
    manifest = local_file(ROOT, args.manifest)
    output = ROOT / 'local-production' / 'image-compare' / comparison_name(manifest)
    if args.adopt:
        adopt(manifest, output, args.adopt)
    else:
        prepare(manifest, output)


if __name__ == '__main__':
    main()
