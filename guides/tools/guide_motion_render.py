"""Sequence generated guide viewpoints and export alpha only in a final batch.

Illustrations come exclusively from image generation. This file crops atlas cells,
interpolates them, and adds the existing fixed review viewfinder when requested.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import math
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import stable_zoom
import local_motion

GUIDES=Path(__file__).resolve().parents[1]
ROOT=GUIDES.parent
OUT=GUIDES/'watercolor_motion'
W,H,FPS=405,720,15
STAGE_VERSION=2
REVIEWED={'approved','keyframes_reviewed'}


def read_manifest():
    return json.loads((OUT/'manifest.json').read_text())


def edit_entry(gid,changes):
    with (OUT/'.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        manifest=read_manifest()
        next(e for e in manifest['guides'] if e['id']==gid).update(changes)
        temporary=OUT/'.render.tmp'
        temporary.write_text(json.dumps(manifest,indent=2)+'\n')
        temporary.replace(OUT/'manifest.json')


def atlas_cells(entry):
    """Use one common scale and grid. Never normalize each subject's own bounds."""
    source=Image.open(entry['original']).convert('RGBA')
    if entry.get('single_pose'):
        scale=min(W/source.width,H/source.height)
        resized=source.resize((round(source.width*scale),round(source.height*scale)),Image.Resampling.LANCZOS)
        view=Image.new('RGBA',(W,H))
        view.alpha_composite(resized,((W-resized.width)//2,(H-resized.height)//2))
        return [view.copy() for _ in range(6)],dict(single_pose=True,common_scale=True)
    override=entry.get('grid_override')
    if override:
        origins=override['origins'];cw,ch=override['cell_size']
    else:
        alpha=np.asarray(source.getchannel('A'),dtype=np.float32)
        density=alpha.mean(axis=1)
        smooth=np.convolve(density,np.ones(9)/9,mode='same')
        cuts=[]
        for fraction in (1/3,2/3):
            lo=int(source.height*(fraction-.08));hi=int(source.height*(fraction+.08))
            area=smooth[lo:hi];low=area.min()+max(1,(np.percentile(area,80)-area.min())*.07)
            indices=np.where(area<=low)[0]+lo
            # Select the transparent gutter nearest the expected row boundary.
            runs=np.split(indices,np.where(np.diff(indices)>1)[0]+1)
            run=min(runs,key=lambda group:abs(group.mean()-source.height*fraction))
            cuts.append(float(run.mean()))
        ch=cuts[1]-cuts[0];cw=source.width/2
        y0=cuts[0]-ch
        origins=[(col*cw,y0+row*ch) for row in range(3) for col in range(2)]
    views=[]
    for index,(x,y) in enumerate(origins):
        if entry['id']=='cup_eye_orbitr_cc':
            centers=[(230,207),(225,207),(236,207),(230,207),(236,207),(234,207)]
            cx,cy=centers[index];scale=.86
            cell=source.crop((x,y,x+cw,y+ch))
            transform=(1/scale,0,cx-W/(2*scale),0,1/scale,cy-345/scale)
            view=cell.transform((W,H),Image.Transform.AFFINE,transform,resample=Image.Resampling.BICUBIC)
        else:
            scale=min(W/cw,(H-36)/ch)
            # A shared affine transform preserves all inter-frame size/position changes.
            transform=(1/scale,0,x-(W/scale-cw)/2,0,1/scale,y-(H/scale-ch)/2)
            view=source.transform((W,H),Image.Transform.AFFINE,transform,resample=Image.Resampling.BICUBIC)
            # Neighboring atlas cells must never bleed into this virtual view.
            mask=Image.new('L',(W,H));draw=ImageDraw.Draw(mask)
            dx=(W-cw*scale)/2;dy=(H-ch*scale)/2
            draw.rectangle((math.ceil(dx),math.ceil(dy),math.floor(W-dx)-1,math.floor(H-dy)-1),fill=255)
            view.putalpha(Image.fromarray(np.minimum(np.asarray(view.getchannel('A')),np.asarray(mask))))
        views.append(view)
    if 'hold_cell' in entry:views=[views[entry['hold_cell']].copy() for _ in range(6)]
    if 'frame_sequence' in entry:views=[views[i].copy() for i in entry['frame_sequence']]
    return views,dict(origins=origins,cell_size=[cw,ch],common_scale=True,hold_cell=entry.get('hold_cell'),frame_sequence=entry.get('frame_sequence'))


def background(image):
    result=Image.new('RGBA',image.size,'#23343e');result.alpha_composite(image)
    return result.convert('RGB')


def stage(gids=None):
    manifest=read_manifest();made=0
    for entry in manifest['guides']:
        if gids and entry['id'] not in gids:continue
        if not entry.get('original'):continue
        folder=OUT/'frames'/entry['id'];folder.mkdir(exist_ok=True)
        source_hash=hashlib.sha256(Path(entry['original']).read_bytes()).hexdigest()
        rendering=entry.get('rendering',{})
        rendering_hash=hashlib.sha256(json.dumps(rendering,sort_keys=True).encode()).hexdigest()
        grid_path=folder/'grid.json'
        if grid_path.exists():
            previous=json.loads(grid_path.read_text())
            if previous.get('stage_version')==STAGE_VERSION and previous.get('source_sha256')==source_hash and previous.get('rendering_sha256')==rendering_hash and previous.get('hold_cell')==entry.get('hold_cell') and previous.get('single_pose',False)==entry.get('single_pose',False) and previous.get('frame_sequence')==entry.get('frame_sequence'):
                continue
        method=rendering.get('method')
        if method=='single_source_crop':
            master=Image.open(rendering['master']).convert('RGBA')
            views=[stable_zoom.frame_at(master,entry,t,eased) for t in entry['keyframe_times']]
            grid=dict(single_pose=entry.get('single_pose',False),common_scale=True,method=method)
        elif method=='layered_animation':
            images=local_motion.load(entry)
            views=[local_motion.frame_at(images,entry,t,eased) for t in entry['keyframe_times']]
            grid=dict(single_pose=entry.get('single_pose',False),common_scale=True,method=method)
        else:views,grid=atlas_cells(entry)
        grid['source_sha256']=source_hash
        grid['rendering_sha256']=rendering_hash
        grid['stage_version']=STAGE_VERSION
        for i,view in enumerate(views):view.save(folder/f'{i}.png')
        sheet=Image.new('RGB',(W*6,H),'#23343e')
        for i,view in enumerate(views):sheet.paste(background(view),(i*W,0))
        sheet.resize((1080,320),Image.Resampling.LANCZOS).save(folder/'keyframes.jpg',quality=90)
        (folder/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')
        made+=1
    print(f'Staged {made} six-view sets. Generated alpha is unchanged.')


def contact():
    entries=[e for e in read_manifest()['guides'] if e['status'] not in REVIEWED and (OUT/'frames'/e['id']/'keyframes.jpg').exists()]
    folder=OUT/'review';folder.mkdir(exist_ok=True)
    for stale in folder.glob('keyframes-*.jpg'):stale.unlink()
    (folder/'queue.json').write_text(json.dumps([dict(id=e['id'],description=e['description'],status=e['status']) for e in entries],indent=2)+'\n')
    for start in range(0,len(entries),5):
        group=entries[start:start+5]
        sheet=Image.new('RGB',(1200,len(group)*400),'#15242d');draw=ImageDraw.Draw(sheet)
        for row,entry in enumerate(group):
            draw.text((12,row*400+8),entry['id']+' | '+entry['status'],fill='#ffffff')
            # One complete strip per guide makes direction and scale easy to compare.
            im=Image.open(OUT/'frames'/entry['id']/'keyframes.jpg').resize((1200,356))
            sheet.paste(im,(0,row*400+30))
        sheet.save(folder/f'keyframes-{start//5+1:02d}.jpg',quality=91)
    print(f'{len(entries)} guides in {math.ceil(len(entries)/5)} functional review sheets.')


def pair_flow(a,b):
    def gray(image):
        rgba=np.asarray(image,dtype=np.float32)
        return np.clip((255-rgba[:,:,:3].mean(axis=2))*.6+rgba[:,:,3]*.5,0,255).astype(np.uint8)
    ga,gb=gray(a),gray(b)
    return (cv2.calcOpticalFlowFarneback(ga,gb,None,.5,5,35,5,7,1.5,0),
            cv2.calcOpticalFlowFarneback(gb,ga,None,.5,5,35,5,7,1.5,0))


def interpolate(a,b,flows,progress):
    if flows is None:return a.copy()
    if progress<=0:return a.copy()
    if progress>=1:return b.copy()
    aa,bb=np.asarray(a,dtype=np.float32),np.asarray(b,dtype=np.float32)
    aa[:,:,:3]*=aa[:,:,3:4]/255;bb[:,:,:3]*=bb[:,:,3:4]/255
    yy,xx=np.indices(aa.shape[:2],dtype=np.float32)
    forward,reverse=flows
    left=cv2.remap(aa,xx-forward[:,:,0]*progress,yy-forward[:,:,1]*progress,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    right=cv2.remap(bb,xx-reverse[:,:,0]*(1-progress),yy-reverse[:,:,1]*(1-progress),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    mixed=left*(1-progress)+right*progress
    mixed[:,:,:3]=np.divide(mixed[:,:,:3]*255,mixed[:,:,3:4],out=np.zeros_like(mixed[:,:,:3]),where=mixed[:,:,3:4]>0)
    return Image.fromarray(np.clip(mixed,0,255).astype(np.uint8))


def eased(value,ease):
    p=max(0,min(1,value))
    if ease=='inOutSine':return (1-math.cos(math.pi*p))/2
    if ease=='inOutExpo':
        if p in (0,1):return p
        return 2**(20*p-10)/2 if p<.5 else (2-2**(-20*p+10))/2
    return p


def position_at(entry,t):
    position=0
    for window in entry['windows']:
        if t<window['start']:break
        indices=window['indices']
        position=indices[0]+(indices[-1]-indices[0])*eased((t-window['start'])/(window['end']-window['start']),window['ease'])
    return position


def alpha50(image):
    result=image.copy()
    result.putalpha(image.getchannel('A').point([(v+1)//2 for v in range(256)]))
    assert np.array_equal(np.asarray(image)[:,:,:3],np.asarray(result)[:,:,:3])
    return result


def viewfinder():
    source=ROOT.parent/'codex_design_study/render_guided_reviews.py'
    spec=importlib.util.spec_from_file_location('fixed_review_sights',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    frame_paths,composition=module.geometry()
    return module.layer(composition+frame_paths)


def render_entry(entry,folder,phase):
    fixed_ui=viewfinder()
    gid=entry['id'];folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    stable=entry.get('rendering',{}).get('method')=='single_source_crop'
    layered=entry.get('rendering',{}).get('method')=='layered_animation'
    if stable:
        master=Image.open(entry['rendering']['master']).convert('RGBA')
        assert hashlib.sha256(Path(entry['rendering']['master']).read_bytes()).hexdigest()==entry['rendering']['master_sha256']
    elif layered:
        images=local_motion.load(entry)
    else:
        views=[Image.open(OUT/'frames'/gid/f'{i}.png').convert('RGBA') for i in range(6)]
        flows=[None if np.array_equal(np.asarray(a),np.asarray(b)) else pair_flow(a,b) for a,b in zip(views,views[1:])]
    raw=[]
    for index in range(math.ceil(entry['duration']*FPS)):
        t=index/FPS
        if stable:frame=stable_zoom.frame_at(master,entry,t,eased)
        elif layered:frame=local_motion.frame_at(images,entry,t,eased)
        else:
            position=position_at(entry,t);segment=min(4,int(position))
            frame=interpolate(views[segment],views[segment+1],flows[segment],position-segment)
        if t>entry['duration']-entry['fade']:
            fade=max(0,(entry['duration']-t)/entry['fade'])
            frame.putalpha(frame.getchannel('A').point(lambda v:round(v*fade)))
        raw.append(frame)
    # Compose every frame first; then apply alpha once to this completed clip.
    for name in ('guide','guide_with_guides'):
        exported=[alpha50(frame if name=='guide' else Image.alpha_composite(frame,fixed_ui)) for frame in raw]
        exported[0].save(folder/f'{name}.png',save_all=True,append_images=exported[1:],duration=1000/FPS,loop=0,disposal=0,blend=0)
    alpha50(raw[0]).save(folder/'poster.png')
    alpha50(Image.alpha_composite(raw[0],fixed_ui)).save(folder/'poster_with_guides.png')
    samples=[min(len(raw)-1,round(t*FPS)) for t in entry['keyframe_times']]
    strip=Image.new('RGB',(1080,320),'#23343e')
    for col,index in enumerate(samples):
        preview=background(alpha50(Image.alpha_composite(raw[index],fixed_ui)))
        strip.paste(preview.resize((180,320),Image.Resampling.LANCZOS),(180*col,0))
    strip.save(folder/'strip.png')
    record={key:entry[key] for key in ('id','description','source_timeline','source_live_steps','camera_spec','windows','keyframe_times','review')}
    record.update(fps=FPS,samples=len(raw),duration=len(raw)/FPS,alpha_factor=.5,colors_preserved=True,
                  alpha_stage='After all frames of this clip are composed',phase=phase,
                  source_sha256=hashlib.sha256(Path(entry['original']).read_bytes()).hexdigest(),
                  method='Single-source affine camera window; no pose interpolation' if stable else ('Rigid painted cutouts, occlusion masks and multiplane motion' if layered else 'Generated viewpoints interpolated using bidirectional optical flow'),device_validation='Not performed')
    if stable or layered:record['rendering']=entry['rendering']
    (folder/'guide.json').write_text(json.dumps(record,indent=2)+'\n')
    print(f'Exported {gid}: {len(raw)} frames, alpha 0.5 ({phase}).',flush=True)
    return gid


def preview_job(entry):
    cv2.setNumThreads(1)
    return render_entry(entry,ROOT/'catalog/animations'/entry['id'],'catalog preview; full guide set incomplete')


def previews(gids=None):
    entries=[e for e in read_manifest()['guides'] if e['status'] in REVIEWED and (not gids or e['id'] in gids)]
    stage([e['id'] for e in entries])
    with ProcessPoolExecutor(max_workers=2) as pool:
        done=list(pool.map(preview_job,entries))
    if gids:
        existing=ROOT/'catalog/animations/index.json'
        prior=set(json.loads(existing.read_text())['guides']) if existing.exists() else set()
        valid={e['id'] for e in read_manifest()['guides'] if e['status'] in REVIEWED}
        done=sorted((prior|set(done))&valid)
    index=dict(count=len(done),guides=done,alpha_factor=.5,phase='reviewed subset previews; not full-set publication')
    (ROOT/'catalog/animations/index.json').write_text(json.dumps(index,indent=2)+'\n')
    print(f'{len(done)} playable catalog previews ready.',flush=True)


def finalize():
    manifest=read_manifest()
    pending=[e['id'] for e in manifest['guides'] if e['status'] not in REVIEWED]
    if pending:raise SystemExit(f'Final opacity batch waits for all generated keyframes and functional reviews: {len(pending)} remain.')
    stage()
    for entry in manifest['guides']:
        render_entry(entry,OUT/'rendered'/entry['id'],'complete-set export')
    (OUT/'export-complete.json').write_text(json.dumps(dict(count=len(manifest['guides']),alpha_factor=.5,fps=FPS),indent=2)+'\n')


def publish():
    manifest=read_manifest();completion=OUT/'export-complete.json'
    if not completion.exists():raise SystemExit('Complete the final batch before publishing.')
    if any(e['status'] not in REVIEWED for e in manifest['guides']):raise SystemExit('Functional reviews are incomplete.')
    archive=GUIDES/'overlays/archive-pre-watercolor-motion'
    archive.mkdir(exist_ok=True)
    catalog=ROOT/'catalog/strips';catalog.mkdir(exist_ok=True)
    for entry in manifest['guides']:
        gid=entry['id'];source=OUT/'rendered'/gid
        for destination in (GUIDES/'overlays/schematic'/f'{gid}.png',GUIDES/'overlays/schematic'/f'{gid}_strip.png'):
            backup=archive/destination.name
            if destination.exists() and not backup.exists():shutil.copy2(destination,backup)
        shutil.copy2(source/'guide.png',GUIDES/'overlays/schematic'/f'{gid}.png')
        shutil.copy2(source/'strip.png',GUIDES/'overlays/schematic'/f'{gid}_strip.png')
        shutil.copy2(source/'strip.png',catalog/f'{gid}.png')
    print(f'Published {len(manifest["guides"])} guide APNGs and catalog strips. Previous exports archived.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['stage','contact','previews','finalize','publish'])
    parser.add_argument('--id',action='append')
    args=parser.parse_args()
    if args.action=='stage':stage(args.id)
    elif args.action=='contact':contact()
    elif args.action=='previews':previews(args.id)
    elif args.action=='finalize':finalize()
    else:publish()
