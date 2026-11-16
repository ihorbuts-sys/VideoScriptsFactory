"""Publish reviewed P0 picture variants without replacing the legacy collection."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def assets(out, versioned_file):
    manifest = json.loads((ROOT / 'previews/clay-3d/p0/manifest.json').read_text())
    published = {}
    for entry in manifest['entries']:
        assert entry['status'] == 'approved'
        source = ROOT / entry['asset']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256']
        published[entry['id']], _ = versioned_file(str(source), out, 'previews/p0', source.name)
    return manifest, published


def apply(bundle, out, versioned_file):
    manifest, published = assets(out, versioned_file)
    bindings = manifest['stepBindings']
    steps = [(t['id'], s) for t in bundle['templates'] for s in t['steps']]
    steps += [(s['templateID'], s) for g in bundle['stepGroups'] for s in g['steps']]
    for template, step in steps:
        binding = bindings.get(template + '.' + step['id'])
        if not binding:
            continue
        if isinstance(binding, dict):
            step['previewByVenueKind'] = {kind: published[key] for kind, key in binding.items()}
            path = next(iter(step['previewByVenueKind'].values()))
        else:
            path = published[binding]
        step.update(imageURL=path, examplePreview=path)
    bundle.setdefault('previewArt', {})['profiles'] = {
        **bundle.get('previewArt', {}).get('profiles', {}),
        'p0': {'manifest': 'previews/clay-3d/p0/manifest.json', 'revisionSHA256': manifest['revisionSHA256'],
               'slots': len(manifest['entries']), 'newIllustrations': 8, 'reuseCorrections': 1}}


def guide_examples(registry, out, versioned_file):
    manifest, published = assets(out, versioned_file)
    for gid, key in manifest['guideBindings'].items():
        if gid in registry['guides']:  # archived guides are not served
            registry['guides'][gid]['examplePreview'] = published[key]
