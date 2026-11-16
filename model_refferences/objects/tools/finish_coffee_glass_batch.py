"""Export, browser-check and publish each guide as its native render completes."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import coffee_glass_progress as progress
from export_glass_guide import run as export

BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'catalog/glass-rollout/coffee'
API=BASE/'api'
KEYS=['cup-orbit','order','menu-to-cup','cup-out','morning-pair','morning-room','entrance']


def run(catalog,keys=None):
    keys=keys or KEYS
    complete=set()
    deadline=time.monotonic()+7200
    while len(complete)<len(keys):
        assert time.monotonic()<deadline,'Native renders did not finish within the review window'
        for key in keys:
            if key in complete:continue
            folder=ROOT/key
            review=folder/'review-status.json'
            if review.exists() and json.loads(review.read_text()).get('status')=='rejected':
                complete.add(key)
                print('COFFEE_GUIDE_WITHDRAWN',key,flush=True)
                continue
            if not (folder/'render-ready.json').exists():continue
            source=json.loads((folder/'scene-spec.json').read_text())
            if source.get('commercial_purpose'):
                review=json.loads((folder/'commercial-review.json').read_text())
                assert review['status']=='passed' and review.get('visual_preview_review')
                assert review.get('no_humans') and review.get('no_hand_animation')
                assert review.get('clearance_frames')==source['frame_count']
            if source.get('interaction_checks'):
                review=folder/'interaction-review.json'
                if not review.exists():continue
                assert json.loads(review.read_text())['status']=='passed','Interaction geometry has not passed: '+key
            if not (folder/'view-overlay-checks.json').exists():export(folder)
            if not (folder/'composite-browser-check.json').exists():
                subprocess.run([sys.executable,str(Path(__file__).with_name('check_hologram_composite.py')),
                    '--folder',str(folder),'--url','http://127.0.0.1:8766/glass-rollout/coffee/'+key+'/index.html','--embedded'],check=True)
            subprocess.run([sys.executable,str(API/'register_glass_guides.py')],check=True)
            subprocess.run([sys.executable,str(API/'clay_scene_assets.py'),'--out',str(catalog)],check=True)
            subprocess.run([sys.executable,str(API/'publish_glass_batch.py'),'--out',str(catalog)],check=True)
            complete.add(key)
            progress.run()
            print('COFFEE_GUIDE_PUBLISHED',key,len(complete),len(keys),flush=True)
        progress.run()
        if len(complete)<len(keys):time.sleep(5)
    print(json.dumps(dict(status='complete',scenes=sorted(complete))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--catalog',type=Path,required=True);p.add_argument('--scenes');args=p.parse_args();run(args.catalog.resolve(),args.scenes.split(',') if args.scenes else None)
