"""Publish the coffee collection; step bindings are published separately."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from publish_venue_collections import versioned

BASE = Path(__file__).resolve().parents[1]
FOLDER = BASE / 'catalog/coffee-ordering'
COLLECTION_ID = 'coffee-ordering'


def publish(catalog):
    original = (catalog / 'catalog.json').read_bytes()
    spec = json.loads((FOLDER / 'scene-spec.json').read_text())
    checks = json.loads((FOLDER / 'export-checks.json').read_text())
    assert checks['status'] == 'passed'
    assert checks['max_alpha'] <= 166 and checks['whole_overlay_alpha'] == .65
    assert spec['full_script_sequence_complete'] is False
    for name, sha in checks['files'].items():
        assert hashlib.sha256((FOLDER / name).read_bytes()).hexdigest() == sha
    view_checks = None
    if spec.get('display', {}).get('opacity_mode') == 'image_view':
        view_checks = json.loads((FOLDER / 'view-overlay-checks.json').read_text())
        assert view_checks['status'] == 'passed' and view_checks['image_opacity_baked'] == 1
        assert view_checks['walls_excluded'] and view_checks['floor_excluded']
        browser = json.loads((FOLDER / 'composite-browser-check.json').read_text())
        assert browser['status'] == 'passed'
        assert browser['overlay_sha256'] == view_checks['files']['view-overlay.png']
        for name, sha in view_checks['files'].items():
            assert hashlib.sha256((FOLDER / name).read_bytes()).hexdigest() == sha
    key = COLLECTION_ID
    manifest = BASE / 'catalog/clay-scenes/active-revisions.json'
    bindings = []
    if manifest.exists():
        for gid, row in json.loads(manifest.read_text()).get('guides', {}).items():
            folder = (BASE / row['folder']).resolve()
            if folder == FOLDER / 'phases/extraction':
                bindings.append(dict(templateID=row['context_template'],
                    stepID=row['context_step'], guideID=gid, phaseID='extraction'))
    record = dict(id=key, title=spec['title'], venueKinds=['coffee'],
        revision=spec.get('revision', 'initial-counter-proof'),
        ghostStyle=spec.get('ghost_style'),
        seconds=spec['duration_s'], animationSeconds=spec['duration_s'], alphaFactor=.65,
        status='scene-proof', scope=spec['scope'], rendering='native-clay-3d',
        fullScriptSequenceComplete=False, existingGuidesReplaced=bool(bindings),
        templateBindings=bindings,
        humanPerformanceIncluded=True, humanAction=spec['human_action'],
        colorResolution=[540, 960], ghostResolution=spec.get('ghost_resolution', [540, 960]),
        viewfinderEmbedded=False, sameSceneForBothVariants=True,
        composition=spec['composition'], lighting=spec['lighting'], mobile=spec['mobile'], phases=[])

    def add_files(row, folder, prefix, include_scene=False):
        files = [('overlay', 'ghost.png', 'sequences'), ('video', 'color.mp4', 'sequences'),
            ('poster', 'ghost-poster.png', 'sequences'), ('colorPoster', 'color-poster.png', 'sequences'),
            ('strip', 'ghost-strip.jpg', 'sequences'), ('colorStrip', 'color-strip.jpg', 'sequences')]
        if view_checks:
            replacements = {'ghost.png': 'view-overlay.png',
                'ghost-poster.png': 'view-overlay-poster.png', 'ghost-strip.jpg': 'view-overlay-strip.jpg'}
            files = [(field, replacements.get(name, name), kind) for field, name, kind in files]
            row.update(alphaFactor=1, imageViewOpacity=spec['display']['image_opacity'],
                opacityAppliedIn='image_view', backgroundDelaySeconds=2,
                viewfinderEmbedded=False, viewfinderLayer='separate_ui',
                wallsEmbedded=False, floorEmbedded=False, ceilingEmbedded=False)
        if include_scene:
            files += [('blender', 'scene.blend', '3d'), ('sceneSpec', 'scene-spec.json', '3d')]
        for field, name, kind in files:
            row[field] = versioned(folder / name, catalog, kind, prefix + '-' + name)

    add_files(record, FOLDER, key, include_scene=True)
    for phase in spec['exported_phases']:
        clip = dict(id=phase['id'], title=phase['id'].replace('-', ' ').title(),
            seconds=phase['capture_seconds'], animationSeconds=phase['animation_seconds'],
            handoverSeconds=phase['handover_seconds'], nextPhaseID=phase['next_phase'],
            sourceStartSeconds=phase['start_s'], scope=phase['scope'], alphaFactor=.65)
        add_files(clip, FOLDER / 'phases' / phase['id'], key + '-' + phase['id'])
        record['phases'].append(clip)
    target = catalog / 'guide-collections.json'
    data = json.loads(target.read_text()) if target.exists() else dict(version=1, collections={})
    data['collections'][key] = record
    temporary = target.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    os.replace(temporary, target)
    assert (catalog / 'catalog.json').read_bytes() == original
    report = dict(status='published_as_separate_proof', collection=key,
        endpoint='/v1/guide-collections/' + key, phases=len(record['phases']),
        existing_catalog_unchanged=True, existing_catalog_sha256=hashlib.sha256(original).hexdigest(),
        source_folder=str(FOLDER), api_catalog=str(catalog))
    (FOLDER / 'publication.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--id', default='coffee-ordering')
    args = parser.parse_args()
    if args.source:
        FOLDER = args.source.resolve()
    COLLECTION_ID = args.id
    publish(args.out)
