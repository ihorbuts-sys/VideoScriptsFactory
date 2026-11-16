"""Contact sheets for visual artwork review and structural animation validation."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]/'watercolor'


def sheets(include_approved=False):
    manifest=json.loads((ROOT/'manifest.json').read_text())
    available=[asset for asset in manifest['assets'] if asset['status']=='generated' or (include_approved and asset['status']=='approved')]
    dest=ROOT/'review-pages';dest.mkdir(exist_ok=True)
    pages=[]
    for start in range(0,len(available),12):
        assets=available[start:start+12]
        page=Image.new('RGB',(1280,1440),'#ede9df')
        draw=ImageDraw.Draw(page)
        for i,asset in enumerate(assets):
            original=Path(asset.get('original',asset.get('source')))
            with Image.open(original) as image:
                artwork=image.convert('RGBA')
                artwork.thumbnail((300,420),Image.Resampling.LANCZOS)
            tile=Image.new('RGBA',(300,420),'#f8f5ee')
            tile.alpha_composite(artwork,((300-artwork.width)//2,(420-artwork.height)//2))
            x,y=(i%4)*320,(i//4)*480
            page.paste(tile.convert('RGB'),(x+10,y+10))
            draw.text((x+10,y+437),asset['id'],fill='#334752')
            draw.text((x+10,y+454),asset['status'],fill='#607b8a')
        name=f'page-{start//12+1:02d}.jpg'
        page.save(dest/name,quality=92)
        pages.append(dict(file=name,assets=[asset['id'] for asset in assets]))
    (dest/'index.json').write_text(json.dumps(pages,indent=2)+'\n')
    print(json.dumps(pages))


def approve(ids):
    with (ROOT/'.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        manifest=json.loads((ROOT/'manifest.json').read_text())
        for asset in manifest['assets']:
            if asset['id'] in ids:
                if asset['status'] not in ('generated','approved'):raise ValueError(asset['id'])
                asset.update(status='approved',review='Generated artwork visually reviewed: watercolor sketch style, no mouths, at most two visible hands, visitor-side viewpoint and appropriate subject. Alpha scaling checked separately.')
        temp=ROOT/'.review.tmp';temp.write_text(json.dumps(manifest,indent=2)+'\n');temp.replace(ROOT/'manifest.json')
    print(f'Approved {len(ids)} reviewed artwork groups.')


def validate():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    errors=[]
    artwork_checks=[]
    for asset in manifest['assets']:
        if asset['status']!='approved':errors.append(f'Artwork not approved: {asset["id"]}')
        if not asset.get('artwork'):
            errors.append(f'Missing artwork: {asset["id"]}');continue
        with Image.open(asset['original']) as image:original=np.asarray(image.convert('RGBA'))
        with Image.open(asset['artwork']) as image:adjusted=np.asarray(image.convert('RGBA'))
        exact_rgb=np.array_equal(original[:,:,:3],adjusted[:,:,:3])
        exact_alpha=np.array_equal(((original[:,:,3].astype(np.uint16)+1)//2).astype(np.uint8),adjusted[:,:,3])
        if not exact_rgb or not exact_alpha:errors.append(f'Alpha-only scaling differs: {asset["id"]}')
        artwork_checks.append(dict(id=asset['id'],rgb_preserved=exact_rgb,alpha_scaled_once=exact_alpha))
    animation_checks=[]
    for gid,entry in manifest['guides'].items():
        base=ROOT/'rendered'
        metadata=base/f'{gid}.json'
        animation=base/f'{gid}.png'
        if not metadata.exists() or not animation.exists():errors.append(f'Missing animation: {gid}');continue
        record=json.loads(metadata.read_text())
        with Image.open(animation) as image:
            if not image.is_animated or image.size!=(405,720):errors.append(f'Invalid APNG: {gid}')
            duration=0
            for i in range(image.n_frames):
                image.seek(i)
                duration+=image.info['duration']
                if image.convert('RGBA').getchannel('A').getextrema()[1]>128:errors.append(f'Alpha exceeds 50%: {gid}/{i}')
            if abs(duration/1000-record['seconds'])>.025:errors.append(f'Duration differs: {gid}')
        source=json.loads((ROOT.parent/'templates'/f'{gid}.json').read_text())
        if source['timeline']!=record['camera_timeline']:errors.append(f'Camera path differs: {gid}')
        if entry['move'].startswith('orbit') and record['generated_view_count']<3:errors.append(f'Orbit lacks perspective views: {gid}')
        for suffix in ('_poster.png','_strip.png'):
            if not (base/f'{gid}{suffix}').exists():errors.append(f'Missing preview: {gid}{suffix}')
        animation_checks.append(dict(id=gid,move=entry['move'],seconds=round(duration/1000,3),camera_path_preserved=True,perspective_views=record['generated_view_count']))
    result=dict(artwork_groups=len(manifest['assets']),guides=len(manifest['guides']),steps=manifest['steps'],
                artwork=artwork_checks,animations=animation_checks,errors=errors,
                limits=['No on-device tracking or sensor validation in this artwork/catalog task.',
                        'Static scenarios retain authored still poses; subject action is not measured or fabricated.',
                        'Native scenario ghost polylines and 3D model geometry retain their existing technical form.'])
    (ROOT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'{len(artwork_checks)} artwork groups, {len(animation_checks)} animations, {len(errors)} errors.')
    if errors:raise SystemExit(1)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['sheets','approve','validate'])
    parser.add_argument('ids',nargs='*')
    parser.add_argument('--all',action='store_true')
    args=parser.parse_args()
    if args.action=='sheets':sheets(args.all)
    elif args.action=='approve':approve(args.ids)
    else:validate()
