"""Activate reviewed preview art and publish immutable JPEG URLs to the local API."""
from pathlib import Path
from PIL import Image, ImageOps
import argparse
import copy
import hashlib
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parents[1]
LIVE = Path('/Users/ihor.buts/Documents/Development/VideoEditorKit/tools/scriptwriter/catalog')
RELEASE = ROOT / 'publication'
DATE = '2026-10-28'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.clay-tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    os.replace(tmp, path)


def atomic_copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + '.clay-tmp')
    shutil.copy2(source, tmp)
    os.replace(tmp, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true', help='Also switch the live API catalog')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    entries = manifest['entries']
    assert len(entries) == 304 and len({e['canonical_stem'] for e in entries}) == 276
    assert all(e['status'] == 'approved' and e.get('art_direction') == manifest['art_direction'] for e in entries)
    files = {}
    for entry in entries:
        name = entry['imageURL']
        assert Path(name).name == name and name.endswith('.jpg')
        for suffix in ['.jpg', '.png']:
            path = ROOT / 'assets' / (entry['stem'] + suffix)
            with Image.open(path) as image:
                assert image.size == (1080, 1920), path
                image.verify()
        files[name] = digest(ROOT / 'assets' / name)
    for entry in entries:
        assert files[entry['imageURL']] == files[entry['canonical_stem'] + '.jpg'], entry['stem']
    revision = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    RELEASE.mkdir(exist_ok=True)

    # Original artwork and the guide input baseline remain intact. The new edition
    # becomes active by an explicit pointer, rather than overwriting source art.
    baseline = json.loads((BASE / 'guides/watercolor/input_hashes.json').read_text())
    current_inputs = {rel: digest(BASE / rel) for rel in baseline}
    prior_changes = [rel for rel, sha in baseline.items() if current_inputs[rel] != sha]
    captured = RELEASE / 'pre-publication-inputs.json'
    if captured.exists():
        assert current_inputs == json.loads(captured.read_text()), 'Inputs changed during the release'
    else:
        save(captured, current_inputs)
    pointer = dict(art_direction=manifest['art_direction'], revisionSHA256=revision,
                   assetDirectory='previews/clay-3d/assets', manifest='previews/clay-3d/manifest.json',
                   step_files=304, unique_illustrations=276, approved=True, date=DATE)
    save(BASE / 'previews/active-art-revision.json', pointer)

    # Existing catalog pages use small copies. Keep the previous thumbnail set.
    thumbs = BASE / 'catalog/previews/clay-v2'
    thumbs.mkdir(parents=True, exist_ok=True)
    for name in files:
        with Image.open(ROOT / 'assets' / name) as image:
            image = ImageOps.fit(image.convert('RGB'), (270, 480), Image.Resampling.LANCZOS)
            tmp = thumbs / (name + '.clay-tmp.jpg')
            image.save(tmp, quality=90, optimize=True, subsampling=0)
            os.replace(tmp, thumbs / name)
    html_path = BASE / 'catalog/catalog.html'
    if html_path.exists():
        backup = RELEASE / 'previous-catalog.html'
        if not backup.exists():
            shutil.copy2(html_path, backup)
        html = html_path.read_text()
        for name in files:
            html = html.replace('previews/' + name, 'previews/clay-v2/' + name)
        assert all('previews/clay-v2/' + name in html for name in files)
        html_path.write_text(html)
    pdf = BASE / 'catalog/scripts-and-guides.pdf'
    if pdf.exists() and not (RELEASE / 'previous-scripts-and-guides.pdf').exists():
        shutil.copy2(pdf, RELEASE / 'previous-scripts-and-guides.pdf')

    old = json.loads((LIVE / 'catalog.json').read_text())
    backup = RELEASE / 'previous-api-catalog.json'
    if not backup.exists():
        save(backup, old)
    updated = copy.deepcopy(old)
    paths = {name: 'previews/' + sha[:16] + '/' + name for name, sha in files.items()}
    found = []
    for template in updated['templates']:
        for step in template['steps']:
            name = Path(step['imageURL']).name
            assert name in paths, name
            step['imageURL'] = paths[name]
            found.append(name)
    assert len(found) == 304 and set(found) == set(files)
    for group in updated.get('stepGroups', []):
        for step in group['steps']:
            step['imageURL'] = paths[Path(step['imageURL']).name]
    updated.update(generatedAt=DATE, previewArt=pointer)
    for key in ['guides', 'stepGuideOverrides', 'scriptGuideSequences']:
        assert updated.get(key) == old.get(key), key
    stage = BASE / 'api/bundle'
    for name, relative in paths.items():
        target = stage / relative
        if not target.exists():
            atomic_copy(ROOT / 'assets' / name, target)
        assert digest(target) == files[name]
        # Flat compatibility files are independent copies, preserving immutable
        # revisions even if a legacy tool later rewrites a flat filename.
        atomic_copy(target, stage / 'previews' / name)
    save(stage / 'catalog.json', updated)
    save(RELEASE / 'api-catalog.json', updated)
    if args.publish:
        for name, relative in paths.items():
            target = LIVE / relative
            if not target.exists():
                atomic_copy(stage / relative, target)
            assert digest(target) == files[name]
            atomic_copy(target, LIVE / 'previews' / name)
        for guide in updated['guides'].values():
            for key in ['overlay', 'poster', 'strip', 'scenario', 'model3D']:
                assert (LIVE / guide[key]).is_file(), guide[key]
        # Every new picture exists before the server observes the atomic index.
        save(LIVE / 'catalog.json', updated)
    report = dict(status='published' if args.publish else 'staged', revision=revision,
                  step_images=304, unique_illustrations=276, reused_step_files=28,
                  size=[1080, 1920], catalog_thumbnail_size=[270, 480],
                  immutable_preview_urls=True, guide_inputs_preserved=len(baseline),
                  historical_snapshot_differences=prior_changes,
                  source_files_changed_by_release=[],
                  guide_data_changed=False, previous_art_preserved=True,
                  live_catalog=str(LIVE / 'catalog.json') if args.publish else None)
    assert all(digest(BASE / rel) == sha for rel, sha in current_inputs.items())
    save(RELEASE / 'release-report.json', report)
    manifest['publication'] = dict(project_active=True, api_published=args.publish, revision=revision)
    manifest['status'] = 'published' if args.publish else 'ready_for_api_publication'
    save(ROOT / 'manifest.json', manifest)
    print(json.dumps(report))


if __name__ == '__main__':
    main()
