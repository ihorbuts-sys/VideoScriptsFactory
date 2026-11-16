"""Render newly available generated artwork while generation continues."""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'watercolor'
previous=set()
while True:
    manifest=json.loads((OUT/'manifest.json').read_text())
    available={asset['id'] for asset in manifest['assets'] if asset['status'] in ('generated','approved')}
    if available!=previous:
        subprocess.run([sys.executable,str(HERE/'watercolor_render.py'),'render','--jobs','3'],check=True)
        previous=available
        print(f'Artwork available: {len(available)}/{len(manifest["assets"])}',flush=True)
    if len(available)==len(manifest['assets']):
        break
    time.sleep(10)
