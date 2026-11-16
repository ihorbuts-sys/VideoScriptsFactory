"""Animate generated watercolor pixels using the existing guide camera timelines.

No illustration is drawn, traced or replaced by procedural shapes. Orbit views
come from generated multi-view sheets and are interpolated by optical flow.
"""
import argparse
import concurrent.futures
import hashlib
import html
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

GUIDES = Path(__file__).resolve().parents[1]
ROOT = GUIDES.parent
OUT = GUIDES/'watercolor'
LOCA = ROOT.parents[3]
sys.path.insert(0, str(LOCA/'.claude/skills/shot-overlay/scripts'))
import render as legacy

W, H, FPS = 405, 720, 15
RENDERER_REVISION = 3


def load_manifest():
    return json.loads((OUT/'manifest.json').read_text())


def fit_views(asset):
    with Image.open(asset['artwork']) as image:
        source = image.convert('RGBA')
    if asset['kind']!='orbit-sheet':
        return [source]
    # A sheet is one generated animation asset, with no more than zero hands.
    views = [source.crop((round(i*source.width/3), 0, round((i+1)*source.width/3), source.height)) for i in range(3)]
    normalized = []
    for view in views:
        alpha = view.getchannel('A').point(lambda value:255 if value>16 else 0)
        box = alpha.getbbox()
        if not box:
            raise ValueError(f'Empty orbit cell: {asset["id"]}')
        view = view.crop(box)
        view.thumbnail((450, 450), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (540, 540))
        canvas.alpha_composite(view, ((540-view.width)//2, (540-view.height)//2))
        normalized.append(canvas)
    return normalized


def flow_pair(a, b):
    import cv2
    # Registration uses luminance and alpha, not the display backdrop.
    def gray(image):
        rgba = np.asarray(image).astype(np.float32)
        alpha = rgba[:,:,3]/128
        pigment = (255-np.mean(rgba[:,:,:3],axis=2))*.55+100
        return np.clip(pigment*alpha,0,255).astype(np.uint8)
    ga, gb = gray(a), gray(b)
    forward = cv2.calcOpticalFlowFarneback(ga,gb,None,.5,5,35,5,7,1.5,0)
    backward = cv2.calcOpticalFlowFarneback(gb,ga,None,.5,5,35,5,7,1.5,0)
    return forward, backward


def morph(a, b, flows, progress):
    import cv2
    if progress<=0:return a
    if progress>=1:return b
    aa, bb = np.asarray(a).astype(np.float32), np.asarray(b).astype(np.float32)
    aa[:,:,:3]*=aa[:,:,3:4]/255
    bb[:,:,:3]*=bb[:,:,3:4]/255
    yy, xx = np.indices(aa.shape[:2],dtype=np.float32)
    forward, backward = flows
    left = cv2.remap(aa,xx-forward[:,:,0]*progress,yy-forward[:,:,1]*progress,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    right = cv2.remap(bb,xx-backward[:,:,0]*(1-progress),yy-backward[:,:,1]*(1-progress),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    mixed=left*(1-progress)+right*progress
    mixed[:,:,:3]=np.divide(mixed[:,:,:3]*255,mixed[:,:,3:4],out=np.zeros_like(mixed[:,:,:3]),where=mixed[:,:,3:4]>0)
    return Image.fromarray(np.clip(mixed,0,255).astype(np.uint8))


def world_rect(scene, asset, image, entry):
    track=scene.tracks['cam']
    # Place the complete artwork in the widest authored view. A pull-out must
    # start on a detail and reveal the complete subject, not shrink a complete
    # picture that was already visible in its first frame.
    cx, cy, scale=min((value for _,value,_ in track),key=lambda value:value[2])
    width,height=W/scale,H/scale
    if asset['kind']=='panorama':
        if entry['transition']=='whip' and len(track)>2:
            track=track[:-1]
        xs=[value[0]-W/value[2]/2 for _,value,_ in track]
        xe=[value[0]+W/value[2]/2 for _,value,_ in track]
        ys=[value[1]-H/value[2]/2 for _,value,_ in track]
        ye=[value[1]+H/value[2]/2 for _,value,_ in track]
        iw=max(xe)-min(xs)
        ih=iw*image.height/image.width
        return (min(xs), (min(ys)+max(ye)-ih)/2, iw, ih)
    ratio=image.width/image.height
    ih=height*.94
    iw=ih*ratio
    if iw>width*.94:
        iw=width*.94;ih=iw/ratio
    focus_y=.38 if asset['family']=='selfie' else .5
    if asset['family']=='bag':focus_y=.58
    if asset['id']=='cup-cup-high':focus_y=.70
    if asset['id']=='cup-pour-eye-level':focus_y=.70
    focus=asset.get('focus',[.5,focus_y])
    return (cx-iw*focus[0],cy-ih*focus[1],iw,ih)


def transform(image, rect, camera):
    x,y,width,height=rect
    cx,cy,scale=camera
    # PIL expects output-to-input coordinates. No new artwork is constructed.
    coefficients=(image.width/(width*scale),0,(cx-W/(2*scale)-x)*image.width/width,
                  0,image.height/(height*scale),(cy-H/(2*scale)-y)*image.height/height)
    frame=image.transform((W,H),Image.Transform.AFFINE,coefficients,resample=Image.Resampling.BICUBIC)
    frame.putalpha(frame.getchannel('A').point(lambda value:min(value,128)))
    return frame


def render_guide(job):
    gid,entry,asset=job
    dest=OUT/'rendered';dest.mkdir(exist_ok=True)
    metadata=dest/f'{gid}.json'
    asset_hash=hashlib.sha256(Path(asset['artwork']).read_bytes()).hexdigest()
    revision=RENDERER_REVISION if entry['move'].startswith('orbit') or (asset['kind']=='panorama' and entry['transition']=='whip') else 2
    if metadata.exists():
        cached=json.loads(metadata.read_text())
        if cached.get('artwork_sha256')==asset_hash and cached.get('renderer_revision')==revision:
            return gid,'cached'
    data=json.loads((GUIDES/'templates'/f'{gid}.json').read_text())
    scene=legacy.Scene(data,scale=.75,fps=FPS)
    views=fit_views(asset)
    if not entry['move'].startswith('orbit'):
        views=views[:1]
    if entry['move']=='orbit-left':views=list(reversed(views))
    flows=[flow_pair(a,b) for a,b in zip(views,views[1:])]
    rect=world_rect(scene,asset,views[0],entry)
    times=[key['t'] for key in data['timeline']]
    motion_start=times[1] if len(times)>2 else .6
    motion_end=times[-2] if len(times)>3 else min(scene.duration-1,motion_start+2)
    frames=[]
    for index in range(math.ceil(scene.duration*FPS)):
        t=index/FPS
        image=views[0]
        if len(views)>1:
            progress=max(0,min(1,(t-motion_start)/max(.1,motion_end-motion_start)))
            progress=legacy.EASE['inOutSine'](progress)*(len(views)-1)
            segment=min(len(views)-2,int(progress))
            image=morph(views[segment],views[segment+1],flows[segment],progress-segment)
        camera=scene.sample(scene.tracks['cam'],t,'cam')
        frame=transform(image,rect,camera)
        if scene.fade>0 and t>scene.duration-scene.fade:
            factor=max(0,(scene.duration-t)/scene.fade)
            frame.putalpha(frame.getchannel('A').point(lambda value:round(value*factor)))
        frames.append(frame)
    # True RGBA APNG keeps watercolor grain and its translucent paint fringes.
    frames[0].save(dest/f'{gid}.png',save_all=True,append_images=frames[1:],
                   duration=1000/FPS,loop=0,disposal=0,blend=0,optimize=True)
    poster_index=min(len(frames)-1,round(motion_start*FPS))
    frames[poster_index].save(dest/f'{gid}_poster.png')
    choices=[round(i*(len(frames)-1-round(scene.fade*FPS))/5) for i in range(6)]
    sheet=Image.new('RGB',(1080,320),'#e9e5db')
    for col,index in enumerate(choices):
        background=Image.new('RGBA',(W,H),'#eee9df')
        background.alpha_composite(frames[index])
        sheet.paste(background.convert('RGB').resize((180,320),Image.Resampling.LANCZOS),(col*180,0))
    sheet.save(dest/f'{gid}_strip.png')
    record=dict(id=gid,asset=asset['id'],artwork_sha256=asset_hash,renderer_revision=revision,
                fps=FPS,frames=len(frames),seconds=round(len(frames)/FPS,3),
                camera_timeline=data['timeline'],image_world_rect=rect,
                angle=entry['angle'],move=entry['move'],transition=entry['transition'],
                generated_view_count=len(views),alpha_scaled_once=.5,
                foreground_action='Authored still pose; scenario timing retained.' if entry['move']=='static' else None,
                orbit_interpolation='Generated perspectives with bidirectional optical flow' if len(views)>1 else None,
                notes=asset.get('adaptation',''))
    metadata.write_text(json.dumps(record,indent=2)+'\n')
    return gid,f'{len(frames)} frames'


def render_available(jobs=3):
    manifest=load_manifest()
    if manifest.get('workflow_status')=='rejected':
        raise SystemExit('This batch was rejected. Redesign one guide from its description first.')
    assets={asset['id']:asset for asset in manifest['assets']}
    work=[(gid,entry,assets[entry['asset']]) for gid,entry in manifest['guides'].items()
          if assets[entry['asset']]['status'] in ('generated','approved')]
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        for gid,result in executor.map(render_guide,work):
            if result!='cached':print(gid,result,flush=True)
    gallery()


def gallery():
    manifest=load_manifest()
    assets={asset['id']:asset for asset in manifest['assets']}
    cards=[]
    ready=0
    for gid,entry in manifest['guides'].items():
        if assets[entry['asset']]['status'] not in ('generated','approved'):
            continue
        file=OUT/'rendered'/f'{gid}.png'
        if not file.exists():continue
        ready+=1
        cards.append(f'<article data-search="{html.escape(gid)}"><h2>{html.escape(gid)}</h2>'
                     f'<div class="stage"><img class="art" loading="lazy" src="rendered/{gid}_poster.png" data-poster="rendered/{gid}_poster.png" data-animation="rendered/{gid}.png" alt="{html.escape(gid)}">'
                     '<img class="composition" src="composition.svg" alt=""><img class="finder" src="viewfinder.svg" alt=""></div>'
                     f'<p>{entry["angle"]} / {entry["move"]}</p><button class="play" aria-pressed="false">Play</button><a href="rendered/{gid}_strip.png">Six frames</a> '
                     f'<a href="rendered/{gid}.png" download>APNG</a></article>')
    # These are existing viewfinder UI graphics, not generated subject artwork.
    design=ROOT.parent/'codex_design_study'
    for filename in ('viewfinder.svg','composition.svg'):
        source=design/filename
        if source.exists():shutil.copy2(source,OUT/filename)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Watercolor camera guides</title>
<style>body{background:#f0ece3;color:#34434b;font:14px system-ui;max-width:1600px;margin:auto;padding:30px}h1{font-weight:500}header p{max-width:800px;line-height:1.6}button,input{font:inherit;padding:8px 12px;margin:4px;border:1px solid #9bafb9;border-radius:5px;background:transparent;color:inherit}.grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px;margin-top:24px}article{min-width:0}h2{font-size:12px;overflow-wrap:anywhere;min-height:32px;font-weight:500}.stage{position:relative;aspect-ratio:9/16;background:#f9f6f0;border:1px solid #c4cbc8;border-radius:7px;overflow:hidden}.stage img{position:absolute;inset:0;width:100%;height:100%}.composition,.finder{pointer-events:none}.composition{opacity:.6}body.dark .stage{background:#293943}body.caught .art{filter:sepia(1) saturate(4) hue-rotate(355deg)}a{color:#476f86;font-size:12px;margin-right:10px}input{min-width:300px}@media(max-width:1000px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:600px){body{padding:16px}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}input{min-width:200px}}</style>
<header><h1>Watercolor camera guides</h1>'''
    page+=f'<p>{ready} of {manifest["guide_count"]} animations rendered. Generated monochrome sketches with watercolor spill, no mouths, two hands maximum and 50% opacity saved in the pixels. Fixed viewfinder graphics are a separate review layer.</p>'
    page+='''<button id="bg">Light / dark</button><button id="caught">Preview caught tint</button><input id="search" type="search" placeholder="Find a guide" aria-label="Find a guide"><p>Choose Play to inspect a camera path. The caught control previews color feedback only; it is not live detection.</p></header><main class="grid">'''
    page+='\n'.join(cards)
    page+='''</main><script>document.getElementById('bg').onclick=()=>document.body.classList.toggle('dark');document.getElementById('caught').onclick=()=>document.body.classList.toggle('caught');document.getElementById('search').oninput=event=>document.querySelectorAll('article').forEach(card=>card.hidden=!card.dataset.search.includes(event.target.value.toLowerCase()));document.querySelectorAll('.play').forEach(button=>button.onclick=()=>{const wasPlaying=button.getAttribute('aria-pressed')==='true';document.querySelectorAll('.play').forEach(other=>{const art=other.closest('article').querySelector('.art');art.src=art.dataset.poster;other.textContent='Play';other.setAttribute('aria-pressed','false');});if(!wasPlaying){const art=button.closest('article').querySelector('.art');art.src=art.dataset.animation;button.textContent='Pause';button.setAttribute('aria-pressed','true');}});</script></html>'''
    (OUT/'index.html').write_text(page)
    print(f'Gallery: {ready}/{manifest["guide_count"]} guides.',flush=True)


def publish():
    manifest=load_manifest()
    if manifest.get('workflow_status')=='rejected':
        raise SystemExit('Rejected batch cannot be published.')
    missing=[gid for gid in manifest['guides'] if not (OUT/'rendered'/f'{gid}.png').exists()]
    if missing:raise SystemExit(f'Render all guides before publishing: {len(missing)} missing.')
    unreviewed=[asset['id'] for asset in manifest['assets'] if asset['status']!='approved']
    if unreviewed:raise SystemExit(f'Artwork must be visually approved first: {len(unreviewed)} assets.')
    archive=OUT/'previous-schematic';archive.mkdir(exist_ok=True)
    for gid in manifest['guides']:
        for filename in (f'{gid}.png',f'{gid}_strip.png'):
            target=GUIDES/'overlays/schematic'/filename
            previous=archive/filename
            if target.exists() and not previous.exists():shutil.copy2(target,previous)
            shutil.copy2(OUT/'rendered'/filename,target)
        shutil.copy2(OUT/'rendered'/f'{gid}_strip.png',ROOT/'catalog/strips'/f'{gid}.png')
    print(f'Published {len(manifest["guides"])} reviewed watercolor APNGs and strips.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['render','gallery','publish'])
    parser.add_argument('--jobs',type=int,default=3)
    args=parser.parse_args()
    if args.action=='render':render_available(args.jobs)
    elif args.action=='gallery':gallery()
    else:publish()
