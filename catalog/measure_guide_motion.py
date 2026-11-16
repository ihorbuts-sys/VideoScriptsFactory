"""Measure visible change during the take, excluding entry holds, exits and fade.

These pixel measurements flag review candidates; they do not grade aesthetics or
measure physical camera motion. Schematic guidance graphics can change without
depicting the requested real subject action.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageSequence

HERE=Path(__file__).resolve().parent


def samples(path,times):
    images=[];clock=0;index=0
    with Image.open(path) as apng:
        last=None
        for frame in ImageSequence.Iterator(apng):
            rgba=frame.convert('RGBA');last=rgba
            end=clock+frame.info.get('duration',1000/15)/1000
            while index<len(times) and times[index]<end-1e-6:
                images.append(rgba.copy());index+=1
            clock=end
        while len(images)<len(times):images.append(last.copy())
    return images,clock


def main():
    manifest=json.loads((HERE.parent/'guides/watercolor_motion/manifest.json').read_text())
    ready=set(json.loads((HERE/'animations/index.json').read_text())['guides'])
    records=[]
    for entry in manifest['guides']:
        gid=entry['id']
        config=entry.get('rendering',{});window=config.get('motion_window',entry['windows'][0])
        start=window['start'];end=min(window['end'],entry['duration']-entry['fade']-.1)
        region='primary take action'
        follows=[s for s in entry['source_live_steps'] if s.get('kind')=='follow']
        if config.get('mode')=='whip' or (len(follows)==1 and follows[0].get('action')=='whip'):
            region='held take before the exit whip'
            start=1.3;end=window['start']-.1
            if gid=='person_host_eye_whip_mm':
                region='held take after the entry whip';start=window['end']+.1;end=entry['duration']-entry['fade']-.1
        times=[start+(end-start)*p for p in (0,.25,.5,.75,1)]
        source=HERE/'animations'/gid/'guide.png' if gid in ready else HERE.parent/'guides/overlays/schematic'/(gid+'.png')
        images,duration=samples(source,times)
        assert times[-1]<duration-.15,(gid,times[-1],duration)
        arrays=[]
        for image in images:
            background=Image.new('RGBA',image.size,'#23343e');background.alpha_composite(image)
            arrays.append(np.asarray(background.convert('RGB'),dtype=np.float32))
        deltas=[np.abs(a-arrays[0]) for a in arrays[1:]]
        mean=max(float(d.mean()) for d in deltas)
        fraction=max(float((d.max(axis=2)>3).mean()) for d in deltas)
        label='identical_take_samples' if mean==0 else ('low_visible_change_candidate' if mean<.8 and fraction<.05 else 'visible_change')
        records.append(dict(id=gid,style='watercolor' if gid in ready else 'schematic',region=region,sample_times=times,decoded_duration=duration,
                            max_mean_rgb_difference=round(mean,6),max_changed_pixel_fraction=round(fraction,6),
                            classification=label,method=config.get('method','multi_view_optical_flow') if gid in ready else 'original_schematic',mode=config.get('mode')))
    report=dict(date='2026-10-26',sampled_guides=len(records),samples_per_guide=5,
                excluded='Entry holds, exit whips and fade; six single-whip guides are measured during their held take. The two-whip salon sequence keeps its first detail-to-detail move.',
                metric='Raw APNG composited over charcoal; RGB difference from first take sample. No viewfinder UI.',
                limitation='Sparse samples can miss cyclic action. Pixel change is not proof of useful motion or aesthetic quality. Original schematic focus/guidance graphics can change without real subject action.',
                counts={label:sum(e['classification']==label for e in records) for label in sorted({e['classification'] for e in records})},
                by_style={style:{label:sum(e['style']==style and e['classification']==label for e in records) for label in sorted({e['classification'] for e in records})} for style in ['watercolor','schematic']},guides=records)
    folder=HERE/'checks/composition';folder.mkdir(exist_ok=True)
    (folder/'motion-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='guides'}))


if __name__=='__main__':main()
