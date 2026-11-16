"""Save generated originals, scale alpha once, and keep generation provenance."""
import argparse
import fcntl
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]/'watercolor'


def accept(asset_id, source):
    with (ROOT/'.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = json.loads((ROOT/'manifest.json').read_text())
        if manifest.get('workflow_status')=='rejected':
            raise SystemExit('Generation batch was rejected; do not accept more artwork into it.')
        entry = next(asset for asset in manifest['assets'] if asset['id']==asset_id)
        original = ROOT/'originals'/f'{asset_id}.png'
        output = ROOT/'artwork'/f'{asset_id}.png'
        if original.exists() and entry['status'] in ('generated','approved'):
            raise SystemExit('Already accepted; preserve it before explicitly replacing.')
        shutil.copy2(source, original)
        with Image.open(original) as image:
            if image.mode!='RGBA':
                raise ValueError('Generated artwork must have an alpha channel.')
            output_image = image.copy()
            output_image.putalpha(image.getchannel('A').point([(value+1)//2 for value in range(256)]))
            output_image.save(output, optimize=True)
            size = list(image.size)
        entry.update(status='generated', source=str(Path(source).resolve()),
                     original=str(original.resolve()), artwork=str(output.resolve()), size=size,
                     original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                     alpha_factor=.5, review='Awaiting visual review; generated image, alpha scaled exactly once.')
        temporary = ROOT/'.manifest.tmp'
        temporary.write_text(json.dumps(manifest,indent=2)+'\n')
        temporary.replace(ROOT/'manifest.json')
        (ROOT/'originals'/f'{asset_id}-prompt.txt').write_text(entry['prompt']+'\n')
    print(f'Saved {asset_id}: {size}, alpha x0.5.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('id')
    parser.add_argument('source')
    args=parser.parse_args()
    accept(args.id,args.source)
