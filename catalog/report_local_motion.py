"""Refresh provenance and the exact guide lists after reviewed subset export."""
import collections
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE.parent/'guides/watercolor_motion'
LOCAL=OUT/'local-motion'


def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    ready=set(json.loads((HERE/'animations/index.json').read_text())['guides'])
    baseline=json.loads((LOCAL/'baseline/regeneration-report.json').read_text())
    baseline_ids={e['id'] for e in baseline['saved']}
    batch=set(json.loads((LOCAL/'guide-ids.json').read_text()))
    saved=[];pending=[]
    for entry in manifest['guides']:
        gid=entry['id'];path=Path(entry['original']) if entry.get('original') else None
        if not path or not path.exists():pending.append(gid);continue
        config=entry.get('rendering',{})
        origin=('Local painted-layer composition' if config.get('method')=='layered_animation' else 'Fixed painted master / local camera window') if gid in batch else 'Baseline generated artwork'
        saved.append(dict(id=gid,description=entry['description'],status=entry['status'],origin=origin,
                          baseline_62=gid in baseline_ids,rebuilt_this_batch=gid in batch,
                          artwork='../'+str(path.relative_to(HERE.parent)),
                          sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          rendering=config.get('method','multi_view_optical_flow'),mode=config.get('mode'),
                          sources=config.get('sources',[config.get('source_original',str(path))]),
                          review=entry['review'],limitation=config.get('limitation',''),
                          playable_preview=f'animations.html#{gid}' if gid in ready else None,
                          animation_export=f'animations/{gid}/guide_with_guides.png' if gid in ready else None))
    local=[e for e in saved if e['rendering'] in ('single_source_crop','layered_animation') and e['id'] in ready]
    summary=dict(date='2026-10-25',total=len(manifest['guides']),available=len(saved),
                 playable_previews=len(ready),local_motion_previews=len(local),
                 rebuilt_this_batch=len(batch),additional_playable_previews=len(ready)-baseline['keyframes_reviewed'],
                 needs_revision=sum(e['status']=='needs_revision' for e in saved),not_generated=len(pending),
                 baseline=dict(available=62,new_generated_atlases=61,reused_approved_study=1,playable_previews=50),
                 this_batch_source_artwork=dict(selected_resources=12,generated_outputs_including_one_color_edit=13),
                 local_modes=dict(collections.Counter(e['mode'] for e in local)),
                 saved=saved,pending=pending,baseline_62=sorted(baseline_ids))
    (HERE/'regeneration-report.json').write_text(json.dumps(summary,indent=2)+'\n')
    lines=['# Guide regeneration report','','Updated 2026-10-25. These assets illustrate live camera guides. Script preview photographs are unchanged.','',
           f'{len(ready)}/178 guides have playable watercolor previews. {len(local)} use fixed painted masters or rigid painted layers; four retain genuine changing-view keyframes. {len(batch)} guides were rebuilt in this batch, adding {len(ready)-50} playable previews.','',
           'The original 62 artwork sets (61 newly generated atlases and one reused cup study) remain identified in the table below. The original report and manifest are archived in [the baseline](../guides/watercolor_motion/local-motion/baseline/regeneration-report.md).','',
           'This batch used 12 selected AI-painted resources (13 generated outputs including a monochrome correction), plus individually checked existing artwork. New images are source paintings or cutouts, never independently generated animation frames. Prompts are saved in [local-motion/prompts](../guides/watercolor_motion/local-motion/prompts/). The built-in image generation tool was used.','',
           f'{len(saved)} guides now have source artwork; {summary["needs_revision"]} of those remain under revision. {len(pending)} still lack matching verified artwork. [All 178 audit results and limitations](local-motion-audit.md).','',
           '[Play animations](animations.html). The PDF contains static frame strips and playback links. Global alpha is multiplied by 0.5 once after composition. Viewfinder, thirds and horizon references remain fixed. Canonical overlays and sensor scenarios are unchanged.','',
           '## Exact artwork and playback list','','| Guide | Original 62 | This batch | Current method | Status |','|---|---|---|---|---|']
    for e in saved:
        link=f'[{e["id"]}]({e["playable_preview"]})' if e['playable_preview'] else f'[{e["id"]}]({e["artwork"]})'
        lines.append(f'| {link} | {"Yes" if e["baseline_62"] else "No"} | {"Rebuilt" if e["rebuilt_this_batch"] else "Retained"} | {e["mode"] or "changing viewpoints"} | {e["status"]} |')
    lines+=['','## Still under revision','']
    lines += [f'- `{e["id"]}`: {e["review"]}' for e in saved if e['status']=='needs_revision']
    lines+=['','## Matching artwork still needed','']+[f'- `{gid}`' for gid in pending]
    (HERE/'regeneration-report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('saved','pending','baseline_62')}))


if __name__=='__main__':main()
