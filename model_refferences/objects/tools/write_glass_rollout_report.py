"""Describe published assets and actual verification, without projected totals."""
import json
import re
from pathlib import Path

BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'catalog/glass-rollout'
CATALOG=Path('/Users/ihor.buts/Documents/Development/Scriptwriter/catalog/catalog.json')


def run():
    catalog=json.loads(CATALOG.read_text())
    manifest=json.loads((BASE/'catalog/clay-scenes/active-revisions.json').read_text())
    guides={gid:row for gid,row in manifest['guides'].items() if row.get('opacity_mode')=='image_view'}
    count=len(guides);total=len(catalog['guides'])
    rows=[]
    for gid,row in guides.items():
        spec=json.loads((BASE/row['folder']/'scene-spec.json').read_text())
        for ctx in row['contexts']:
            template=next(t for t in catalog['templates'] if t['id']==ctx['template'])
            step=next(s for s in template['steps'] if s['id']==ctx['step'])
            rows.append(f"|{template['title']}|{step['title']}|`{gid}`|{ctx['capture_seconds']:g}|{spec['duration_s']:.2f}|")
    live=json.loads((ROOT/'live-api-check.json').read_text())
    typed=json.loads((ROOT/'validation/typed-scenarios.json').read_text())
    new_ids={'room_lights_eye_hold','table_corner_pov_out_mw','room_eye_panr_ww_whipout','table_desk_pov_in_mc','table_outlets_high_tiltd_cc'}
    text=f'''# Approved glass guide rollout

**{count}/{total} unique guides across {len(rows)} step bindings are published in the approved glass style. {total-count} remain for this treatment.**

[Open the playable coffee batch](http://127.0.0.1:8766/glass-rollout/coffee/index.html).
Select **Animation** in the iOS camera. The image-view-opacity client changes from the first batch must be included in the app build.

## Current coffee continuation

{len(new_ids & guides.keys())}/5 additional guides are published: Lights on, Your corner, and the Work spot room, desk and Wi-Fi detail. The work route uses one physical scene and fixed lens, with a three-second room-to-desk handover and a two-second desk-to-card handover. Its step clips are seven, seven and five seconds; recommended capture times remain four, five and four seconds.

The work table has a supported laptop, cup, pastry and folded Wi-Fi card. The Wi-Fi symbol has a deliberate contrast mask so it remains recognizable through the smooth glass material. Morning ritual retains the same opened pastry halves in its final corner shot. Lights on is intentionally stationary: staff switches the practical lights on once, while window light and fixture positions stay fixed. The ghost emphasizes the lit diffusers in yellow, with no scene bloom.

[Play the complete Morning ritual sequence](http://127.0.0.1:8766/glass-rollout/sequences/cafe-morning-ritual/index.html): all four steps, 368 frames at 15 fps, 24.53 seconds including holds. Cup to pastry is continuous, with repeated handover frames removed. The other joins are explicit cuts. API: `/v1/scripts/cafe-morning-ritual/guide-sequence`.

One new reusable Tripo laptop cost **40 credits**. It has six rendered projections, a packed Blender file and an appendable asset in `model_refferences/objects/laptop/tripo-generated/review/`. The ledger's checked API balance is **645**, with no automatic paid retries. Other models and the canonical barista are reused.

## Published step bindings

|Template|Step|Guide|Capture seconds|Animation seconds|
|---|---|---|---|---|
'''+ '\n'.join(rows)+f'''

## Display and verification

- Hero surfaces are opaque at 100% image-view opacity. The default global image-view opacity is 65%, applied once. Supporting objects stay softer; legacy baked-opacity images use view opacity 1.
- Walls, floor and ceiling are absent from the ghost. Furniture, window/door frames and mounted props remain. The viewfinder and level are separate UI.
- Full-color video and glass share the same native camera. The preview reference video follows two seconds behind; live camera capture is not delayed.
- New moving shots stay in public space, with a fixed lens and measured camera speeds below 0.54 m/s. Table props have checked support and separate footprints, and all three main subjects fit the starting table view.
- Each published scene passed embedded-browser Play, Stop, phase replay, opacity, independent viewfinder, mobile layout and visible APNG-motion checks. The full Morning ritual sequence passed the same checks and lossless shot-boundary comparisons.
- Last live API check: {live['unique_glass_guides']} guides / {live['template_bindings']} bindings / {live['downloaded_assets']} downloaded, hash-checked assets. It also verifies the complete Morning ritual sequence and preservation of step preview art and unrelated overrides.
- Last typed Swift scenario check: {len(typed['guides'])} guides. The first batch's five focused client tests and iPhone SDK build passed; no additional SDK source changes were needed for this batch.

Physical recording and performance on an iPhone have not been exercised. Other full-script sequences retain their previous versions. The PDF has not been rebuilt for this continuation.

## Remaining work

Complete the canonical-character coffee performances: controlled milk pour, first sip, dose preparation, drink build and spoken selfie shots. Validate grips, cup/rim contact and facial poses before replacing the existing versions. The old Dial in description still needs a public-side adaptation together with its performance. Then continue by reusable venue/prop groups; the older local bar reconstruction needs the newer Tripo kit rather than a material-only conversion.

See [remaining coffee bindings](remaining-coffee.md), [full inventory](rollout.json), [live API evidence](live-api-check.json) and [typed scenarios](validation/typed-scenarios.json). The [first coffee batch report](first-coffee-batch-report.md) preserves its original nine-guide milestone.
'''
    path=ROOT/'report.md'
    history=ROOT/'first-coffee-batch-report.md'
    if not history.exists():history.write_text(path.read_text())
    path.write_text(text)
    for name in ['regeneration-report.md','blender-regeneration-report.md']:
        path=BASE/'catalog'/name;s=path.read_text()
        s=re.sub(r'(?:Nine|\d+) unique guides are(?: now)? published[^\n]*',f'{count} unique guides are published in the approved object-only glass style, plus the complete Morning ritual sequence. [Current report](glass-rollout/report.md) · [Playable batch](glass-rollout/coffee/index.html). Earlier counts below describe previous artwork generations.',s,count=1)
        path.write_text(s)
    print(json.dumps(dict(published_guides=count,bindings=len(rows),remaining=total-count)))


if __name__=='__main__':run()
