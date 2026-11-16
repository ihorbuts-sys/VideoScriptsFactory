"""Package native P0 frames without a baked whole-image opacity multiplier."""
import argparse,hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageOps
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'model_refferences/objects/tools'))
from pack_full_frame_apng import pack


def export(folder,destination=None):
    meta=json.loads((folder/'meta.json').read_text());record=meta['record'];count=meta['frame_count']
    assert not meta['probe'] and count==15*(record['durationSec']+record['setupBeatSeconds']+1)
    assert meta['source_surfaces_absent'] and meta['maximum_hands']<=record.get('allowedHands',0) and meta['detailed_people']<=record.get('allowedPeople',0)
    gid=meta['id'];destination=destination or ROOT/'guides/p0/renders';destination.mkdir(parents=True,exist_ok=True)
    masters=folder/'frames';frames=folder/'export_frames';frames.mkdir(exist_ok=True)
    selectors=folder/'selectors';selectors.mkdir(exist_ok=True)
    first=None;changed=False;peak=0;hashes=[]
    for number in range(1,count+1):
        path=frames/f'frame_{number:04d}.png'
        with Image.open(masters/path.name) as original:
            image=original.copy()
            if meta.get('preview_mirrored'):image=ImageOps.mirror(image)
            raw=np.asarray(image);rgb=raw[:,:,:3].astype(float)
            warm=(rgb[:,:,0]>rgb[:,:,1]*1.04)&(rgb[:,:,1]>rgb[:,:,2]*1.08)
            if warm.any():
                mask=Image.fromarray(np.where(warm,raw[:,:,3],0).astype('uint8'))
                blur=mask.filter(ImageFilter.GaussianBlur(1.5 if meta.get('steam_edge_glow') else .65))
                halo=Image.new('RGBA',image.size,(255,202,72,0));halo.putalpha(blur.point(lambda a:round(a*(.28 if meta.get('steam_edge_glow') else .10))))
                image=Image.alpha_composite(halo,image)
            row=meta['camera_samples'][number-1]
            if meta.get('picture_in_picture',False):
                ImageDraw.Draw(image).rounded_rectangle((276,205,393,386),radius=8,outline=(255,255,255,35),width=1)
            if row['u']==1 and meta.get('triangle_markers'):
                dots=ImageDraw.Draw(image)
                for x,y in meta['triangle_markers']:
                    if 3<=x<402 and 3<=y<717:dots.ellipse((x-3,y-3,x+3,y+3),fill=(255,255,255,35))
            # Keep transparent pixels neutral as well as fully transparent.
            # Some image inspectors display RGB even where alpha is zero.
            normalized=np.array(image);normalized[normalized[:,:,3]==0]=0
            image=Image.fromarray(normalized)
            image.save(path)
            assert image.size==(405,720) and image.mode=='RGBA'
            rgba=np.asarray(image)
            assert (rgba[:,:,3]==0).any() and (rgba[:,:,3]>0).any()
            assert (rgba[:,:,3]>0).mean()<.35
            peak=max(peak,int(rgba[:,:,3].max()))
            if first is None:first=rgba.copy()
            elif not np.array_equal(first,rgba):changed=True
            hashes.append(hashlib.sha256(rgba.tobytes()).hexdigest())
            image.resize((120,213),Image.Resampling.LANCZOS).save(selectors/path.name)
    assert len(set(hashes[:8]))==1 and len(set(hashes[-7:]))==1
    # The required target frame opens and closes the guide.
    assert hashes[0]==hashes[-1],('Target differs at the end',gid)
    hero=folder/'hero-target.png'
    if hero.exists():
        alpha=np.asarray(Image.open(hero))[:,:,3];ys,xs=np.where(alpha>8)
        assert len(ys) and ys.min()>=round(720*.28) and ys.max()<round(720*.65),(gid,int(ys.min()),int(ys.max()))
    with Image.open(frames/'frame_0001.png') as image:image.save(destination/(gid+'_poster.png'))
    pack(frames,destination/(gid+'.png'),count,15,plays=1)
    pack(selectors,destination/(gid+'_selector.png'),count,15,plays=0)
    for filename,size in [(gid+'.png',(405,720)),(gid+'_selector.png',(120,213))]:
        with Image.open(destination/filename) as animation:
            assert animation.n_frames==count and animation.size==size
            seconds=0
            for n in range(count):animation.seek(n);seconds+=animation.info['duration']/1000
            assert abs(seconds-meta['expected_seconds'])<1/15
            animation.seek(0)
            if size==(405,720):assert np.array_equal(np.array(animation.convert('RGBA')),first)
    checks=dict(id=gid,status='passed',frames=count,seconds=meta['expected_seconds'],durationSec=record['durationSec'],
        setupBeatSeconds=record['setupBeatSeconds'],alphaFactor=1,global_opacity_baked=False,maximum_alpha=peak,
        target_first_and_last_identical=True,poster_equals_frame_zero=True,encoded_frames_preserved=True,
        selector_size=[120,213],animation_size=[405,720],initial_hold_frames=8,final_hold_frames=7,
        visible_motion=changed,hero_pixel_band_checked=hero.exists(),maximum_hands=meta['maximum_hands'],
        detailed_people=meta['detailed_people'],silhouettes=meta['silhouettes'],fixed_lens=True,fixed_lighting=True,
        local_yellow_edge_glow=bool(meta.get('light_cues')),steam_edge_glow=bool(meta.get('steam_edge_glow')),
        glow_from_native_yellow_contours_only=True,triangle_markers=meta.get('triangle_markers',[]),
        sha256=hashlib.sha256((destination/(gid+'.png')).read_bytes()).hexdigest())
    if meta.get('detailed_people'):
        checks.update(character=meta['character'],preview_mirrored=meta['preview_mirrored'],
            facial_animation=False,hero_region=meta['hero_region'])
    (folder/'export-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    (destination/(gid+'_checks.json')).write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks),flush=True)
    return checks


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--out',type=Path)
    a=p.parse_args();export(a.folder,a.out)
