"""Package only the reviewed P0 gallery and its animation assets for public hosting."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def build(out,include_character_guides=False):
    source = ROOT / 'catalog/p0'
    players = json.loads((source / 'players.json').read_text())
    records = [r for r in players['guides'] if r['ready']]
    completion=json.loads((source/'completion-checks.json').read_text())
    assert completion['status']=='passed' and len(records)==players['total']==completion['guides']
    # Owner chose local/API-only delivery for the eight character guides.
    # Do not expand the public scope without a later explicit instruction.
    if not include_character_guides:records=[r for r in records if not r.get('filmingMode')]
    dist = out / 'dist'
    dist.mkdir(parents=True, exist_ok=True)
    public = []
    digests = {}
    for record in records:
        gid = record['id']
        folder = dist / 'animations' / gid
        folder.mkdir(parents=True, exist_ok=True)
        for suffix in ['.png', '_poster.png', '_selector.png']:
            src = ROOT / 'guides/p0/renders' / (gid + suffix)
            dst = folder / ('guide' + suffix)
            data = src.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if suffix == '.png':
                assert digest == record['sha256'], gid
            shutil.copyfile(src, dst)
            digests[str(dst.relative_to(dist))] = digest
        row = {k: record[k] for k in ['id', 'title', 'shotType', 'invariant', 'durationSec',
                                      'setupBeatSeconds', 'ready', 'sha256', 'seconds']}
        row['base'] = 'animations/' + gid + '/'
        for key in ['camera','filmingMode','previewMirrored']:
            if key in record:row[key]=record[key]
        public.append(row)
    active = {r['id'] for r in public}
    types = [{k: kind[k] for k in ['id', 'title', 'guides']} for kind in players['types']]
    for kind in types:
        kind['guides'] = [gid for gid in kind['guides'] if gid in active]
    manifest = dict(ready=len(public), total=len(public), types=types, guides=public)
    (dist / 'players.json').write_text(json.dumps(manifest, indent=2) + '\n')
    html = (source / 'index.html').read_text()
    html = html.replace('<title>Loca / P0 line-art guides</title>', '<title>Loca Camera / Filming guides</title>')
    html = html.replace('<h1>P0 / line-art animations</h1>', '<h1>Filming guides</h1>')
    html = html.replace('<a href="../animations.html">Guide catalog</a> · <a href="progress.json">Batch progress</a>', 'Loca Camera / Animated shot guides')
    html = re.sub(r'<p>Step-card pictures.*?</p>',
                  '<p>Choose a shot and press Play / replay. Use the target pose to frame your shot, then follow the movement. Switch backgrounds and opacity to preview the transparent overlay.</p>', html)
    html = html.replace(",['Blender scene','scene.blend'],['Checks','export-checks.json']", '')
    html = html.replace('setInterval(refresh,5000)', 'setInterval(refresh,60000)')
    for private in ['127.0.0.1', 'localhost', '/Users/', '.blend', 'progress.json', 'export-checks.json', 'README.md', '../animations.html']:
        assert private not in html, private
    (dist / 'index.html').write_text(html)
    allowed = {'index.html', 'players.json'} | set(digests)
    assert {str(p.relative_to(dist)) for p in dist.rglob('*') if p.is_file()} == allowed
    assert all((dist / path).stat().st_size < 25 * 1024 * 1024 for path in digests)
    report = dict(status='passed', guides=len(public), animation_assets=len(digests),
                  bytes=sum((dist / path).stat().st_size for path in digests), sha256=digests,
                  excluded=['Blender scenes', 'source frames', 'internal reports', 'credentials', 'local API'])
    (source / 'public-package-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'sha256'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'catalog/public-gallery-upload')
    parser.add_argument('--include-character-guides',action='store_true',help='Requires a new explicit owner instruction to publish the character guides; default scope is the original 29.')
    args=parser.parse_args();build(args.out.resolve(),args.include_character_guides)
