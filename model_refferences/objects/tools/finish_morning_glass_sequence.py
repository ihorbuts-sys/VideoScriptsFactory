"""Assemble and publish the full morning sequence after its last shot passes."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from assemble_morning_glass_sequence import run as assemble
import coffee_glass_progress as progress

BASE=Path(__file__).resolve().parents[3]
OUT=BASE/'catalog/glass-rollout/sequences/cafe-morning-ritual'


def run(catalog):
    deadline=time.monotonic()+3600
    while not (BASE/'catalog/glass-rollout/coffee/work-corner/composite-browser-check.json').exists():
        assert time.monotonic()<deadline,'Final morning shot is not ready'
        time.sleep(5)
    assemble()
    subprocess.run([sys.executable,str(Path(__file__).with_name('check_hologram_composite.py')),
        '--folder',str(OUT),'--url','http://127.0.0.1:8766/glass-rollout/sequences/cafe-morning-ritual/index.html','--embedded'],check=True)
    subprocess.run([sys.executable,str(BASE/'api/register_morning_glass_sequence.py')],check=True)
    subprocess.run([sys.executable,str(BASE/'api/clay_scene_assets.py'),'--out',str(catalog)],check=True)
    progress.run()
    report=dict(status='published',template='cafe-morning-ritual',
        endpoint='/v1/scripts/cafe-morning-ritual/guide-sequence',steps=4,
        full_script_sequence_complete=True,opacity_mode='image_view')
    (OUT/'publication.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--catalog',required=True,type=Path);args=parser.parse_args();run(args.catalog.resolve())
