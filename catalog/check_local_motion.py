"""Check exported media, deterministic motion, opacity and source preservation."""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageSequence

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'guides/tools'))
import guide_motion_render as render
import local_motion
import stable_zoom


def main():
    manifest=render.read_manifest();entries={e['id']:e for e in manifest['guides']}
    ready=json.loads((HERE/'animations/index.json').read_text())['guides']
    batch=set(json.loads((local_motion.LOCAL/'guide-ids.json').read_text()))
    hashes=json.loads((ROOT/'guides/watercolor/input_hashes.json').read_text())
    changed=[p for p,h in hashes.items() if not (ROOT/p).exists() or local_motion.digest(ROOT/p)!=h]
    assert not changed,changed
    missing=[]
    for page in ('animations.html','catalog.html'):
        for path in re.findall(r'(?:src|data-animation|data-poster)="([^"]+)"',(HERE/page).read_text()):
            if not (HERE/path).exists():missing.append([page,path])
    assert not missing,missing
    durations={};alpha_max=0;sample_checks=0;apng_frames=0
    for gid in ready:
        entry=entries[gid];folder=HERE/'animations'/gid
        config=entry.get('rendering',{})
        if gid in batch:
            assets=local_motion.load(entry) if config['method']=='layered_animation' else Image.open(config['master']).convert('RGBA')
        for name in ('guide','guide_with_guides'):
            total=0;frame_count=0
            with Image.open(folder/(name+'.png')) as apng:
                assert apng.size==(405,720)
                for frame in ImageSequence.Iterator(apng):
                    rgba=frame.convert('RGBA');a=np.asarray(rgba)
                    alpha_max=max(alpha_max,int(a[:,:,3].max()));assert a[:,:,3].max()<=128,(gid,name)
                    # Check the first image and first/middle/end motion samples.
                    t=round(total*15)/15
                    windows=entry['windows'];w=config.get('motion_window',windows[0])
                    targets=[0,w['start'],(w['start']+w['end'])/2,w['end']]
                    if gid in batch and name=='guide' and any(abs(t-target)<.04 for target in targets):
                        raw=local_motion.frame_at(assets,entry,t,render.eased) if config['method']=='layered_animation' else stable_zoom.frame_at(assets,entry,t,render.eased)
                        if t>entry['duration']-entry['fade']:
                            fade=max(0,(entry['duration']-t)/entry['fade']);raw.putalpha(raw.getchannel('A').point(lambda v:round(v*fade)))
                        expected=np.asarray(render.alpha50(raw));visible=(expected[:,:,3]>0)|(a[:,:,3]>0)
                        assert np.array_equal(a[:,:,3],expected[:,:,3]),(gid,t,'alpha mismatch')
                        assert np.array_equal(a[:,:,:3][visible],expected[:,:,:3][visible]),(gid,t,'paint mismatch')
                        sample_checks+=1
                    total+=frame.info['duration']/1000;frame_count+=1
            assert abs(total-math.ceil(entry['duration']*15)/15)<.01,(gid,name,total)
            durations[gid]=total;apng_frames+=frame_count
    bar=entries['bar_low_truckr_mm'];cfg=bar['rendering']
    assert cfg['end_rect'][0]-cfg['start_rect'][0]==75
    assert cfg['start_rect'][1:]==cfg['end_rect'][1:]
    occlusion_checks=0
    for entry in entries.values():
        cfg=entry.get('rendering',{})
        if cfg.get('mode')!='reveal':continue
        images=local_motion.load(entry);fg=local_motion.transformed(images[-1],cfg['layers'][-1],0)
        composed=local_motion.frame_at(images,entry,entry['windows'][0]['start'],render.eased)
        a=np.asarray(fg);b=np.asarray(composed);opaque=a[:,:,3]>=128
        assert opaque.any(),entry['id']
        assert np.array_equal(a[opaque],b[opaque]),(entry['id'],'background shows through blocker')
        occlusion_checks+=1
    audit=json.loads((HERE/'local-motion-audit.json').read_text())
    assert {e['id'] for e in audit['guides']}==set(entries)
    report=dict(guides=ready,apng_files=len(ready)*2,decoded_frames=apng_frames,
                max_alpha=alpha_max,local_media_missing=len(missing),source_inputs_unchanged=len(hashes),
                deterministic_export_samples_checked=sample_checks,foreground_occlusion_checks=occlusion_checks,
                bar_camera_shift_right_px=75,bar_artwork_shift_left_px=75,
                duration_checks=len(durations),audited_guides=len(audit['guides']),
                physical_camera_calibration=False,device_validation=False)
    (HERE/'animation-asset-check.json').write_text(json.dumps(report,indent=2)+'\n')
    (HERE/'local-motion-check.json').write_text(json.dumps({k:v for k,v in report.items() if k!='guides'},indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='guides'}))


if __name__=='__main__':main()
