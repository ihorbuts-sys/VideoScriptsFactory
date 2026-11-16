"""Register only the complete, browser-checked Morning ritual replacement."""
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
FOLDER=BASE/'catalog/glass-rollout/sequences/cafe-morning-ritual'
MANIFEST=BASE/'catalog/clay-scenes/active-revisions.json'


def run():
    spec=json.loads((FOLDER/'scene-spec.json').read_text())
    browser=json.loads((FOLDER/'composite-browser-check.json').read_text())
    checks=json.loads((FOLDER/'assembly-checks.json').read_text())
    assert browser['status']==checks['status']=='passed' and checks['all_four_steps_regenerated']
    assert browser['overlay_sha256']==hashlib.sha256((FOLDER/'ghost.png').read_bytes()).hexdigest()
    assert [s['step_id'] for s in spec['steps']]==['light','cup','pastry','corner']
    data=json.loads(MANIFEST.read_text())
    data.setdefault('sequences',{})['cafe-morning-ritual']=dict(reviewed=True,
        reviewer='Native per-step review, lossless boundary comparison and embedded-browser playback',
        folder=str(FOLDER.relative_to(BASE)),seconds=spec['duration_s'],steps=spec['steps'],
        opacity_mode='image_view',revision=spec['revision'],
        files={n:hashlib.sha256((FOLDER/n).read_bytes()).hexdigest() for n in ['ghost.png','preview.mp4','poster.png','strip.jpg']})
    MANIFEST.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(status='registered',template='cafe-morning-ritual',steps=4)))


if __name__=='__main__':run()
