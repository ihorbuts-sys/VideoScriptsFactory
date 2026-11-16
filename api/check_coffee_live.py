"""Fetch the published coffee guide through the routes used by the app."""
import argparse
import hashlib
import io
import json
import urllib.request
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parents[1]
FOLDER = BASE / 'catalog/coffee-ordering-v2'
GUIDE = 'cup_shot_eye_in_cd_through'


def check(server, base):
    token = (server / '.token').read_text().strip()
    catalog = json.loads((server / 'catalog/catalog.json').read_text())

    def get(path):
        request = urllib.request.Request(base + path,
            headers={'Authorization': 'Bearer ' + token})
        with urllib.request.urlopen(request, timeout=30) as response:
            assert response.status == 200
            return json.load(response)

    def file(url, source):
        with urllib.request.urlopen(url, timeout=60) as response:
            assert response.status == 200
            body = response.read()
        actual = hashlib.sha256(body).hexdigest()
        assert actual == hashlib.sha256(source.read_bytes()).hexdigest(), source.name
        return body, actual

    scripts = get('/v1/scripts?venueKind=coffee&pageSize=100')
    # The service calls this field "templates" in the app catalog response.
    templates = scripts.get('templates', scripts.get('scripts', []))
    template = next(t for t in templates if t['id'] == 'cafe-before-opening')
    step = next(s for s in template['steps'] if s['id'] == 'shot')
    guides = get('/v1/steps/cafe-before-opening.shot/guides')
    guide = next(g for g in guides['guides'] if g['id'] == GUIDE)
    direct = get('/v1/guides/' + GUIDE)
    assert step['overlays'][0] == guide['overlayURL'] == direct['overlayURL']
    assert guide['alphaFactor'] == .65 and guide['animationSeconds'] > 9
    phase = FOLDER / 'phases/extraction'
    assets = []
    for key, name in [('overlayURL', 'ghost.png'), ('posterURL', 'ghost-poster.png'),
                      ('stripURL', 'ghost-strip.jpg'), ('colorVideoURL', 'color.mp4')]:
        body, sha = file(guide[key], phase / name)
        assets.append(dict(file=name, bytes=len(body), sha256=sha))
        if name == 'ghost.png':
            with Image.open(io.BytesIO(body)) as im:
                assert im.n_frames == 143 and im.size == (405, 720)
                duration = maximum = 0
                for frame in range(im.n_frames):
                    im.seek(frame)
                    duration += im.info['duration']
                    maximum = max(maximum, im.convert('RGBA').getchannel('A').getextrema()[1])
                assert abs(duration / 1000 - guide['animationSeconds']) < .03
                assert maximum <= 166
    collection = get('/v1/guide-collections/coffee-ordering')
    source = json.loads((FOLDER / 'scene-spec.json').read_text())
    assert collection.get('ghostStyle') == source.get('ghost_style')
    assert collection['seconds'] == 16
    assert collection['humanAction'].startswith('Barista behind the counter, left hand')
    for key, name in [('overlayURL', 'ghost.png'), ('colorVideoURL', 'color.mp4')]:
        body, sha = file(collection[key], FOLDER / name)
        assets.append(dict(file='full-scene/' + name, bytes=len(body), sha256=sha))
    assert get('/v1/guides?pageSize=1')['total'] == len(catalog['guides']) == 178
    report = dict(status='passed', api=base, templateID=template['id'],
        templateTitle=template['title'], stepID=step['id'], stepTitle=step['title'],
        guideID=GUIDE, app_template_step_and_direct_guide_urls_match=True,
        animation_seconds=guide['animationSeconds'], full_scene_seconds=16,
        ghost_style=collection.get('ghostStyle'),
        whole_overlay_alpha=.65, fetched_files=assets, existing_guides=178)
    (FOLDER / 'live-api-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', type=Path, required=True)
    parser.add_argument('--base', default='http://127.0.0.1:8765')
    args = parser.parse_args()
    check(args.server, args.base)
