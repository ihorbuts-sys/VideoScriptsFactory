"""Plan generated watercolor artwork and retain each guide's authored camera path."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GUIDES = HERE.parent
ROOT = GUIDES.parent
OUT = GUIDES/'watercolor'
sys.path.insert(0, str(HERE))
import catalog

STYLE = '''Use case: illustration-story.
Asset: watercolor artwork for an animated camera guide.
This is an animatable camera-guide subject, not a replacement script-preview illustration. Keep incidental
context sparse. Show the view through the camera; never show a device being used to film. A phone that is
the actual product being repaired may be shown as the subject.
Image 1 is the APPROVED ART STYLE reference: preserve its loose human pencil contours, natural proportions,
single pale slate-blue watercolor pigment, light washes with uneven brush marks spilling beyond outlines,
paper-like granulation and unfinished edges. Image 2 is the subject/composition reference only; do not copy
its flat vector shading, mouth, additional hands or any staff-only camera position.
The artwork must be genuinely AI-drawn, not CAD, generic geometric symbols, rigid vectors or traced edges.
Keep faces schematic. NO MOUTHS, lips, smiles, teeth or detailed eyes on any person. Maximum TWO visible
hands TOTAL in the entire scene, partial and background hands included. Hide other hands; use normal anatomy.
Use only one pale slate-blue hue with density variation. Do NOT darken the pigment or add other colors.
Opacity will be scaled programmatically by 0.5 after generation, so keep the original alpha and gentle pigment.
Transparent background with transparent paint fringes. No white paper rectangle, solid background, matte,
checkerboard, glow, text, letters, digits, logos, captions, watermarks, UI, arrows or viewfinder marks.
One scene, airy unpainted margin, recognizable subject large enough to read as a small thumbnail.
Camera viewpoint must be accessible to an ordinary visitor. Never place it behind staff counters, behind a
till, inside a kitchen or on a staff prep line. Staff may be the subject from the customer side. Do not assume
special permission. Do not show other customers' detailed faces.
'''


def main():
    OUT.mkdir(exist_ok=True)
    (OUT/'artwork').mkdir(exist_ok=True)
    (OUT/'originals').mkdir(exist_ok=True)
    groups = {}
    for row in catalog.catalog():
        key = '-'.join((row['family'], row['item'], row['angle']))
        groups.setdefault(key, []).append(row)
    assets = []
    guide_map = {}
    for key, rows in sorted(groups.items()):
        first = rows[0]
        family, item, angle = first['family'], first['item'], first['angle']
        wide = family in ('room', 'facade', 'rail', 'case', 'bar')
        orbit = any(row['move'].startswith('orbit') for row in rows)
        step = next(s for t in catalog.TEMPLATES['templates'] if t['id']==first['template']
                    for s in t['steps'] if s['id']==first['step'])
        prompt = STYLE+f'\nScene: {first["template"]}; subject {step["title"]}. '
        prompt += f'Action: {first["direction"]}. Intended camera angle: {angle}.\n'
        prompt += ('Create an expansive landscape panorama, approximately 2:1, with coherent perspective and enough '
                   'scene extending to both sides for a later camera pan. Keep all paint and context on transparency.\n'
                   if wide else 'Portrait 9:16 composition, complete subject with airy margin; no clipped heads or fingertips.\n')
        adaptation = ''
        if family=='oven':
            adaptation = 'Show a baker presenting the fresh bread tray across the CUSTOMER SIDE of the service counter, with no kitchen-side camera access. Keep the tray as the main subject.'
        elif family=='over_shoulder':
            adaptation = 'The shoulder is the VISITOR shoulder on the public side, never the staff shoulder in a restricted workspace. Show the staff activity facing the visitor across the service counter. For checkout show the CUSTOMER payment terminal or receipt, never the back of a cashier register.'
        elif family=='hands' and item in ('dough','griddle','wrap','hands','tool','work'):
            adaptation = 'Keep the camera above or beside the VISITOR side of a public service counter. The worker presents the item or finished work there. For cooking, show the freshly cooked item at pickup; do not put the viewer over a staff-only griddle or kitchen bench. The visitor never enters the workspace.'
        elif family=='cup' and item=='shot':
            adaptation = 'Show espresso served at the customer pickup counter; the camera must not be at a staff-side machine position.'
        if adaptation:
            prompt += '\nVisitor-access adaptation, overrides any conflicting reference/direction: '+adaptation+'\n'
        if family=='selfie':
            prompt += '\nFront-camera composition: one schematic mouthless creator at arm length, phone outside the frame. Avoid extra hands.\n'
        if family=='person' and item=='full':
            prompt += '\nShow a complete naturally proportioned person doing the exercise from a low visitor viewpoint, no more than two visible hands.\n'
        if orbit:
            prompt += ('\nOUTPUT FOR ONE ANIMATION: one horizontal 3:1 motion-keypose sheet on transparency, consisting of THREE '
                       'equal square cells across the width, no borders or drawn divisions. The SAME subject, identical scale, '
                       'lighting, drawing style and center in each cell. Camera azimuth 0 degrees in the left cell, 15 degrees '
                       'clockwise in the middle cell, 30 degrees clockwise in the right cell, always at the same stated elevation. '
                       'Change the actual perspective: show the far side coming around, not a 2D rotation of the drawing. '
                       'Keep subject features consistent. No hands in these three poses; no faces/mouths where the back of hair is '
                       'the subject. Each subject fits fully within its own cell, with generous transparent gutters. '
                       'No words or angle labels. This is one three-pose animation asset, not three different designs.\n')
        else:
            prompt += '\nOutput ONE illustration, no panels, alternatives or contact sheet.\n'
        reference = str((ROOT/'catalog/previews'/step['imageURL']).resolve())
        assets.append(dict(id=key, status='pending', family=family, item=item, angle=angle,
                           kind='orbit-sheet' if orbit else 'panorama' if wide else 'portrait',
                           reference=reference, prompt=prompt, adaptation=adaptation,
                           guide_ids=sorted({row['guide'] for row in rows})))
        for row in rows:
            guide_map[row['guide']] = dict(asset=key, **{k:row[k] for k in ('angle','start','end','move','transition')})
    approved = next(asset for asset in assets if asset['id']=='bag-handoff-low')
    approved.update(status='approved', original=str((ROOT/'catalog/style-study/waterbrush-ai-v3.png').resolve()),
                    artwork=str((ROOT/'catalog/style-study/waterbrush-ai-v3-opacity50.png').resolve()),
                    review='Approved by user; two hands, no mouth, public counter view, alpha scaled by 0.5.')
    manifest = dict(style_reference=str((ROOT/'catalog/style-study/waterbrush-ai-v3.png').resolve()),
                    alpha_factor=.5, assets=assets, guides=guide_map,
                    steps=304, guide_count=len(guide_map),
                    policy='Generate artwork using built-in image_gen only. Code may transform and animate generated pixels, scale alpha by 0.5 and tint caught state yellow. Never draw or trace substitute illustrations.')
    path = OUT/'manifest.json'
    if path.exists():
        previous = {asset['id']:asset for asset in json.loads(path.read_text())['assets']}
        manifest['assets'] = [previous.get(asset['id'], asset) for asset in assets]
    path.write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'{len(assets)} artwork groups for {len(guide_map)} guides; {sum(a["status"]=="pending" for a in manifest["assets"])} pending.')


if __name__=='__main__':
    main()
