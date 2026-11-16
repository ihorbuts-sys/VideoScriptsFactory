"""Publish additive visit collections without changing existing scripts or guides."""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE / 'catalog/shared-venue-visits'


def versioned(source, catalog, kind, name):
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    relative = f'{kind}/{sha[:16]}/{name}'
    destination = catalog / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copy2(source, destination)
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == sha
    return relative


def publish(catalog):
    previous = (catalog / 'catalog.json').read_bytes()
    records = {}
    kinds = {'cafe': ['coffee'], 'bakery': ['bakery'], 'bar': ['craft-beer']}
    for venue in ['cafe', 'bakery', 'bar']:
        folder = ROOT / venue
        if not (folder / 'export-checks.json').exists():
            continue
        checks = json.loads((folder / 'export-checks.json').read_text())
        spec = json.loads((folder / 'scene-spec.json').read_text())
        assert checks['status'] == 'passed' and checks['max_alpha'] <= 166
        assert checks['full_route_continuous'] and checks['no_embedded_viewfinder']
        for name, sha in checks['files'].items():
            assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == sha
        record = dict(id=venue, title=spec['title'], venueKinds=kinds[venue],
            seconds=spec['duration_s'], animationSeconds=spec['duration_s'], alphaFactor=.65,
            scope='complete_non_character_visit', rendering='shared-3d-venue-visit',
            humanPerformanceIncluded=False, viewfinderEmbedded=False, sameSceneForBothVariants=True,
            composition=spec['composition'], lighting=spec['lighting'], mobile=spec['mobile'], phases=[])
        for key, filename, kind in [('overlay', 'ghost.png', 'sequences'), ('video', 'color.mp4', 'sequences'),
            ('poster', 'ghost-poster.png', 'sequences'), ('colorPoster', 'color-poster.png', 'sequences'),
            ('strip', 'ghost-strip.jpg', 'sequences'), ('colorStrip', 'color-strip.jpg', 'sequences'),
            ('blender', 'scene.blend', '3d'), ('sceneSpec', 'scene-spec.json', '3d')]:
            record[key] = versioned(folder / filename, catalog, kind, f'shared-{venue}-{filename}')
        for phase in spec['exported_phases']:
            clip = dict(id=phase['id'], title=phase['id'].title(), seconds=phase['capture_seconds'],
                animationSeconds=phase['animation_seconds'], handoverSeconds=phase['handover_seconds'],
                nextPhaseID=phase['next_phase'], scope=phase['scope'], alphaFactor=.65,
                sourceStartSeconds=phase['start_s'], sourceFirstFrame=phase['source_first_frame'],
                sourceLastFrame=phase['source_last_frame'])
            for key, filename in [('overlay', 'ghost.png'), ('video', 'color.mp4'),
                ('poster', 'ghost-poster.png'), ('colorPoster', 'color-poster.png'),
                ('strip', 'ghost-strip.jpg'), ('colorStrip', 'color-strip.jpg')]:
                clip[key] = versioned(folder / 'phases' / phase['id'] / filename, catalog,
                    'sequences', f'shared-{venue}-{phase["id"]}-{filename}')
            record['phases'].append(clip)
        records[venue] = record
    assert records, 'No verified collection is ready'
    data = dict(version=1, collections=records)
    payload = json.dumps(data, indent=2) + '\n'
    destination = catalog / 'guide-collections.json'
    temporary = destination.with_suffix('.json.tmp')
    temporary.write_text(payload)
    os.replace(temporary, destination)
    assert (catalog / 'catalog.json').read_bytes() == previous, 'Existing guide/script catalog changed'
    report = dict(status='passed', collections=list(records), phases=sum(len(v['phases']) for v in records.values()),
        existing_catalog_sha256=hashlib.sha256(previous).hexdigest(), existing_catalog_unchanged=True,
        destination=str(destination), immutable_asset_urls=True, no_extra_alpha_multiplier=True)
    (ROOT / 'publication.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    publish(parser.parse_args().out)
